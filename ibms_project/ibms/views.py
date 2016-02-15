from __future__ import print_function, unicode_literals, absolute_import
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormView
import json
import os
import tempfile
from xlrd import open_workbook
from xlutils.copy import copy

from ibms import forms
from ibms.file_funcs import validate_file, process_upload_file
from ibms.models import (
    IBMData, GLPivDownload, NCServicePriority, PVSServicePriority,
    SFMServicePriority)
from ibms.report import (
    reload_report, code_update_report, data_amend_report,
    service_priority_report, download_report)
from ibms.utils import get_download_period, breadcrumb_trail

T = 'IBMS'


class SiteHomeView(TemplateView):
    """Static template view for the site homepage.
    """
    template_name = 'site_home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SiteHomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SiteHomeView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['superuser'] = True
        context['page_title'] = T
        context['title'] = 'HOME'
        links = [(None, 'Home')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        context['managers'] = settings.MANAGERS
        return context


class IbmsFormView(FormView):
    """Base FormView class, to set common context variables.
    """
    template_name = 'ibms/form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IbmsFormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IbmsFormView, self).get_context_data(**kwargs)
        context['download_period'] = get_download_period()
        if self.request.user.is_superuser:
            context['superuser'] = True
        return context


class UploadView(IbmsFormView):
    """Upload view for superusers only.
    """
    form_class = forms.UploadForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('site_home')
        return super(UploadView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'Upload'])
        context['title'] = 'UPLOAD'
        links = [
            (reverse('site_home'), 'Home'),
            (None, 'Upload')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        return context

    def get_success_url(self):
        return reverse('upload')

    def form_valid(self, form):
        file_type = form.cleaned_data['upload_file_type']
        fy = form.cleaned_data['financial_year']
        if validate_file(form.cleaned_data['upload_file'], file_type):
            t = tempfile.NamedTemporaryFile()
            for chunk in form.cleaned_data['upload_file'].chunks():
                t.write(chunk)
            t.flush()
            process_upload_file(t.name, file_type, fy)
            messages.success(self.request, 'Data imported successfully.')
            t.close()
            return redirect('upload')
        else:
            messages.error(
                self.request, '''This file appears to be of an incorrect type.
                Please choose a {0} file.'''.format(file_type))
            return redirect('upload')
        return super(UploadView, self).form_valid(form)


class DownloadView(IbmsFormView):
    template_name = 'ibms/download.html'
    form_class = forms.DownloadForm

    def get_form_kwargs(self):
        kwargs = super(DownloadView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'Download'])
        context['title'] = 'DOWNLOAD'
        links = [
            (reverse('site_home'), 'Home'),
            (None, 'Download')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        return context

    def get_success_url(self):
        return reverse('download')

    def form_valid(self, form):
        d = form.cleaned_data
        glrows = GLPivDownload.objects.filter(
            financialYear=d['financial_year'])
        if d.get('cost_centre', None):
            glrows = glrows.filter(costCentre=d['cost_centre'])
        elif d.get('region', None):
            glrows = glrows.filter(regionBranch=d['region'])
        elif d.get('division', None):
            glrows = glrows.filter(division=d['division'])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=ibms_data_download.csv'
        response = download_report(glrows, response)  # Write CSV data.
        return response


class ReloadView(IbmsFormView):
    template_name = 'ibms/reload.html'
    form_class = forms.ReloadForm

    def get_form_kwargs(self):
        kwargs = super(ReloadView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ReloadView, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'Reload'])
        context['title'] = 'RELOAD'
        links = [
            (reverse('site_home'), 'Home'),
            (None, 'Reload')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        context['reload_template_url'] = settings.IBM_RELOAD_URI
        return context

    def get_success_url(self):
        return reverse('reload')

    def form_valid(self, form):
        fy = form.cleaned_data['financial_year']
        ibm = IBMData.objects.filter(
            financialYear=fy, costCentre=form.cleaned_data['cost_centre'])
        ibm = ibm.exclude(service=11, job='777', activity='DJ0')
        gl = GLPivDownload.objects.filter(
            financialYear=fy, costCentre=form.cleaned_data['cost_centre'])
        gl = gl.exclude(shortCode='').distinct().order_by(
            'gLCode', 'shortCode', 'shortCodeName')
        # Service priority checkboxes
        nc_sp = NCServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['ncChoice'])
        pvs_sp = PVSServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['pvsChoice'])
        fm_sp = SFMServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['fmChoice'])

        fpath = os.path.join(settings.STATIC_ROOT, 'excel', 'reload_base.xls')
        excel_template = open_workbook(
            fpath, formatting_info=True, on_demand=True)
        book = copy(excel_template)

        # Style & populate the worksheet.
        reload_report(book, ibm, nc_sp, pvs_sp, fm_sp, gl)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=ibms_reloads.xls'
        book.save(response)  # Save the worksheet contents to the response.

        return response


