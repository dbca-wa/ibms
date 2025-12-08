import csv

from django import forms
from django.contrib.admin import ModelAdmin, register
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from .models import (
    CorporateStrategy,
    DepartmentProgram,
    ERServicePriority,
    GeneralServicePriority,
    GLPivDownload,
    IBMData,
    NCServicePriority,
    NCStrategicPlan,
    PVSServicePriority,
    ServicePriorityMapping,
    SFMServicePriority,
)


def export_as_csv_action(fields=None, translations=None, exclude=None, header=True, description="Export selected objects to CSV"):
    """
    This function adds an "Export as CSV" action to a model in the Django admin site.
    Register the action using the ModelAdmin ``action`` option.
    ``fields`` and ``exclude`` work the same as those Django ModelForm options (use one or the other).
    ``header`` defines whether or not the column names are output as the first row.

    Ref: http://djangosnippets.org/snippets/2020/
    """

    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        """
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]
        if fields:
            field_names = fields
        elif exclude:
            excludeset = set(exclude)
            field_names = [f for f in field_names if f not in excludeset]
        # Create the response object.
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={0}.csv".format(str(opts).replace(".", "_"))
        # Write the CSV to the response object.
        writer = csv.writer(response)
        if header:
            writer.writerow(list(translations))
        else:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = description
    return export_as_csv


@register(IBMData)
class IBMDataAdmin(VersionAdmin):
    date_hierarchy = "modified"
    search_fields = ("fy__financialYear", "ibmIdentifier", "budgetArea", "modifier__username")
    list_display = ("ibmIdentifier", "fy", "costCentre", "budgetArea", "servicePriorityID", "modified", "modifier")
    list_filter = ("fy__financialYear", "costCentre", "budgetArea", "service")
    ordering = ("ibmIdentifier",)
    readonly_fields = (
        "fy",
        "ibmIdentifier",
        "budgetArea",
        "projectSponsor",
        "regionalSpecificInfo",
        "servicePriorityID",
        "annualWPInfo",
        "costCentre",
        "account_display",
        "service",
        "activity",
        "project",
        "job",
        "priorityActionNo",
        "priorityLevel",
        "marineKPI",
        "regionProject",
        "regionDescription",
        "modified",
        "modifier",
    )
    fieldsets = (
        (
            "IBM data record",
            {
                "fields": (
                    "fy",
                    "ibmIdentifier",
                    "budgetArea",
                    "projectSponsor",
                    "regionalSpecificInfo",
                    "servicePriorityID",
                    "annualWPInfo",
                    "costCentre",
                    "account_display",
                    "service",
                    "activity",
                    "project",
                    "job",
                    "priorityActionNo",
                    "priorityLevel",
                    "marineKPI",
                    "regionProject",
                    "regionDescription",
                )
            },
        ),
        ("Audit fields", {"fields": ("modified", "modifier")}),
    )
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "ibmIdentifier",
                "costCentre",
                "account",
                "service",
                "activity",
                "project",
                "job",
                "budgetArea",
                "projectSponsor",
                "regionalSpecificInfo",
                "servicePriorityID",
                "annualWPInfo",
                "priorityActionNo",
                "priorityLevel",
                "marineKPI",
                "regionProject",
                "regionDescription",
                "last modified by",
                "last modified",
            ],
            fields=[
                "fy",
                "ibmIdentifier",
                "costCentre",
                "account",
                "service",
                "activity",
                "project",
                "job",
                "budgetArea",
                "projectSponsor",
                "regionalSpecificInfo",
                "servicePriorityID",
                "annualWPInfo",
                "priorityActionNo",
                "priorityLevel",
                "marineKPI",
                "regionProject",
                "regionDescription",
                "modifier",
                "modified",
            ],
        )
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def account_display(self, obj):
        return obj.get_account_display()

    account_display.short_description = "account"


class DepartmentProgramAdminForm(forms.ModelForm):
    class Meta:
        model = DepartmentProgram
        fields = ["fy", "ibmIdentifier", "dept_program1", "dept_program2", "dept_program3"]
        widgets = {
            "dept_program1": forms.Textarea(attrs={"cols": "80", "rows": "4"}),
            "dept_program2": forms.Textarea(attrs={"cols": "80", "rows": "4"}),
            "dept_program3": forms.Textarea(attrs={"cols": "80", "rows": "4"}),
        }


@register(DepartmentProgram)
class DepartmentProgramAdmin(ModelAdmin):
    form = DepartmentProgramAdminForm
    list_display = ["ibmIdentifier", "fy", "dept_program1"]
    list_filter = [
        "fy__financialYear",
    ]
    fields = ["fy", "ibmIdentifier", "dept_program1", "dept_program2", "dept_program3"]
    readonly_fields = ["fy", "ibmIdentifier"]
    search_fields = ["ibmIdentifier", "dept_program1", "dept_program2", "dept_program3"]
    actions = [
        export_as_csv_action(
            translations=["financialYear", "ibmIdentifier", "DeptProgram1", "DeptProgram2", "DeptProgram3"],
            fields=["fy", "ibmIdentifier", "dept_program1", "dept_program2", "dept_program3"],
        )
    ]


@register(GLPivDownload)
class GLPivDownloadAdmin(ModelAdmin):
    date_hierarchy = "download_period"
    search_fields = (
        "fy__financialYear",
        "costCentre",
        "account",
        "service",
        "activity",
        "ccName",
        "shortCode",
        "shortCodeName",
        "gLCode",
        "codeID",
    )
    list_display = (
        "gLCode",
        "fy",
        "division",
        "ccName",
        "projectName",
        "ibmdata_link",
        "department_program_link",
    )
    list_filter = ("fy__financialYear", "division", "regionBranch", "costCentre")
    fields = (
        "fy",
        "costCentre",
        "regionBranch",
        "service",
        "project",
        "job",
        "download_period",
        "downloadPeriod",
        "account_display",
        "activity",
        "resource",
        "shortCode",
        "shortCodeName",
        "gLCode",
        "ptdActual",
        "ptdBudget",
        "ytdActual",
        "ytdBudget",
        "fybudget",
        "ytdVariance",
        "ccName",
        "serviceName",
        "activityName",
        "resourceName",
        "projectName",
        "jobName",
        "codeID",
        "resNameNo",
        "actNameNo",
        "projNameNo",
        "division",
        "resourceCategory",
        "wildfire",
        "expenseRevenue",
        "fireActivities",
        "mPRACategory",
    )
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "Download Period",
                "CC",
                "Account",
                "Service",
                "Activity",
                "Resource",
                "Project",
                "Job",
                "Shortcode",
                "Shortcode_Name",
                "GL_Code",
                "PTD_Actual",
                "PTD_Budget",
                "YTD_Actual",
                "YTD_Budget",
                "FY_Budget",
                "YTD_Variance",
                "CC_Name",
                "Service Name",
                "Activity_Name",
                "Resource_Name",
                "Project_Name",
                "Job_Name",
                "Code identifier",
                "ResNmNo",
                "ActNmNo",
                "ProjNmNo",
                "Region/Branch",
                "Division",
                "Resource Category",
                "Wildfire",
                "Exp_Rev",
                "Fire Activities",
                "MPRA Category",
            ],
            fields=[
                "fy",
                "downloadPeriod",
                "costCentre",
                "account",
                "service",
                "activity",
                "resource",
                "project",
                "job",
                "shortCode",
                "shortCodeName",
                "gLCode",
                "ptdActual",
                "ptdBudget",
                "ytdActual",
                "ytdBudget",
                "fybudget",
                "ytdVariance",
                "ccName",
                "serviceName",
                "activityName",
                "resourceName",
                "projectName",
                "jobName",
                "codeID",
                "resNameNo",
                "actNameNo",
                "projNameNo",
                "regionBranch",
                "division",
                "resourceCategory",
                "wildfire",
                "expenseRevenue",
                "fireActivities",
                "mPRACategory",
            ],
        )
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def ibmdata_link(self, obj):
        if obj.ibmdata:
            url = reverse("admin:ibms_ibmdata_change", args=[obj.ibmdata.pk])
            return format_html(f"<a href='{url}'>{obj.ibmdata}</a>")
        else:
            return ""

    ibmdata_link.short_description = "IBM data"

    def department_program_link(self, obj):
        if obj.department_program:
            url = reverse("admin:ibms_departmentprogram_change", args=[obj.department_program.pk])
            return format_html(f"<a href='{url}'>{obj.department_program}</a>")
        else:
            return ""

    department_program_link.short_description = "department program"

    def account_display(self, obj):
        return obj.get_account_display()

    account_display.short_description = "account"


@register(CorporateStrategy)
class CorporateStrategyAdmin(ModelAdmin):
    fields = ["fy", "corporateStrategyNo", "description1", "description2"]
    readonly_fields = ["fy", "corporateStrategyNo"]
    list_display = ["corporateStrategyNo", "fy", "description1"]
    list_filter = ["fy__financialYear"]
    search_fields = ["corporateStrategyNo", "description1", "description2"]
    actions = [
        export_as_csv_action(
            translations=["financialYear", "IBMSCSNo", "IBMSCSDesc1", "IBMSCSDesc2"],
            fields=["fy", "corporateStrategyNo", "description1", "description2"],
        )
    ]


@register(NCStrategicPlan)
class NCStrategicPlanAdmin(ModelAdmin):
    fields = [
        "fy",
        "strategicPlanNo",
        "directionNo",
        "direction",
        "aimNo",
        "aim1",
        "aim2",
        "actionNo",
        "action",
    ]
    readonly_fields = ["fy", "strategicPlanNo"]
    list_filter = ["fy__financialYear"]
    list_display = ["strategicPlanNo", "fy", "directionNo", "direction"]
    search_fields = ["strategicPlanNo", "direction"]
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "StratPlanNo",
                "StratDirNo",
                "StratDir",
                "AimNo",
                "Aim1",
                "Aim2",
                "ActNo",
                "Action",
            ],
            fields=[
                "fy",
                "strategicPlanNo",
                "directionNo",
                "direction",
                "aimNo",
                "aim1",
                "aim2",
                "actionNo",
                "action",
            ],
        )
    ]


class ServicePriorityAdmin(ModelAdmin):
    readonly_fields = ["fy"]
    list_display = [
        "servicePriorityNo",
        "fy",
        "categoryID",
        "strategicPlanNo",
        "corporate_strategy_link",
        "strategic_plan_link",
    ]
    list_filter = ["fy__financialYear", "categoryID"]
    search_fields = ["fy__financialYear", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]

    def corporate_strategy_link(self, obj):
        if obj.corporate_strategy:
            url = reverse("admin:ibms_corporatestrategy_change", args=[obj.corporate_strategy.pk])
            return format_html(f"<a href='{url}'>{obj.corporate_strategy}</a>")
        else:
            return ""

    corporate_strategy_link.short_description = "corporate strategy"

    def strategic_plan_link(self, obj):
        if obj.strategic_plan:
            url = reverse("admin:ibms_ncstrategicplan_change", args=[obj.strategic_plan.pk])
            return format_html(f"<a href='{url}'>{obj.strategic_plan}</a>")
        else:
            return ""

    strategic_plan_link.short_description = "strategic plan"


@register(GeneralServicePriority)
class GeneralServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["description2"]
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Description 1",
                "Description 2",
            ],
            fields=[
                "fy",
                "categoryID",
                "servicePriorityNo",
                "strategicPlanNo",
                "corporateStrategyNo",
                "description",
                "description2",
            ],
        )
    ]


@register(NCServicePriority)
class NCServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + [
        "description",
        "target",
        "action",
        "milestone",
    ]
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "AssetNo",
                "Asset",
                "TargetNo",
                "Target",
                "ActionNo",
                "Action",
                "MileNo",
                "Milestone",
            ],
            fields=[
                "fy",
                "categoryID",
                "servicePriorityNo",
                "strategicPlanNo",
                "corporateStrategyNo",
                "assetNo",
                "asset",
                "targetNo",
                "target",
                "actionNo",
                "action",
                "mileNo",
                "milestone",
            ],
        )
    ]


@register(PVSServicePriority)
class PVSServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["servicePriority1"]
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri",
                "PVSExampleAnnWP",
                "PVSExampleActNo",
            ],
            fields=[
                "fy",
                "categoryID",
                "servicePriorityNo",
                "strategicPlanNo",
                "corporateStrategyNo",
                "description",
                "pvsExampleAnnWP",
                "pvsExampleActNo",
                "servicePriority1",
            ],
        )
    ]


@register(SFMServicePriority)
class SFMServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["regionBranch", "description2"]
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "CategoryID",
                "Region",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri2",
            ],
            fields=[
                "fy",
                "categoryID",
                "regionBranch",
                "servicePriorityNo",
                "strategicPlanNo",
                "corporateStrategyNo",
                "description",
                "description2",
            ],
        )
    ]


@register(ERServicePriority)
class ERServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["classification"]
    # NOTE: The header values and the column order for this export are critical and must not be changed.
    actions = [
        export_as_csv_action(
            translations=[
                "financialYear",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Env Regs Specific Classification",
                "Env Regs Specific Description",
            ],
            fields=[
                "fy",
                "categoryID",
                "servicePriorityNo",
                "strategicPlanNo",
                "corporateStrategyNo",
                "classification",
                "description",
            ],
        )
    ]


# @register(Outcome)
class OutcomeAdmin(ModelAdmin):
    list_display = ["fy", "q1Input"]
    list_filter = ["fy__financialYear"]
    actions = [
        export_as_csv_action(
            translations=["financialYear", "q1Input", "q2Input", "q3Input", "q4Input"],
            fields=["fy", "q1Input", "q2Input", "q3Input", "q4Input"],
        )
    ]


@register(ServicePriorityMapping)
class ServicePriorityMappingAdmin(ModelAdmin):
    list_display = ["costCentreNo", "fy", "wildlifeManagement", "parksManagement", "forestManagement"]
    list_filter = ["fy__financialYear", "costCentreNo"]
    actions = [
        export_as_csv_action(
            translations=["financialYear", "costCentreNo", "wildlifeManagement", "parksManagement", "forestManagement"],
            fields=["fy", "costCentreNo", "wildlifeManagement", "parksManagement", "forestManagement"],
        )
    ]
