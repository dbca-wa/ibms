from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout, Submit
from django import forms
from sfm.models import FinancialYear

from ibms.models import GLPivDownload, IBMData, NCServicePriority, PVSServicePriority, SFMServicePriority


def get_generic_choices(model, key, allow_null=False):
    """Generates a list of choices for a drop down from a model and key."""
    CHOICES = [("", "--------")] if allow_null else []
    for i in model.objects.all().values_list(key, flat=True).distinct():
        CHOICES.append((str(i), str(i)))
    CHOICES.sort()

    return CHOICES


FILE_CHOICES = (
    ("", "--Please Select--"),
    ("General", (("GLPivotDownload", "GL Pivot Download"), ("IBMData", "IBM Data"))),
    ("Strategic", (("CorporateStrategyData", "IBMS Corporate Strategy"), ("NCStrategyData", "Nature Conservation"))),
    (
        "Service Priorities",
        (
            ("GeneralServicePriorityData", "General"),
            ("NCServicePriorityData", "Nature Conservation"),
            ("PVSServicePriorityData", "Parks & Visitor Services"),
            ("ERServicePriorityData", "Fire Services"),
            ("SFMServicePriorityData", "Forest Management"),
            ("ServicePriorityMappings", "Service Priority Mapping"),
        ),
    ),
)
REPORT_CHOICES = (
    (None, "--Please Select--"),
    ("dj0", "DJ0 activities only"),
    ("no-dj0", "Exclude DJ0 activities"),
)


