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

    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all().order_by("-financialYear"), empty_label=None, required=True
    )


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
        self.fields["division"] = forms.ChoiceField(choices=get_generic_choices(GLPivDownload, "division", allow_null=True), required=False)

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


class IbmDataFilterForm(forms.Form):
    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all().order_by("-financialYear"), empty_label=None, required=True
    )
    cost_centre = forms.ChoiceField(choices=[("", "--------")], required=False)
    region = forms.ChoiceField(choices=[("", "--------")], required=False, label="Region/branch")
    budget_area = forms.ChoiceField(choices=[("", "--------")], required=False)
    project_sponsor = forms.ChoiceField(choices=[("", "--------")], required=False)
    service = forms.ChoiceField(choices=[("", "--------")], required=False)
    project = forms.ChoiceField(choices=[("", "--------")], required=False)
    job = forms.ChoiceField(choices=[("", "--------")], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set field options for CC and Region/branch.
        fy = FinancialYear.objects.get(financialYear=kwargs["initial"]["financial_year"])
        cost_centres = IBMData.objects.filter(fy=fy, costCentre__isnull=False).values_list("costCentre", flat=True).distinct()
        self.fields["cost_centre"].choices += sorted([(i, i) for i in cost_centres])
        regions = GLPivDownload.objects.filter(fy=fy, regionBranch__isnull=False).values_list("regionBranch", flat=True).distinct()
        self.fields["region"].choices += sorted([(i, i) for i in regions])

        if "cost_centre" in kwargs["initial"] and kwargs["initial"]["cost_centre"]:
            budget_areas = (
                IBMData.objects.filter(fy=fy, costCentre=kwargs["initial"]["cost_centre"], budgetArea__isnull=False)
                .values_list("budgetArea", flat=True)
                .distinct()
            )
            self.fields["budget_area"].choices += sorted([(i, i) for i in budget_areas if i])
            project_sponsors = (
                IBMData.objects.filter(fy=fy, costCentre=kwargs["initial"]["cost_centre"], projectSponsor__isnull=False)
                .values_list("projectSponsor", flat=True)
                .distinct()
            )
            self.fields["project_sponsor"].choices += sorted([(i, i) for i in project_sponsors if i])
            services = (
                IBMData.objects.filter(fy=fy, costCentre=kwargs["initial"]["cost_centre"], service__isnull=False)
                .values_list("service", flat=True)
                .distinct()
            )
            self.fields["service"].choices += sorted([(i, i) for i in services if i])
            projects = (
                IBMData.objects.filter(fy=fy, costCentre=kwargs["initial"]["cost_centre"], project__isnull=False)
                .values_list("project", flat=True)
                .distinct()
            )
            self.fields["project"].choices += sorted([(i, i) for i in projects if i])
            jobs = (
                IBMData.objects.filter(fy=fy, costCentre=kwargs["initial"]["cost_centre"], job__isnull=False)
                .values_list("job", flat=True)
                .distinct()
            )
            self.fields["job"].choices += sorted([(i, i) for i in jobs if i])

        if "region" in kwargs["initial"] and kwargs["initial"]["region"]:
            region_branch = kwargs["initial"]["region"]
            cost_centres = set(GLPivDownload.objects.filter(fy=fy, regionBranch=region_branch).values_list("costCentre", flat=True))

            budget_areas = (
                IBMData.objects.filter(fy=fy, costCentre__in=cost_centres, budgetArea__isnull=False)
                .values_list("budgetArea", flat=True)
                .distinct()
            )
            self.fields["budget_area"].choices += sorted([(i, i) for i in budget_areas if i])
            project_sponsors = (
                IBMData.objects.filter(fy=fy, costCentre__in=cost_centres, projectSponsor__isnull=False)
                .values_list("projectSponsor", flat=True)
                .distinct()
            )
            self.fields["project_sponsor"].choices += sorted([(i, i) for i in project_sponsors if i])
            services = (
                IBMData.objects.filter(fy=fy, costCentre__in=cost_centres, service__isnull=False)
                .values_list("service", flat=True)
                .distinct()
            )
            self.fields["service"].choices += sorted([(i, i) for i in services if i])
            projects = (
                IBMData.objects.filter(fy=fy, costCentre__in=cost_centres, project__isnull=False)
                .values_list("project", flat=True)
                .distinct()
            )
            self.fields["project"].choices += sorted([(i, i) for i in projects if i])
            jobs = IBMData.objects.filter(fy=fy, costCentre__in=cost_centres, job__isnull=False).values_list("job", flat=True).distinct()
            self.fields["job"].choices += sorted([(i, i) for i in jobs if i])

        # crispy_forms layout
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-xs-12 col-sm-4 col-md-3 col-lg-2"
        self.helper.field_class = "col-xs-12 col-sm-8 col-md-6 col-lg-4"
        self.helper.layout = Layout(
            "financial_year",
            HTML("""<div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Select either Cost Centre OR Region/Branch:</div>"""),
            "cost_centre",
            "region",
            HTML("""<div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Select additional filter(s) to limit records returned:
                </div>"""),
            "budget_area",
            "project_sponsor",
            "service",
            "project",
            "job",
            Div(Submit("filter", "Filter"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class ListTextWidget(forms.TextInput):
    """A customised TextInput widget, which accepts a list of options and renders
    a datalist element inline with the text input element.
    References:
      - https://docs.djangoproject.com/en/dev/ref/forms/widgets/#customizing-widget-instances
      - https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data_list
    """

    def __init__(self, name, data_list, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({"list": f"{self._name}_list"})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = f'<datalist id="{self._name}_list">'
        for item in self._list:
            data_list += f'<option value="{item}">'
        data_list += "</datalist>"

        return text_html + data_list


class IbmDataForm(forms.ModelForm):
    budgetArea = forms.CharField(
        label="Budget area",
        required=True,
        help_text="Free text. Delete existing value and click to display list.",
    )
    projectSponsor = forms.CharField(
        label="Project sponsor",
        required=False,
        help_text="Free text. Delete existing value and click to display list.",
    )
    servicePriorityID = forms.ChoiceField(
        choices=[("", "--------")],
        label="Service priority ID",
        required=False,
        help_text="Must match Service Number e.g. S24 - WM",
    )
    marineKPI = forms.CharField(
        label="Marine KPI",
        required=False,
        help_text="Mandatory for Marine Parks. Free text. Delete existing value and click to display list.",
    )
    regionProject = forms.CharField(
        label="Region project",
        required=False,
        help_text="Mandatory for PfoP. Free text. Delete existing value and click to display list.",
    )
    regionDescription = forms.CharField(
        label="Region description",
        required=False,
        help_text="Mandatory for PfoP. Free text. Delete existing value and click to display list.",
    )

    save_button = Submit("save", "Save", css_class="btn-lg")
    cancel_button = Submit("cancel", "Cancel", css_class="btn-secondary")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]

        # CharFields using ListTextWidget
        budget_areas = (
            IBMData.objects.filter(fy=instance.fy, costCentre=instance.costCentre, budgetArea__isnull=False)
            .exclude(budgetArea="")
            .values_list("budgetArea", flat=True)
            .distinct()
        )
        budget_areas = sorted(list(budget_areas))
        self.fields["budgetArea"].widget = ListTextWidget(name="budget_areas", data_list=budget_areas)

        project_sponsors = (
            IBMData.objects.filter(fy=instance.fy, costCentre=instance.costCentre, projectSponsor__isnull=False)
            .exclude(projectSponsor="")
            .values_list("projectSponsor", flat=True)
            .distinct()
        )
        project_sponsors = sorted(list(project_sponsors))
        self.fields["projectSponsor"].widget = ListTextWidget(name="project_sponsors", data_list=project_sponsors)

        service_priority_ids = (
            IBMData.objects.filter(fy=instance.fy, costCentre=instance.costCentre, servicePriorityID__isnull=False)
            .values_list("servicePriorityID", flat=True)
            .distinct()
        )
        self.fields["servicePriorityID"].choices += sorted([(i, i) for i in service_priority_ids if i])

        marine_kpis = (
            IBMData.objects.filter(fy=instance.fy, costCentre=instance.costCentre, marineKPI__isnull=False)
            .exclude(marineKPI="")
            .values_list("marineKPI", flat=True)
            .distinct()
        )
        marine_kpis = sorted(list(marine_kpis))
        self.fields["marineKPI"].widget = ListTextWidget(name="marine_kpi", data_list=marine_kpis)

        region_projects = (
            IBMData.objects.filter(fy=instance.fy, costCentre=instance.costCentre, regionProject__isnull=False)
            .exclude(regionProject="")
            .values_list("regionProject", flat=True)
            .distinct()
        )
        region_projects = sorted(list(region_projects))
        self.fields["regionProject"].widget = ListTextWidget(name="region_project", data_list=region_projects)

        region_descriptions = (
            IBMData.objects.filter(fy=instance.fy, costCentre=instance.costCentre, regionDescription__isnull=False)
            .exclude(regionDescription="")
            .values_list("regionDescription", flat=True)
            .distinct()
        )
        region_descriptions = sorted(list(region_descriptions))
        self.fields["regionDescription"].widget = ListTextWidget(name="region_description", data_list=region_descriptions)

        # Readonly fields
        for field in [
            "ibmIdentifier",
            "fy",
            "costCentre",
            "account",
            "service",
            "activity",
            "project",
            "job",
        ]:
            self.fields[field].required = False
            self.fields[field].disabled = True
            self.fields[field].widget = forms.TextInput(attrs={"readonly": "readonly"})

        # Business rule: for accounts 1, 2 and 42, the servicePriorityID field is compulsory.
        if instance.account in [1, 2, 42]:
            self.fields["servicePriorityID"].required = True

        # Non-essential Textarea fields.
        for field in [
            "regionalSpecificInfo",
            "annualWPInfo",
            "priorityActionNo",
            "priorityLevel",
        ]:
            self.fields[field].required = False
            # Use smaller textarea widgets.
            self.fields[field].widget = forms.Textarea(attrs={"cols": "40", "rows": "4"})

        # crispy_forms layout
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-xs-12 col-sm-4 col-md-2"
        self.helper.field_class = "col-xs-12 col-sm-8 col-md-10"
        self.helper.help_text_inline = True
        self.helper.attrs = {"novalidate": ""}
        self.helper.layout = Layout(
            "ibmIdentifier",
            "fy",
            "budgetArea",
            "projectSponsor",
            "regionalSpecificInfo",
            "servicePriorityID",
            "annualWPInfo",
            "costCentre",
            "account",
            "service",
            "activity",
            "project",
            "job",
            "priorityActionNo",
            "priorityLevel",
            "marineKPI",
            "regionProject",
            "regionDescription",
            Div(self.save_button, self.cancel_button, css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    class Meta:
        model = IBMData
        fields = [
            "ibmIdentifier",
            "fy",
            "budgetArea",
            "projectSponsor",
            "regionalSpecificInfo",
            "servicePriorityID",
            "annualWPInfo",
            "costCentre",
            "account",
            "service",
            "activity",
            "project",
            "job",
            "priorityActionNo",
            "priorityLevel",
            "marineKPI",
            "regionProject",
            "regionDescription",
        ]
        exclude = ["id"]