class CodeUpdateView(IbmsFormView):
    template_name = 'ibms/code_update.html'
    form_alternative = None

    def get_form_class(self):
        if self.request.user.is_superuser:
            return forms.ManagerCodeUpdateForm
        else:
            return forms.CodeUpdateForm

    def get_form_kwargs(self):
        kwargs = super(CodeUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CodeUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'Code update'])
        context['title'] = 'CODE UPDATE'
        links = [
            (reverse('site_home'), 'Home'),
            (None, 'Code update')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        context['code_update_template_url'] = settings.IBM_CODE_UPDATER_URI
        return context

    def get_success_url(self):
        return reverse('code_update')

    def form_valid(self, form):
        cc = self.request.POST.get('cost_centre')  # May be None.
        fy = form.cleaned_data['financial_year']
        gl = GLPivDownload.objects.filter(
            financialYear=fy, account__in=[1, 2], resource__lt=4000)
        # Exclude service 11 from GLPivDownload query:
        gl = gl.exclude(service=11)
        ibm = IBMData.objects.filter(financialYear=fy)
        # costCentre filter is optional.
        if cc:
            gl = gl.filter(costCentre=cc)
            ibm = ibm.filter(costCentre=cc)
        # If the form post contains cost_centre, assume that a non-superuser
        # has run the report and return non-DJ0 activities only.
        # Superuser may also specify non-DJ0 activities only.
        if cc or form.cleaned_data['report_type'] == '0':
            gl = gl.exclude(activity='DJ0')  # Non-DJ0 only
        else:
            gl = gl.filter(activity='DJ0')  # DJ0 only
        # Filter by codeID: EXCLUDE objects with a codeID that matches any
        # IBMData object's ibmIdentifier for the same FY.
        code_ids = set(ibm.values_list('ibmIdentifier', flat=True))
        gl = gl.exclude(codeID__in=code_ids).order_by('codeID')
        gl_codeids = sorted(set(gl.values_list('codeID', flat=True)))

        # Service priority checkboxes.
        nc_sp = NCServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['ncChoice']).order_by('servicePriorityNo')
        pvs_sp = PVSServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['pvsChoice']).order_by('servicePriorityNo')
        fm_sp = SFMServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['fmChoice']).order_by('servicePriorityNo')

        # Style & populate the workbook.
        fpath = os.path.join(
            settings.STATIC_ROOT, 'excel', 'ibms_codeupdate_base.xls')
        excel_template = open_workbook(
            fpath, formatting_info=True, on_demand=True)
        book = copy(excel_template)
        code_update_report(excel_template, book, gl, gl_codeids, nc_sp, pvs_sp, fm_sp)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=ibms_exceptions.xls'
        book.save(response)  # Save the worksheet contents to the response.
        return response


class DataAmendmentView(IbmsFormView):
    form_class = forms.DataAmendmentForm
    form_alternative = None
    template_name = 'ibms/data_amendment.html'

    def get_form_kwargs(self):
        kwargs = super(DataAmendmentView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DataAmendmentView, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'Data amendment'])
        context['title'] = 'DATA AMENDMENT'
        links = [
            (reverse('site_home'), 'Home'),
            (None, 'Data amendment')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        context['data_amend_template_url'] = settings.IBM_DATA_AMEND_URI
        return context

    def get_success_url(self):
        return reverse('dataamendment')

    def form_valid(self, form):
        fy = form.cleaned_data['financial_year']
        gl = GLPivDownload.objects.filter(financialYear=fy, account__in=[1, 2], resource__lt=4000)
        gl = gl.exclude(activity='DJ0', job='777', service='11')
        gl = gl.order_by('codeID')
        if form.cleaned_data['cost_centre']:
            gl = gl.filter(costCentre=form.cleaned_data['cost_centre'])
        if form.cleaned_data['region']:
            gl = gl.filter(regionBranch=form.cleaned_data['region'])
        if form.cleaned_data['service']:
            gl = gl.filter(service=form.cleaned_data['service'])

        ibm = IBMData.objects.filter(financialYear=fy)
        if form.cleaned_data['budget_area']:
            ibm = ibm.filter(budgetArea=form.cleaned_data['budget_area'])
        if form.cleaned_data['project_sponsor']:
            ibm = ibm.filter(projectSponsor=form.cleaned_data['project_sponsor'])

        # Service priority checkboxes.
        nc_sp = NCServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['ncChoice']).order_by('servicePriorityNo')
        pvs_sp = PVSServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['pvsChoice']).order_by('servicePriorityNo')
        fm_sp = SFMServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['fmChoice']).order_by('servicePriorityNo')

        fpath = os.path.join(
            settings.STATIC_ROOT, 'excel', 'ibms_dataamend_base.xls')
        excel_template = open_workbook(
            fpath, formatting_info=True, on_demand=True)
        book = copy(excel_template)

        # Style & populate the worksheet.
        data_amend_report(book, gl, ibm, nc_sp, pvs_sp, fm_sp)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=ibms_dataamendment.xls'
        book.save(response)  # Save the worksheet contents to the response.
        return response


