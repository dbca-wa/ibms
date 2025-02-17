import json
import os
import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView, UpdateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormMixin, FormView
from sfm.models import FinancialYear
from xlrd import open_workbook
from xlutils.copy import copy

from ibms.forms import (
    ClearGLPivotForm,
    DownloadForm,
    IbmDataFilterForm,
    IbmDataForm,
    ManagerCodeUpdateForm,
    ReloadForm,
    UploadForm,
)
from ibms.models import GLPivDownload, IBMData, NCServicePriority, PVSServicePriority, SFMServicePriority
from ibms.reports import code_update_report, download_enhanced_report, download_report, reload_report
from ibms.utils import get_download_period, process_upload_file, validate_upload_file


class SiteHomeView(LoginRequiredMixin, TemplateView):
    """Static template view for the site homepage."""

    template_name = "site_home.html"

    def get_context_data(self, **kwargs):
        context = super(SiteHomeView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["superuser"] = True
        context["page_title"] = f"{settings.SITE_ACRONYM} | Home"
        context["title"] = "HOME"
        context["managers"] = settings.MANAGERS
        return context


class IbmsFormView(LoginRequiredMixin, FormView):
    """Base FormView class, to set common context variables."""

    template_name = "ibms/form.html"

    def get_context_data(self, **kwargs):
        context = super(IbmsFormView, self).get_context_data(**kwargs)
        context["download_period"] = get_download_period()
        if self.request.user.is_superuser:
            context["superuser"] = True
        return context


class ClearGLPivotView(IbmsFormView):
    """A basic function for admins to clear all GL Pivot entries for a financial year."""

    form_class = ClearGLPivotForm

    def get_context_data(self, **kwargs):
        context = super(ClearGLPivotView, self).get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_ACRONYM} | Clear GL Pivot entries"
        context["title"] = "CLEAR GL PIVOT ENTRIES"
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(self.request, "You are not authorised to carry out this operation")
            return redirect("site_home")
        return super(ClearGLPivotView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("site_home")

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.error(self.request, "You are not authorised to carry out this operation.")
            return redirect("site_home")
        if self.request.POST.get("cancel"):
            return redirect("site_home")
        # Do the bulk delete. We can use the private method _raw_delete because we don't
        # have any signals or cascade deletes to worry about.
        fy = form.cleaned_data["financial_year"]
        glpiv = GLPivDownload.objects.filter(fy=fy)
        if glpiv.exists():
            glpiv._raw_delete(glpiv.db)
            messages.success(self.request, f"GL Pivot entries for {fy} have been cleared.")
        return super(ClearGLPivotView, self).form_valid(form)


class UploadView(IbmsFormView):
    """Upload view for superusers only."""

    form_class = UploadForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("site_home")
        return super(UploadView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_ACRONYM} | Upload"
        context["title"] = "UPLOAD"
        return context

    def get_success_url(self):
        return reverse("upload")

    def form_valid(self, form):
        # Uploaded CSVs may contain characters with oddball encodings.
        # To overcome this, we need to decode the uploaded file content as UTF-8 (ignoring errors),
        # re-encode the file, and then process that. Wasteful, but necessary to parse the CSV
        # in a consistent fashion.
        t = tempfile.NamedTemporaryFile()
        for chunk in form.cleaned_data["upload_file"].chunks():
            t.write(chunk.decode("utf-8", "ignore").encode())
        t.flush()
        # We have to open the uploaded file in text mode to parse it.
        file = open(t.name, "r")
        file_type = form.cleaned_data["upload_file_type"]

        # Catch exception thrown by the upload validation process and display it to the user.
        try:
            upload_valid = validate_upload_file(file, file_type)
        except Exception as e:
            messages.warning(self.request, f"Error: {str(e)}")
            return redirect("upload")

        # Upload may still not be valid, but at least no exception was thrown.
        if upload_valid:
            fy = form.cleaned_data["financial_year"]
            try:
                process_upload_file(file.name, file_type, fy)
                messages.success(self.request, f"{file_type} data imported successfully")
                return redirect("upload")
            except Exception as e:
                messages.warning(self.request, f"Error: {str(e)}")
                return redirect("upload")
        else:
            messages.warning(
                self.request,
                f"This file appears to be of an incorrect type. Please choose a {file_type} file.",
            )
            return redirect("upload")


class DownloadView(IbmsFormView):
    template_name = "ibms/download.html"
    form_class = DownloadForm

    def get_form_kwargs(self):
        kwargs = super(DownloadView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_ACRONYM} | Download"
        context["title"] = "DOWNLOAD"
        return context

    def get_success_url(self):
        return reverse("download")

    def form_valid(self, form):
        d = form.cleaned_data
        glpiv_qs = GLPivDownload.objects.filter(fy=d["financial_year"])
        print(glpiv_qs)
        if d.get("cost_centre", None):
            glpiv_qs = glpiv_qs.filter(costCentre=d["cost_centre"])
        elif d.get("region", None):
            glpiv_qs = glpiv_qs.filter(regionBranch=d["region"])
        elif d.get("division", None):
            glpiv_qs = glpiv_qs.filter(division=d["division"])

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=ibms_data_download.csv"
        response = download_report(glpiv_qs, response)  # Write CSV data.
        return response


class DownloadEnhancedView(DownloadView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_ACRONYM} | Enhanced Download"
        context["title"] = "ENHANCED DOWNLOAD"
        return context

    def get_success_url(self):
        return reverse("download_enhanced")

    def form_valid(self, form):
        d = form.cleaned_data
        glpiv_qs = GLPivDownload.objects.filter(fy=d["financial_year"])
        if d.get("cost_centre", None):
            glpiv_qs = glpiv_qs.filter(costCentre=d["cost_centre"])
        elif d.get("region", None):
            glpiv_qs = glpiv_qs.filter(regionBranch=d["region"])
        elif d.get("division", None):
            glpiv_qs = glpiv_qs.filter(division=d["division"])

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=ibms_data_enhanced_download.csv"
        response = download_enhanced_report(glpiv_qs, response)  # Write CSV data.
        return response


class ReloadView(IbmsFormView):
    template_name = "ibms/reload.html"
    form_class = ReloadForm

    def get_context_data(self, **kwargs):
        context = super(ReloadView, self).get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_ACRONYM} | Reload"
        context["title"] = "RELOAD"
        return context

    def get_success_url(self):
        return reverse("reload")

    def form_valid(self, form):
        fy = form.cleaned_data["financial_year"]
        ibm = IBMData.objects.filter(fy=fy, costCentre=form.cleaned_data["cost_centre"])
        ibm = ibm.exclude(service=11, job="777", activity="DJ0")
        gl = GLPivDownload.objects.filter(fy=fy, costCentre=form.cleaned_data["cost_centre"])
        gl = gl.exclude(shortCode="").distinct().order_by("gLCode", "shortCode", "shortCodeName")
        # Service priority checkboxes
        nc_sp = NCServicePriority.objects.filter(fy=fy, categoryID__in=form.cleaned_data["ncChoice"])
        pvs_sp = PVSServicePriority.objects.filter(fy=fy, categoryID__in=form.cleaned_data["pvsChoice"])
        fm_sp = SFMServicePriority.objects.filter(fy=fy, categoryID__in=form.cleaned_data["fmChoice"])

        fpath = os.path.join(settings.STATIC_ROOT, "excel", "reload_base.xls")
        excel_template = open_workbook(fpath, formatting_info=True, on_demand=True)
        workbook = copy(excel_template)

        # Style & populate the worksheet.
        reload_report(workbook, ibm, nc_sp, pvs_sp, fm_sp, gl)
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "attachment; filename=ibms_reloads.xls"
        workbook.save(response)  # Save the worksheet contents to the response.

        return response


class CodeUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "ibms/code_update.html"

    def get_context_data(self, **kwargs):
        context = super(CodeUpdateView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["superuser"] = True
        context["download_period"] = get_download_period()
        context["page_title"] = f"{settings.SITE_ACRONYM} | Code update"
        context["title"] = "CODE UPDATE"
        return context


class CodeUpdateAdminView(IbmsFormView):
    template_name = "ibms/code_update_admin.html"
    form_class = ManagerCodeUpdateForm

    def get_context_data(self, **kwargs):
        context = super(CodeUpdateAdminView, self).get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_ACRONYM} | Code update"
        context["title"] = "CODE UPDATE (ADMIN)"
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(self.request, "You are not authorised to carry out this operation")
            return redirect("site_home")
        return super(CodeUpdateAdminView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("code_update")

    def form_valid(self, form):
        fy = form.cleaned_data["financial_year"]
        ibm = IBMData.objects.filter(fy=fy)
        gl = GLPivDownload.objects.filter(fy=fy)

        # CC limits both the querysets.
        cc = self.request.POST.get("cost_centre")
        if cc:
            gl = gl.filter(costCentre=cc)
            ibm = ibm.filter(costCentre=cc)

        # Filter GLPivot to resource < 4000
        gl = gl.filter(resource__lt=4000)

        # Exclude service 11 from GLPivDownload queryset.
        gl = gl.exclude(service=11)

        # Superuser must specify DJ0 or non-DJ0 activities only.
        # Business rule: for normal users, include any line items that are
        # activity 'DJ0', EXCEPT where service is 42, 43 or 75.
        # For superusers, do the opposite (include activity DJ0 items ONLY if
        # service is 42, 43 or 75).
        if self.request.user.is_superuser and "report_type" in form.cleaned_data:
            if form.cleaned_data["report_type"] == "dj0":
                gl = gl.filter(activity="DJ0")
                gl = gl.filter(service__in=[42, 43, 75])
                gl = gl.filter(account__in=[1, 2, 4, 42])
            else:  # Non-DJ0.
                gl = gl.exclude(activity="DJ0")
                gl = gl.filter(account__in=[1, 2, 42])
        else:
            # Business rule: for CC 531 only, include accounts 1, 2, 6 & 42.
            if cc and cc == "531":
                gl = gl.filter(account__in=[1, 2, 6, 42])
            else:
                gl = gl.filter(account__in=[1, 2, 42])
            gl = gl.exclude(activity="DJ0", service__in=[42, 43, 75])

        # Filter by codeID: EXCLUDE objects with a codeID that matches any
        # IBMData object's ibmIdentifier for the same FY.
        code_ids = set(ibm.values_list("ibmIdentifier", flat=True))
        gl = gl.exclude(codeID__in=code_ids).order_by("codeID")
        gl_codeids = sorted(set(gl.values_list("codeID", flat=True)))

        # Service priority checkboxes.
        nc_sp = NCServicePriority.objects.filter(fy=fy, categoryID__in=form.cleaned_data["ncChoice"]).order_by(
            "servicePriorityNo"
        )
        pvs_sp = PVSServicePriority.objects.filter(fy=fy, categoryID__in=form.cleaned_data["pvsChoice"]).order_by(
            "servicePriorityNo"
        )
        fm_sp = SFMServicePriority.objects.filter(fy=fy, categoryID__in=form.cleaned_data["fmChoice"]).order_by(
            "servicePriorityNo"
        )

        # Style & populate the workbook.
        fpath = os.path.join(settings.STATIC_ROOT, "excel", "ibms_codeupdate_base.xls")
        excel_template = open_workbook(fpath, formatting_info=True, on_demand=True)
        workbook = copy(excel_template)
        code_update_report(excel_template, workbook, gl, gl_codeids, nc_sp, pvs_sp, fm_sp, ibm)

        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "attachment; filename=ibms_exceptions.xls"
        workbook.save(response)  # Save the Excel workbook contents to the response.
        return response


class JSONResponseMixin(object):
    """View mixin to return a JSON response to requests."""

    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content, content_type="application/json", **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json.dumps(context)


class ServicePriorityMappingsJSON(JSONResponseMixin, BaseDetailView):
    """View to return a filtered list of mappings.
    Cannot use below as we require multiple fields without PKs
    """

    model = None
    fieldname = None
    return_pk = False

    def get(self, request, *args, **kwargs):
        try:
            for fieldname in self.fieldname.split(", "):
                self.model._meta.get_field(fieldname)
        except ValueError:
            return HttpResponseBadRequest(f"Invalid field name: {self.fieldname}")
        r = self.model.objects.all()
        if request.GET.get("financialYear", None):
            r = r.filter(fy=request.GET["financialYear"])
        if request.GET.get("costCentreNo", None):
            r = r.filter(costCentreNo=request.GET["costCentreNo"])
        choices = []
        r = r.distinct()
        try:
            res = r.get()
        except self.model.DoesNotExist:
            return HttpResponse("Query returns empty.")
        for fieldname in self.fieldname.split(", "):
            choice_val = getattr(res, fieldname)
            choices.append(choice_val)
        context = {"choices": choices}
        return self.render_to_response(context)


class IbmsModelFieldJSON(JSONResponseMixin, BaseDetailView):
    """View to return a filtered list of distinct values from a
    defined field for a defined model type, suitable for inserting
    into a select list.
    Used to update select lists via AJAX.
    """

    model = None
    fieldname = None
    return_pk = False

    def get(self, request, *args, **kwargs):
        # Sanity check: if the model hasn't got that field, return a
        # HTTPResponseBadRequest response.
        if not hasattr(self.model, self.fieldname):
            return HttpResponseBadRequest(f"Invalid field name: {self.fieldname}")
        qs = self.model.objects.all()
        if request.GET.get("financialYear", None):
            qs = qs.filter(fy__financialYear=request.GET["financialYear"])
        if request.GET.get("costCentre", None):
            qs = qs.filter(costCentre=request.GET["costCentre"])
        if request.GET.get("service", None):
            qs = qs.filter(costCentre=request.GET["service"])

        if request.GET.get("regionBranch", None):
            if self.model == IBMData and request.GET.get("financialYear", None):
                # As regionBranch is a field on GLPivDownload, we obtain the set of CC values for the given FY,
                # then use those values to filter the IBMData queryset.
                fy = FinancialYear.objects.get(financialYear=request.GET["financialYear"])
                cost_centres = set(
                    GLPivDownload.objects.filter(fy=fy, regionBranch=self.request.GET["regionBranch"]).values_list(
                        "costCentre", flat=True
                    )
                )
                qs = qs.filter(costCentre__in=cost_centres)
            else:
                qs = qs.filter(regionBranch=request.GET["regionBranch"])

        # If we're not after PKs, then we need to reduce the qs to distinct values.
        if not self.return_pk:
            qs = qs.distinct(self.fieldname)
        choices = []
        for obj in qs:
            if self.fieldname == "__str__":
                choice_val = str(obj)
            else:
                choice_val = getattr(obj, self.fieldname)
            if choice_val:
                if self.return_pk:
                    choices.append([obj.pk, choice_val])
                else:
                    choices.append([choice_val, choice_val])
        context = {"choices": choices}
        return self.render_to_response(context)


class IbmDataList(LoginRequiredMixin, FormMixin, ListView):
    model = IBMData
    http_method_names = ["get", "head", "options", "trace"]
    form_class = IbmDataFilterForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        for key in ["financial_year", "cost_centre", "region", "service", "budget_area", "project_sponsor"]:
            if self.request.GET.get(key, None):
                kwargs["initial"][key] = self.request.GET[key]
        # Always provide a default FY.
        if "financial_year" not in self.request.GET:
            fy = FinancialYear.objects.order_by("-financialYear").first()
            kwargs["initial"]["financial_year"] = fy.financialYear

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["superuser"] = True
        context["javascript_context"] = {
            "ajax_ibmdata_budgetarea_url": reverse("ajax_ibmdata_budgetarea"),
            "ajax_ibmdata_projectsponsor_url": reverse("ajax_ibmdata_projectsponsor"),
            "ajax_ibmdata_service_url": reverse("ajax_ibmdata_service"),
            "ajax_ibmdata_project_url": reverse("ajax_ibmdata_project"),
            "ajax_ibmdata_job_url": reverse("ajax_ibmdata_job"),
        }
        context["download_period"] = get_download_period()
        context["page_title"] = f"{settings.SITE_ACRONYM} | IBM data amendment"
        context["title"] = "IBM DATA AMENDMENT"
        context["object_count"] = self.get_queryset().count()
        return context

    def get_queryset(self):
        qs = super().get_queryset()

        # Always filter by the newest financial year.
        fy = FinancialYear.objects.order_by("-financialYear").first()
        qs = qs.filter(fy=fy)

        # If we don't have either CC or region/branch filters, return an empty queryset.
        if not (self.request.GET.get("cost_centre", None) or self.request.GET.get("region", None)):
            return qs.none()

        # Cost centre
        if self.request.GET.get("cost_centre", None):
            qs = qs.filter(costCentre=self.request.GET["cost_centre"])

        # Region/branch
        if self.request.GET.get("region", None):
            # As regionBranch is a field on GLPivDownload, we obtain the set of CC values for the given FY,
            # then use those values to filter the IBMData queryset.
            region_branch = self.request.GET["region"]
            cost_centres = set(
                GLPivDownload.objects.filter(fy=fy, regionBranch=region_branch).values_list("costCentre", flat=True)
            )
            qs = qs.filter(costCentre__in=cost_centres)

        # Service
        if self.request.GET.get("service", None):
            qs = qs.filter(service=self.request.GET["service"])

        # Project
        if self.request.GET.get("project", None):
            qs = qs.filter(service=self.request.GET["project"])

        # Job
        if self.request.GET.get("job", None):
            qs = qs.filter(service=self.request.GET["job"])

        # Budget area
        if self.request.GET.get("budget_area", None):
            qs = qs.filter(budgetArea=self.request.GET["budget_area"])

        # Project sponsor
        if self.request.GET.get("project_sponsor", None):
            qs = qs.filter(projectSponsor=self.request.GET["project_sponsor"])

        return qs.order_by("ibmIdentifier")


class IbmDataUpdate(UpdateView):
    model = IBMData
    form_class = IbmDataForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        if self.request.user.is_superuser:
            context["superuser"] = True
        context["page_title"] = f"{settings.SITE_ACRONYM} | Edit IBM data {obj.ibmIdentifier}"
        context["title"] = f"EDIT IBM DATA {obj.ibmIdentifier}"
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("cancel", None):
            return redirect(reverse("ibmdata_list"))
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("ibmdata_list")

    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f"IBM Data {obj.ibmIdentifier} ({obj.fy}) updated successfully")
        return super().form_valid(form)
