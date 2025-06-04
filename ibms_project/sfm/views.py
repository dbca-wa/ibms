import json
import os
import tempfile
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormView
from openpyxl import load_workbook
from sfm.forms import FMOutputReportForm, OutputEntryForm, OutputUploadForm
from sfm.models import MeasurementType, MeasurementValue, Quarter, SFMMetric
from sfm.report import outputs_report
from sfm.utils import process_upload_file, validate_file

from ibms.utils import get_download_period
from ibms.views import JSONResponseMixin


class OutputEntry(LoginRequiredMixin, FormView):
    template_name = "sfm/output_entry.html"
    form_class = OutputEntryForm
    http_method_names = ["get", "post", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = " | ".join([settings.SITE_ACRONYM, "Output Entry"])
        context["download_period"] = get_download_period()
        context["title"] = "Output Entry"
        if self.request.user.is_superuser:
            context["superuser"] = True
        # Context variable to allow mapping of MeasurementType fields.
        mt = [(i.pk, i.unit.lower()) for i in MeasurementType.objects.all()]
        context["measurement_types"] = json.dumps(mt)
        return context

    def get_success_url(self):
        return reverse("sfm:outcome-entry")

    def form_valid(self, form):
        d = form.cleaned_data
        # Iterate through each of the input value fields.
        for val in ["quantity", "percentage", "hectare", "kilometer"]:
            mt = MeasurementType.objects.get(unit__iexact=val)
            mv, created = MeasurementValue.objects.get_or_create(
                quarter=d["quarter"], sfmMetric=d["sfm_metric_id"], measurementType=mt, costCentre=d["cost_centre"]
            )
            mv.value = d[val]
            if d["comment"]:
                mv.comment = d["comment"]
            mv.save()

        messages.success(self.request, "Output values updated successfully.")
        return super().form_valid(form)


class OutputUpload(LoginRequiredMixin, FormView):
    template_name = "ibms/form.html"
    form_class = OutputUploadForm
    http_method_names = ["get", "post", "head", "options"]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect(reverse("sfm:output-upload"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = " | ".join([settings.SITE_ACRONYM, "Output Upload"])
        context["download_period"] = get_download_period()
        context["title"] = "Output Upload"
        context["output-upload_page"] = True
        if self.request.user.is_superuser:
            context["superuser"] = True
        return context

    def get_success_url(self):
        return reverse("sfm:output-upload")

    def form_valid(self, form):
        # Uploaded CSVs may contain characters with oddball encodings.
        # To overcome this, we need to decode the uploaded file content as UTF-8 (ignoring errors),
        # re-encode the file, and then process that. Wasteful, but necessary to parse the CSV
        # in a consistent fashion.
        t = tempfile.NamedTemporaryFile()
        for chunk in form.cleaned_data["upload_file"].chunks():
            t.write(chunk.decode("utf-8", "ignore").encode())
        t.flush()
        # NOTE: we have to open the uploaded file in non-binary mode to parse it.
        file = open(t.name, "r")
        file_type = form.cleaned_data["upload_file_type"]
        if validate_file(file, file_type):
            fy = form.cleaned_data["financial_year"]
            process_upload_file(file.name, file_type, fy)
            messages.success(self.request, "Output upload values updated successfully.")
        else:
            messages.error(self.request, f"This file appears to be of an incorrect type. Please choose a {file_type} file.")
        return super().form_valid(form)


class OutputReport(LoginRequiredMixin, FormView):
    template_name = "sfm/output_report.html"
    form_class = FMOutputReportForm
    http_method_names = ["get", "post", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = " | ".join([settings.SITE_ACRONYM, "Output Report"])
        context["download_period"] = get_download_period()
        context["title"] = "Output Report"
        if self.request.user.is_superuser:
            context["superuser"] = True
        return context

    def form_valid(self, form):
        d = form.cleaned_data
        fy = d["financial_year"]
        qtr = d["quarter"]
        cc = d["cost_centre"]
        sfm = SFMMetric.objects.filter(fy=fy).order_by("servicePriorityNo", "metricID")
        # Ordered list of service priority numbers.
        spn = sorted(set(sfm.values_list("servicePriorityNo", flat=True)))
        # Current download period.
        dp = datetime.strftime(get_download_period(), "%d/%m/%Y")
        fpath = os.path.join(settings.STATIC_ROOT, "excel", "fm_outputs.xlsx")
        book = load_workbook(fpath)

        # Style & populate the worksheet.
        outputs_report(book, sfm, spn, dp, fy, qtr, cc)
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=fm_outputs.xlsx"
        book.save(response)  # Save the worksheet contents to the response.
        return response


class MeasurementValueJSON(JSONResponseMixin, BaseDetailView):
    """Utility view to return MeasurementValue object values as JSON,
    based upon the passed-in filter values.
    """

    http_method_names = ["get", "post", "head", "options"]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        metric = None
        measure = None

        if "quarter" in request.GET and "region" in request.GET and "sfmMetric" in request.GET:
            quarter = Quarter.objects.get(pk=request.GET["quarter"])
            metric = SFMMetric.objects.get(pk=request.GET["sfmMetric"])

            if MeasurementValue.objects.filter(quarter=quarter, region=request.GET["region"], sfmMetric=metric).exists():
                # Find the measure
                measures = MeasurementValue.objects.filter(quarter=quarter, region=request.GET["region"], sfmMetric=metric)
                if measures.filter(value__isnull=False).exists():
                    measure = measures.filter(value__isnull=False).first()
                else:  # Just use the first object in the queryset.
                    measure = measures.first()

        if metric and measure:
            context = {"sfmMetric": model_to_dict(metric), "measurementValue": model_to_dict(measure)}
        else:
            context = {"sfmMetric": {}, "measurementValue": {}}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        if "quarter" in request.POST and "region" in request.POST and "sfmMetric" in request.POST:
            quarter = Quarter.objects.get(pk=request.POST["quarter"])
            metric = SFMMetric.objects.get(pk=request.POST["sfmMetric"])
            measure, created = MeasurementValue.objects.get_or_create(quarter=quarter, region=request.POST["region"], sfmMetric=metric)
            if "planned" in request.POST:
                measure.planned = request.POST["planned"] == "true"
            if "status" in request.POST:
                measure.status = request.POST["status"]
            if "comment" in request.POST:
                measure.comment = request.POST["comment"]
            measure.save()

            return self.render_to_response({"success": True, "created": created})
        else:
            return {}