class ServicePriorityDataView(IbmsFormView):
    template_name = 'ibms/service_priority_data.html'
    form_class = forms.ServicePriorityDataForm

    def get_context_data(self, **kwargs):
        context = super(
            ServicePriorityDataView,
            self).get_context_data(
            **kwargs)
        context['page_title'] = ' | '.join([T, 'Service Priority data'])
        context['title'] = 'SERVICE PRIORITY DATA'
        links = [
            (reverse('site_home'), 'Home'),
            (None, 'Service priority data')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        context['service_priority_template_url'] = settings.IBM_SERVICE_PRIORITY_URI
        return context

    def get_form_kwargs(self):
        kwargs = super(ServicePriorityDataView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_success_url(self):
        return reverse('serviceprioritydata')

    def form_valid(self, form):
        fy = form.cleaned_data['financial_year']
        gl = GLPivDownload.objects.filter(
            financialYear=fy, account__in=[1, 2], resource__lt=4000)
        gl = gl.order_by('codeID')
        if form.cleaned_data['region']:
            gl = gl.filter(regionBranch=form.cleaned_data['region'])
        if form.cleaned_data['service']:
            gl = gl.filter(service=form.cleaned_data['service'])

        ibm = IBMData.objects.filter(
            financialYear=fy, servicePriorityID__iexact='GENERAL 01')

        # Service priority checkboxes.
        nc_sp = NCServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['ncChoice']).order_by('servicePriorityNo')
        pvs_sp = PVSServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['pvsChoice']).order_by('servicePriorityNo')
        fm_sp = SFMServicePriority.objects.filter(
            financialYear=fy, categoryID__in=form.cleaned_data['fmChoice']).order_by('servicePriorityNo')

        fpath = os.path.join(
            settings.STATIC_ROOT, 'excel', 'service_priority_base.xls')
        excel_template = open_workbook(
            fpath, formatting_info=True, on_demand=True)
        book = copy(excel_template)

        # Style & populate the worksheet.
        service_priority_report(book, gl, ibm, nc_sp, pvs_sp, fm_sp)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=serviceprioritydata.xls'
        book.save(response)  # Save the worksheet contents to the response.

        return response


class JSONResponseMixin(object):
    """View mixin to return a JSON response to requests.
    """
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(
            content, content_type='application/json', **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json.dumps(context)


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
        try:
            self.model._meta.get_field_by_name(self.fieldname)
        except:
            return HttpResponseBadRequest(
                'Invalid field name: {0}'.format(self.fieldname))
        r = self.model.objects.all()
        if request.GET.get('financialYear', None):
            r = r.filter(financialYear=request.GET['financialYear'])
        if request.GET.get('costCentre', None):
            r = r.filter(costCentre=request.GET['costCentre'])
        # Check for fields that may not exist on the model.
        try:
            if request.GET.get('regionBranch', None) and self.model._meta.get_field_by_name(
                    'regionBranch'):
                r = r.filter(regionBranch=request.GET['regionBranch'])
        except:
            pass
        try:
            if request.GET.get('service', None) and self.model._meta.get_field_by_name(
                    'service'):
                r = r.filter(costCentre=request.GET['service'])
        except:
            pass
        # If we're not after PKs, then we need to reduce the qs to distinct values.
        if not self.return_pk:
            r = r.distinct(self.fieldname)
        choices = []
        for i in r:
            choice_val = getattr(i, self.fieldname)
            if self.return_pk:
                choices.append([i.pk, choice_val])
            else:
                choices.append([choice_val, choice_val])
        choices.sort()
        context = {'choices': choices}
        return self.render_to_response(context)
