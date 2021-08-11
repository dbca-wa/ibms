from django import forms
from crispy_forms.layout import Submit, Layout, HTML, Div

from ibms.forms import HelperForm
from sfm.models import Quarter, CostCentre, SFMMetric, FinancialYear, MeasurementValue
from sfm.fields import (
    QtrModelChoiceField, SFMMetricModelChoiceField, SFMCostCentreModelChoiceField,
)


class OutputEntryForm(HelperForm):
    financial_year = forms.ModelChoiceField(
        label='Financial Year',
        queryset=FinancialYear.objects.all().order_by('financialYear'))
    quarter = QtrModelChoiceField(
        label='Quarter', queryset=Quarter.objects.none())
    cost_centre = forms.ModelChoiceField(
        label='Cost Centre',
        queryset=CostCentre.objects.all().order_by('costCentre'))
    sfm_metric_id = SFMMetricModelChoiceField(
        label='Metric ID #',
        queryset=SFMMetric.objects.none().order_by('metricID'))
    planned = forms.ChoiceField(
        label='Action planned?',
        widget=forms.RadioSelect,
        choices=[('true', 'Yes'), ('false', 'No')],
        required=False,
    )
    status = forms.ChoiceField(
        choices=MeasurementValue.STATUS_CHOICES,
        widget=forms.RadioSelect,
        required=False,
    )
    comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(OutputEntryForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('Please select ALL the fields below:'),
                    css_class='col-sm-12 col-md-9 col-lg-6 alert alert-info',
                ),
                css_class='row',
            ),
            # These divs is used by JS on the template.
            Div(
                'financial_year', 'quarter', 'cost_centre', 'sfm_metric_id',
                css_id='id_filter_fields',
            ),
            Div(
                Div(
                    Div(
                        HTML('''<span class="glyphicon glyphicon-info-sign"></span>&nbsp;
                            <span id="id_descriptor_text"></span>'''),
                        css_class='col-sm-12 col-md-9 col-lg-6 alert alert-warning',
                    ),
                    css_class='row', css_id='id_descriptor_row',
                ),
                Div(
                    Div(
                        HTML('Input required output values below:'),
                        css_class='row col-sm-12 col-md-9 col-lg-6 alert alert-info',
                    ),
                    Div(
                        'planned', 'status', 'comment',
                    ),
                    css_id='id_measurement_fields',
                ),
                Div(
                    Div(
                        HTML('''<span class="glyphicon glyphicon-info-sign"></span>&nbsp;
                        Ranking: <span id="id_example_text"></span>'''),
                        css_class='col-sm-12 col-md-9 col-lg-6 alert alert-warning',
                    ),
                    css_class='row', css_id='id_example_row',
                ),
                Div(
                    Submit(name='save', value='Save Output Values'),
                    css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2',
                ),
                css_id='id_input_div',
            ),
        )


class OutputUploadForm(HelperForm):
    FILE_CHOICES = (
        ('', '--Please Select--'),
        ('sfmmetrics', 'SFM Metrics'),
        ('costcentres', 'Cost Centres'),
        ('measurementvalues', 'Measurement values')
    )
    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all().order_by('financialYear'),
        required=True)
    upload_file_type = forms.ChoiceField(choices=FILE_CHOICES, required=True)
    upload_file = forms.FileField(label='Select file')

    def __init__(self, *args, **kwargs):
        super(OutputUploadForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            'financial_year',
            'upload_file_type',
            'upload_file',
            Div(
                Submit(name='output-upload', value='Upload'),
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