class HelperForm(forms.Form):
    """Base form class with a crispy_forms FormHelper."""

    def __init__(self, *args, **kwargs):
        super(HelperForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-xs-12 col-sm-4 col-md-3 col-lg-2"
        self.helper.field_class = "col-xs-12 col-sm-8 col-md-6 col-lg-4"


class FinancialYearFilterForm(HelperForm):
    """Base form class to be include a financial year filter select."""

    financial_year = forms.ModelChoiceField(queryset=FinancialYear.objects.all().order_by("financialYear"))


class ClearGLPivotForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(ClearGLPivotForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            HTML("""<div class="row">
                <div class="col-md-10 col-lg-9 alert alert-warning">
                Please confirm that you want to clear all GL Pivot entries for the selected financial year.</div></div>"""),
            Div(
                "financial_year",
                Submit("confirm", "Confirm", css_class="btn-danger"),
                Submit("cancel", "Cancel"),
                css_class="col-sm-offset-3 col-md-offset-2 col-lg-offset-1",
            ),
        )


class UploadForm(FinancialYearFilterForm):
    upload_file_type = forms.ChoiceField(choices=FILE_CHOICES)
    upload_file = forms.FileField(label="Select file")

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            "upload_file_type",
            "upload_file",
            "financial_year",
            Div(Submit("upload", "Upload"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class DownloadForm(FinancialYearFilterForm):
    def __init__(self, request, *args, **kwargs):
        super(DownloadForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields["cost_centre"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "costCentre", allow_null=True), required=False
        )
        self.fields["region"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "regionBranch", allow_null=True),
            required=False,
            label="Region/branch",
        )
        self.fields["division"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "division", allow_null=True), required=False
        )

        # Disable several fields on initial form load.
        for field in ["cost_centre", "region", "division"]:
            self.fields[field].widget.attrs.update({"disabled": ""})

        # crispy_forms layout
        self.helper.layout = Layout(
            "financial_year",
            "cost_centre",
            "region",
            "division",
            Div(Submit("download", "Download"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    def clean(self):
        """Validate that at least one (but only one) of CC, region or division
        has been selected.
        Superusers may choose none of these.
        """
        if not self.request.user.is_superuser:
            d = self.cleaned_data
            if not d["cost_centre"] and not d["region"] and not d["division"]:
                valid = False
            elif d["cost_centre"] and d["region"] and d["division"]:
                valid = False
            elif d["cost_centre"] and (d["region"] or d["division"]):
                valid = False
            elif d["region"] and (d["cost_centre"] or d["division"]):
                valid = False
            elif d["division"] and (d["cost_centre"] or d["region"]):
                valid = False
            else:
                valid = True
            if not valid:
                msg = "You must choose either Cost Centre OR Region/Branch OR Division"
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
                self._errors["division"] = self.error_class([msg])
        return self.cleaned_data


class ReloadForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(ReloadForm, self).__init__(*args, **kwargs)
        self.fields["cost_centre"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "costCentre", allow_null=True), required=True
        )
        self.fields["cost_centre"].widget.attrs.update({"disabled": ""})
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "categoryID"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "categoryID"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "categoryID"),
            required=False,
            label="Forest Management",
        )

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:</div></div>"""),
            "financial_year",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select a Cost Centre</div></div>"""),
            "cost_centre",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relevant Service Priorities for your cost centre
                </div></div>"""),
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("reload", "Reload"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class DataAmendmentForm(FinancialYearFilterForm):
    def __init__(self, request, *args, **kwargs):
        super(DataAmendmentForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields["cost_centre"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "costCentre", allow_null=True), required=False
        )
        self.fields["region"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "regionBranch", allow_null=True),
            required=False,
            label="Region/branch",
        )
        self.fields["service"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "service", allow_null=True), required=False, label="Service"
        )
        self.fields["budget_area"] = forms.ChoiceField(
            choices=get_generic_choices(IBMData, "budgetArea", allow_null=True), required=False, label="Budget Area"
        )
        self.fields["project_sponsor"] = forms.ChoiceField(
            choices=get_generic_choices(IBMData, "projectSponsor", allow_null=True),
            required=False,
            label="Project Sponsor",
        )
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "categoryID"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "categoryID"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "categoryID"),
            required=False,
            label="Forest Management",
        )

        # Disable several fields on initial form load.
        if not self.request.user.is_superuser:
            for field in ["cost_centre", "region", "service", "budget_area", "project_sponsor"]:
                self.fields[field].widget.attrs.update({"disabled": ""})

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:
                </div></div>"""),
            "financial_year",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select either Cost Centre OR Region/Branch:</div>
                </div>"""),
            "cost_centre",
            "region",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select appropriate filter(s) to generate the codes required (optional):
                </div></div>"""),
            "service",
            "budget_area",
            "project_sponsor",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relevant Service Priorities for your Region/Branch:
                </div></div>"""),
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("dataamendment", "Data Amendment"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    def clean(self):
        # Non-superusers must choose either cost centre or region/branch.
        # Superusers may choose neither.
        if not self.request.user.is_superuser:
            if not self.cleaned_data["cost_centre"] and not self.cleaned_data["region"]:
                msg = "You must choose either Cost Centre OR Region/Branch"
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
            if self.cleaned_data["cost_centre"] and self.cleaned_data["region"]:
                msg = "You must choose either Cost Centre OR Region/Branch"
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
        return self.cleaned_data


class ServicePriorityDataForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(ServicePriorityDataForm, self).__init__(*args, **kwargs)
        self.fields["region"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "regionBranch", allow_null=True),
            required=False,
            label="Region/branch",
        )
        self.fields["service"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "service", allow_null=True), required=False, label="Service"
        )
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "categoryID"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "categoryID"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "categoryID"),
            required=False,
            label="Forest Management",
        )

        # Disable several fields on initial form load.
        for field in ["region", "service"]:
            self.fields[field].widget.attrs.update({"disabled": ""})

        # crispy_forms layout
        self.helper.layout = Layout(
            "financial_year",
            "region",
            "service",
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("download", "Download"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class CodeUpdateForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(CodeUpdateForm, self).__init__(*args, **kwargs)
        self.fields["cost_centre"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "costCentre", allow_null=True), required=True
        )
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "categoryID"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "categoryID"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "categoryID"),
            required=False,
            label="Forest Management",
        )

        # Initially disable the cost centre field on form load.
        self.fields["cost_centre"].widget.attrs.update({"disabled": ""})

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:
                </div></div>"""),
            "financial_year",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select a Cost Centre
                </div></div>"""),
            "cost_centre",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relevant Service Priorities for your cost centre
                </div></div>"""),
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("codeupdate", "Code Update"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class ManagerCodeUpdateForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(ManagerCodeUpdateForm, self).__init__(*args, **kwargs)
        self.fields["report_type"] = forms.ChoiceField(choices=REPORT_CHOICES, label="Report Type?", required=True)
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "categoryID"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "categoryID"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "categoryID"),
            required=False,
            label="Forest Management",
        )

        self.helper.layout = Layout(
            "report_type",
            "financial_year",
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("codeupdate", "Code Update"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )
