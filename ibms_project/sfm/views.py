from __future__ import print_function, unicode_literals, absolute_import
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormView
import json
import os
from openpyxl import load_workbook
import tempfile

from ibms.views import JSONResponseMixin, T
from ibms.utils import get_download_period, breadcrumb_trail
from sfm.forms import FMUploadForm, FMOutputReportForm, FMOutputsForm
from sfm.models import SFMMetric, MeasurementType, MeasurementValue
from sfm.report import outputs_report
from sfm.sfm_file_funcs import process_upload_file, validate_file


class ProtectedFormView(FormView):
    """Base FormView class, to required authentication.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedFormView, self).dispatch(*args, **kwargs)


class FMOutputsView(ProtectedFormView):
    template_name = 'sfm/outputs.html'
    form_class = FMOutputsForm

    def get_context_data(self, **kwargs):
        context = super(FMOutputsView, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'FM Outputs'])
        context['download_period'] = get_download_period()
        context['title'] = 'FM Outputs'
        links = [(reverse('site_home'), 'Home'), (None, 'FM Outputs')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        if self.request.user.is_superuser:
            context['superuser'] = True
        # Context variable to allow mapping of MeasurementType fields.
        mt = [(i.pk, i.unit.lower()) for i in MeasurementType.objects.all()]
        context['measurement_types'] = json.dumps(mt)
        return context

    def get_success_url(self):
        return reverse('sfmoutcome')

    def form_valid(self, form):
        d = form.cleaned_data
        # Iterate through each of the input value fields.
        for val in ['quantity', 'percentage', 'hectare', 'kilometer']:
            mt = MeasurementType.objects.get(unit__iexact=val)
            mv, created = MeasurementValue.objects.get_or_create(
                quarter=d['quarter'], sfmMetric=d['sfm_metric_id'],
                measurementType=mt, costCentre=d['cost_centre'])
            mv.value = d[val]
            if d['comment']:
                mv.comment = d['comment']
            mv.save()

        messages.success(self.request, 'Output values updated successfully.')
        return super(FMOutputsView, self).form_valid(form)


class FMUploadView(ProtectedFormView):
    template_name = 'ibms/form.html'
    form_class = FMUploadForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect(reverse('sfmupload'))
        return super(FMUploadView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FMUploadView, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'FM Upload'])
        context['download_period'] = get_download_period()
        context['title'] = 'FM Upload'
        links = [(reverse('site_home'), 'Home'), (None, 'FM Output Report')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        context['sfmupload_page'] = True
        if self.request.user.is_superuser:
            context['superuser'] = True
        return context

    def get_success_url(self):
        return reverse('sfmupload')

    def form_valid(self, form):
        file_type = form.cleaned_data['upload_file_type']
        fy = form.cleaned_data['financial_year']
        if validate_file(form.cleaned_data['upload_file'], file_type):
            temp = tempfile.NamedTemporaryFile(delete=True)
            for chunk in form.cleaned_data['upload_file'].chunks():
                temp.write(chunk)
            temp.flush()
            process_upload_file(temp.name, file_type, fy)
            messages.success(self.request, 'FM upload values updated successfully.')
        else:
            messages.error(
                self.request,
                'This file appears to be of an incorrect type. Please choose a {} file.'.format(file_type))
        return super(FMUploadView, self).form_valid(form)


class FMOutputReport(ProtectedFormView):
    template_name = 'sfm/output_report.html'
    form_class = FMOutputReportForm

    def get_context_data(self, **kwargs):
        context = super(FMOutputReport, self).get_context_data(**kwargs)
        context['page_title'] = ' | '.join([T, 'FM Output Report'])
        context['download_period'] = get_download_period()
        context['title'] = 'FM Output Report'
        links = [(reverse('site_home'), 'Home'), (None, 'FM Output Report')]
        context['breadcrumb_trail'] = breadcrumb_trail(links)
        context['sfmdownload_page'] = True
        if self.request.user.is_superuser:
            context['superuser'] = True
        return context

    def form_valid(self, form):
        d = form.cleaned_data
        fy = d['financial_year']
        qtr = d['quarter']
        cc = d['cost_centre']
        sfm = SFMMetric.objects.filter(financialYear=fy).order_by('servicePriorityNo', 'metricID')
        # Ordered list of service priority numbers.
        spn = sorted(set(sfm.values_list('servicePriorityNo', flat=True)))
        # Current download period.
        dp = datetime.strftime(get_download_period(), '%d/%m/%Y')
        fpath = os.path.join(
            settings.STATIC_ROOT, 'excel', 'fm_outputs.xlsx')
        book = load_workbook(fpath)

        # Style & populate the worksheet.
        outputs_report(book, sfm, spn, dp, fy, qtr, cc)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=fm_outputs.xlsx'
        book.save(response)  # Save the worksheet contents to the response.
        return response


class MeasurementValueJSON(JSONResponseMixin, BaseDetailView):
    """Utility view to return MeasurementValue object values as JSON,
    based upon the passed-in filter values.
    """
    def get(self, request, *args, **kwargs):
        r = MeasurementValue.objects.all()
        if request.GET.get('quarter', None):
            r = r.filter(quarter=request.GET['quarter'])
        if request.GET.get('costCentre', None):
            r = r.filter(costCentre=request.GET['costCentre'])
        if request.GET.get('sfmMetric', None):
            metric = SFMMetric.objects.get(pk=request.GET['sfmMetric']).__dict__
            metric.pop('_state')
            r = r.filter(sfmMetric__id=metric['id'])
        else:
            metric = dict()
        if request.GET.get('measurementType', None):
            r = r.filter(measurementType=request.GET['measurementType'])

        values = []
        for i in r:
            d = i.__dict__
            d.pop('_state')  # Remove the _state key value from the dict.
            values.append(d)
        context = {'sfmMetric': metric, 'measurementValues': values}
        return self.render_to_response(context)
