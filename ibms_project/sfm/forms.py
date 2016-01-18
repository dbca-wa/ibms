from django import forms
from crispy_forms.layout import Submit, Layout, HTML, Div

from ibms.forms import HelperForm
from sfm.models import Quarter, CostCentre, SFMMetric, FinancialYear
from sfm.fields import (QtrModelChoiceField, SFMMetricModelChoiceField,
                     SFMCostCentreModelChoiceField)

FILE_CHOICES = (
    ('', '--Please Select--'),
    ('sfmmetrics', 'SFM Metrics'),
    ('costcentres', 'Cost Centres'),
)


class FMOutputsForm(HelperForm):
    financial_year = forms.ModelChoiceField(
        label='Financial Year', required=True,
        queryset=FinancialYear.objects.all().order_by('financialYear'))
    quarter = QtrModelChoiceField(
        label='Quarter', queryset=Quarter.objects.all(), required=True)
    cost_centre = forms.ModelChoiceField(
        label='Cost Centre', required=True,
        queryset=CostCentre.objects.all().order_by('costCentre'))
    sfm_metric_id = SFMMetricModelChoiceField(
        label='Metric ID #',
        queryset=SFMMetric.objects.all().order_by('metricID'))
    # Measurement value fields
    quantity = forms.FloatField(label='Number (#)', min_value=0, required=False)
    percentage = forms.FloatField(label='Percentage (%)', min_value=0, required=False)
    hectare = forms.FloatField(label='Hectares (ha)', min_value=0, required=False)
    kilometer = forms.FloatField(label='Kilometers (km)', min_value=0, required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(FMOutputsForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('Please select ALL the fields below:'),
                    css_class='col-sm-12 col-md-9 col-lg-6 alert alert-info'),
                css_class='row'),
            # These divs is used by JS on the template.
            Div(
                'financial_year', 'quarter', 'cost_centre', 'sfm_metric_id',
                css_id='id_filter_fields'),
            Div(
                Div(
                    HTML('''<span class="glyphicon glyphicon-info-sign"></span>&nbsp;
                        <span id="id_descriptor_text"></span>'''),
                    css_class='col-sm-12 col-md-9 col-lg-6 alert alert-warning'),
                css_class='row', css_id='id_descriptor_row'),
            Div(
                Div(
                    HTML('Input required output values below:'),
                    css_class='col-sm-12 col-md-9 col-lg-6 alert alert-info'),
                css_class='row', css_id='id_measurement_fields'),
            Div(
                Div(
                    'quantity', 'percentage', 'hectare', 'kilometer', 'comment',
                    css_class='row'),
                 css_id='id_measurement_fields'),
            Div(
                Div(
                    HTML('''<span class="glyphicon glyphicon-info-sign"></span>&nbsp;
                    Example: <span id="id_example_text"></span>'''),
                    css_class='col-sm-12 col-md-9 col-lg-6 alert alert-warning'),
                css_class='row', css_id='id_example_row'),
            Div(
                Submit(name='save', value='Save Output Values'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2'),
        )


class FMUploadForm(HelperForm):
    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all().order_by('financialYear'),
        required=True)
    upload_file_type = forms.ChoiceField(choices=FILE_CHOICES, required=True)
    upload_file = forms.FileField(label='Select file')

    def __init__(self, *args, **kwargs):
        super(FMUploadForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            'financial_year',
            'upload_file_type',
            'upload_file',
            Div(
                Submit(name='sfmupload', value='Upload'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )


class FMOutputReportForm(HelperForm):
    financial_year = forms.ModelChoiceField(
        label='Financial Year', required=True,
        queryset=FinancialYear.objects.all().order_by('financialYear'))
    quarter = QtrModelChoiceField(
        label='Quarter', queryset=Quarter.objects.all(), required=True)
    cost_centre = SFMCostCentreModelChoiceField(
        label='Cost Centre', required=True,
        queryset=CostCentre.objects.all().order_by('costCentre'))

    def __init__(self, *args, **kwargs):
        super(FMOutputReportForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            'financial_year',
            'quarter',
            'cost_centre',
            Div(
                Submit(name='download', value='Download'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )
