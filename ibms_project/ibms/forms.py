from django import forms
from django.db.utils import ProgrammingError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Div
from ibms.models import (
    GLPivDownload, FINYEAR_CHOICES, NCServicePriority, IBMData,
    GeneralServicePriority, PVSServicePriority, SFMServicePriority)


def getGenericChoices(classmodel, key, allowNull=False):
    """Generates a list of choices for a drop down from a model and key.
    """
    CHOICES = [('', '--------')] if allowNull else []
    try:
        for i in classmodel.objects.all().values_list(key, flat=True).distinct():
            CHOICES.append((i, i))
        CHOICES.sort()
    except ProgrammingError:  # This should only except with an empty database (no relations).
        pass
    return CHOICES


FILE_CHOICES = (
    ('', '--Please Select--'),
    ('General', (('GLPivotDownload', 'GL Pivot Download'),
                 ('IBMData', 'IBM Data'))),
    ('Strategic', (('CorporateStrategyData', 'IBMS Corporate Strategy'),
                   ('NCStrategyData', 'Nature Conservation'))),
    ('Service Priorities', (('GeneralServicePriorityData', 'General'),
                            ('NCServicePriorityData', 'Nature Conservation'),
                            ('PVSServicePriorityData', 'Parks & Visitor Services'),
                            ('ERServicePriorityData', 'Fire Services'),
                            ('SFMServicePriorityData', 'State Forest Management')))
)
REPORT_CHOICES = (
    ('', '--Please Select--'),
    ('0', 'Non DJ0 Activities'),
    ('1', 'DJ0 Activities Only'),
)


class HelperForm(forms.Form):
    """Base form class with a crispy_forms FormHelper.
    """
    def __init__(self, *args, **kwargs):
        super(HelperForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
        self.helper.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'


class FinancialYearFilterForm(HelperForm):
    """Base form class to be include a financial year filter select.
    """
    financial_year = forms.ChoiceField(
        choices=getGenericChoices(GLPivDownload, 'financialYear', allowNull=True))


class UploadForm(HelperForm):
    upload_file_type = forms.ChoiceField(choices=FILE_CHOICES)
    upload_file = forms.FileField(label='Select file')
    # We still use FINYEAR_CHOICES from the models.py because this covers
    # future uploads.
    financial_year = forms.ChoiceField(choices=FINYEAR_CHOICES)

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            'upload_file_type',
            'upload_file',
            'financial_year',
            Div(
                Submit('upload', 'Upload'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )


class DownloadForm(FinancialYearFilterForm):

    def __init__(self, request, *args, **kwargs):
        super(DownloadForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['cost_centre'] = forms.ChoiceField(
            choices=getGenericChoices(GLPivDownload, 'costCentre', allowNull=True),
            required=False)
        self.fields['region'] = forms.ChoiceField(
            choices=getGenericChoices(GLPivDownload, 'regionBranch', allowNull=True),
            required=False, label='Region/branch')
        self.fields['division'] = forms.ChoiceField(
            choices=getGenericChoices(GLPivDownload, 'division', allowNull=True),
            required=False)

        # Disable several fields on initial form load.
        for field in ['cost_centre', 'region', 'division']:
            self.fields[field].widget.attrs.update({'disabled': ''})

        # crispy_forms layout
        self.helper.layout = Layout(
            'financial_year', 'cost_centre', 'region', 'division',
            Div(
                Submit('download', 'Download'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )

    def clean(self):
        '''Validate that at least one (but only one) of CC, region or division
        has been selected.
        Superusers may choose none of these.
        '''
        if not self.request.user.is_superuser:
            d = self.cleaned_data
            if not d['cost_centre'] and not d['region'] and not d['division']:
                valid = False
            elif d['cost_centre'] and d['region'] and d['division']:
                valid = False
            elif d['cost_centre'] and (d['region'] or d['division']):
                valid = False
            elif d['region'] and (d['cost_centre'] or d['division']):
                valid = False
            elif d['division'] and (d['cost_centre'] or d['region']):
                valid = False
            else:
                valid = True
            if not valid:
                msg = 'You must choose either Cost Centre OR Region/Branch OR Division'
                self._errors['cost_centre'] = self.error_class([msg])
                self._errors['region'] = self.error_class([msg])
                self._errors['division'] = self.error_class([msg])
        return self.cleaned_data


class ReloadForm(FinancialYearFilterForm):

    def __init__(self, request, *args, **kwargs):
        super(ReloadForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['cost_centre'] = forms.ChoiceField(
            choices=getGenericChoices(GLPivDownload, 'costCentre', allowNull=True),
            required=True)
        self.fields['cost_centre'].widget.attrs.update({'disabled': ''})
        self.fields['ncChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(NCServicePriority, 'categoryID'),
            required=False, label='Wildlife Management')
        self.fields['pvsChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(PVSServicePriority, 'categoryID'),
            required=False, label='Parks Management')
        self.fields['fmChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(SFMServicePriority, 'categoryID'),
            required=False, label='Forest Management')

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:</div></div>'''),
            'financial_year',
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select a Cost Centre</div></div>'''),
            'cost_centre',
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relavant Service Priorities for your cost centre
                </div></div>'''),
            HTML('<div class="checkbox">'),
            'ncChoice',
            'pvsChoice',
            'fmChoice',
            HTML('</div>'),
            Div(
                Submit('reload', 'Reload'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )


class DataAmendmentForm(FinancialYearFilterForm):

    def __init__(self, request, *args, **kwargs):
        super(DataAmendmentForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['cost_centre'] = forms.ChoiceField(
            choices=getGenericChoices(GLPivDownload, 'costCentre', allowNull=True),
            required=False)
        self.fields['region'] = forms.ChoiceField(
            choices=getGenericChoices(GLPivDownload, 'regionBranch', allowNull=True),
            required=False, label='Region/branch')
        self.fields['service'] = forms.ChoiceField(
            choices=getGenericChoices(GLPivDownload, 'service', allowNull=True),
            required=False, label='Service')
        self.fields['budget_area'] = forms.ChoiceField(
            choices=getGenericChoices(IBMData, 'budgetArea', allowNull=True),
            required=False, label='Budget Area')
        self.fields['project_sponsor'] = forms.ChoiceField(
            choices=getGenericChoices(IBMData, 'projectSponsor', allowNull=True),
            required=False, label='Project Sponsor')
        #self.fields['genChoice'] = forms.MultipleChoiceField(
        #    widget=forms.HiddenInput(),
        #    choices=getGenericChoices(GeneralServicePriority, 'categoryID'),
        #    required=False)
        self.fields['ncChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(NCServicePriority, 'categoryID'),
            required=False, label='Wildlife Management')
        self.fields['pvsChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(PVSServicePriority, 'categoryID'),
            required=False, label='Parks Management')
        self.fields['fmChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(SFMServicePriority, 'categoryID'),
            required=False, label='Forest Management')

        # Disable several fields on initial form load.
        if not self.request.user.is_superuser:
            for field in [
                    'cost_centre', 'region', 'service', 'budget_area',
                    'project_sponsor']:
                self.fields[field].widget.attrs.update({'disabled': ''})

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:
                </div></div>'''),
            'financial_year',
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select either Cost Centre OR Region/Branch:</div>
                </div>'''),
            'cost_centre',
            'region',
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select appropriate filter(s) to generate the codes required (optional):
                </div></div>'''),
            'service',
            'budget_area',
            'project_sponsor',
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relavant Service Priorities for your Region/Branch:
                </div></div>'''),
            HTML('<div class="checkbox">'),
            'ncChoice',
            'pvsChoice',
            'fmChoice',
            HTML('</div>'),
            Div(
                Submit('dataamendment', 'Data Amendment'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )

    def clean(self):
        # Non-superusers must choose either cost centre or region/branch.
        # Superusers may choose neither.
        if not self.request.user.is_superuser:
            if not self.cleaned_data[
                    'cost_centre'] and not self.cleaned_data['region']:
                msg = 'You must choose either Cost Centre OR Region/Branch'
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
            if self.cleaned_data[
                    'cost_centre'] and self.cleaned_data['region']:
                msg = 'You must choose either Cost Centre OR Region/Branch'
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
        return self.cleaned_data


class ServicePriorityDataForm(FinancialYearFilterForm):

    def __init__(self, request, *args, **kwargs):
        super(ServicePriorityDataForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['region'] = forms.ChoiceField(
            choices=getGenericChoices(
                GLPivDownload,
                'regionBranch',
                allowNull=True),
            required=False,
            label='Region/branch')
        self.fields['service'] = forms.ChoiceField(
            choices=getGenericChoices(
                GLPivDownload,
                'service',
                allowNull=True),
            required=False,
            label='Service')
        #self.fields['genChoice'] = forms.MultipleChoiceField(
        #    widget=forms.HiddenInput(),
        #    choices=getGenericChoices(
        #        GeneralServicePriority,
        #        'categoryID'),
        #    required=False,
        #    label='General Service Priorities')
        self.fields['ncChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(
                NCServicePriority,
                'categoryID'),
            required=False,
            label='Wildlife Management')
        self.fields['pvsChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(
                PVSServicePriority,
                'categoryID'),
            required=False,
            label='Parks Management')
        self.fields['fmChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(
                SFMServicePriority,
                'categoryID'),
            required=False,
            label='Forest Management')

        # Disable several fields on initial form load.
        for field in ['region', 'service']:
            self.fields[field].widget.attrs.update({'disabled': ''})

        # crispy_forms layout
        self.helper.layout = Layout(
            'financial_year',
            'region',
            'service',
            HTML('<div class="checkbox">'),
            'ncChoice',
            'pvsChoice',
            'fmChoice',
            HTML('</div>'),
            Div(
                Submit('download', 'Download'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )


class CodeUpdateForm(FinancialYearFilterForm):

    def __init__(self, request, *args, **kwargs):
        super(CodeUpdateForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['cost_centre'] = forms.ChoiceField(
            choices=getGenericChoices(
                GLPivDownload,
                'costCentre',
                allowNull=True),
            required=True)
        #self.fields['genChoice'] = forms.MultipleChoiceField(
        #    widget=forms.HiddenInput(),
        #    choices=getGenericChoices(
        #        GeneralServicePriority,
        #        'categoryID'),
        #    required=False,
        #    label='General Service Priorities')
        self.fields['ncChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(
                NCServicePriority,
                'categoryID'),
            required=False,
            label='Wildlife Management')
        self.fields['pvsChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(
                PVSServicePriority,
                'categoryID'),
            required=False,
            label='Parks Management')
        self.fields['fmChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(
                SFMServicePriority,
                'categoryID'),
            required=False,
            label='Forest Management')

        # Initially disable the cost centre field on form load.
        self.fields['cost_centre'].widget.attrs.update({'disabled': ''})

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:
                </div></div>'''),
            'financial_year',
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select a Cost Centre
                </div></div>'''),
            'cost_centre',
            HTML('''<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relavant Service Priorities for your cost centre
                </div></div>'''),
            HTML('<div class="checkbox">'),
            'ncChoice',
            'pvsChoice',
            'fmChoice',
            HTML('</div>'),
            Div(
                Submit('codeupdate', 'Code Update'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )


class ManagerCodeUpdateForm(FinancialYearFilterForm):

    def __init__(self, request, *args, **kwargs):
        super(ManagerCodeUpdateForm, self).__init__(*args, **kwargs)
        self.fields['report_type'] = forms.ChoiceField(
            choices=REPORT_CHOICES, label='Report Type?', required=True)
        #self.fields['genChoice'] = forms.MultipleChoiceField(
        #    widget=forms.HiddenInput(),
        #    choices=getGenericChoices(GeneralServicePriority, 'categoryID'),
        #    required=False, label='General Service Priorities')
        self.fields['ncChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(NCServicePriority, 'categoryID'),
            required=False, label='Wildlife Management')
        self.fields['pvsChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(PVSServicePriority, 'categoryID'),
            required=False, label='Parks Management')
        self.fields['fmChoice'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=getGenericChoices(SFMServicePriority, 'categoryID'),
            required=False, label='Forest Management')

        # crispy_forms layout
        self.helper.layout = Layout(
            'report_type',
            'financial_year',
            HTML('<div class="checkbox">'),
            'ncChoice',
            'pvsChoice',
            'fmChoice',
            HTML('</div>'),
            Div(
                Submit('codeupdate', 'Code Update'),
                css_class='col-sm-offset-4 col-md-offset-3 col-lg-offset-2')
        )
