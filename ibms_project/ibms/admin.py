import csv

from django.contrib.admin import ModelAdmin, register
from django.http import HttpResponse
from reversion.admin import VersionAdmin

from .models import (
    CorporateStrategy,
    ERServicePriority,
    GeneralServicePriority,
    GLPivDownload,
    IBMData,
    NCServicePriority,
    NCStrategicPlan,
    Outcomes,
    PVSServicePriority,
    ServicePriorityMappings,
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
    list_display = ("ibmIdentifier", "fy", "budgetArea", "modified", "modifier")
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
    list_display = ("fy", "costCentre", "account", "service", "activity", "ccName")
    list_filter = ("fy__financialYear", "division", "regionBranch", "costCentre")
    actions = [
        export_as_csv_action(
            translations=[
                "id",
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
                "id",
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


@register(CorporateStrategy)
class CorporateStrategyAdmin(ModelAdmin):
    list_display = ["fy", "corporateStrategyNo", "description1"]
    list_filter = ["fy__financialYear"]
    search_fields = ["corporateStrategyNo", "description1"]
    actions = [
        export_as_csv_action(
            translations=["id", "financialYear", "IBMSCSNo", "IBMSCSDesc1", "IBMSCSDesc2"],
            fields=["id", "fy", "corporateStrategyNo", "description1", "description2"],
        )
    ]


@register(GeneralServicePriority)
class GeneralServicePriorityAdmin(ModelAdmin):
    list_display = ["fy", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]
    list_filter = ["fy__financialYear"]
    search_fields = ["fy__financialYear", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]
    actions = [
        export_as_csv_action(
            translations=[
                "id",
                "financialYear",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Description 1",
                "Description 2",
            ],
            fields=[
                "id",
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
class NCServicePriorityAdmin(ModelAdmin):
    list_display = ["fy", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]
    list_filter = ["fy__financialYear", "categoryID"]
    search_fields = [
        "fy__financialYear",
        "categoryID",
        "servicePriorityNo",
        "strategicPlanNo",
        "corporateStrategyNo",
        "description",
        "target",
        "action",
        "milestone",
    ]
    actions = [
        export_as_csv_action(
            translations=[
                "id",
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
                "id",
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
class PVSServicePriorityAdmin(ModelAdmin):
    list_display = ["fy", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]
    list_filter = ["fy__financialYear"]
    search_fields = ["fy__financialYear", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]
    actions = [
        export_as_csv_action(
            translations=[
                "id",
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
                "id",
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
class SFMServicePriorityAdmin(ModelAdmin):
    list_display = ["fy", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]
    list_filter = ["fy__financialYear"]
    actions = [
        export_as_csv_action(
            translations=[
                "id",
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
                "id",
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
class ERServicePriorityAdmin(ModelAdmin):
    list_display = ["fy", "categoryID", "servicePriorityNo", "strategicPlanNo", "corporateStrategyNo"]
    list_filter = ["fy__financialYear"]
    actions = [
        export_as_csv_action(
            translations=[
                "id",
                "financialYear",
                "categoryID",
                "servicePriorityNo",
                "strategicPlanNo",
                "corporateStrategyNo",
                "description",
                "pvsExampleAnnWP",
                "pvsExampleActNo",
                "classification",
            ],
            fields=[
                "id",
                "fy",
                "categoryID",
                "servicePriorityNo",
                "strategicPlanNo",
                "corporateStrategyNo",
                "description",
                "pvsExampleAnnWP",
                "pvsExampleActNo",
                "classification",
            ],
        )
    ]


@register(NCStrategicPlan)
class NCStrategicPlanAdmin(ModelAdmin):
    list_filter = ["fy__financialYear"]
    list_display = ["fy", "strategicPlanNo", "directionNo", "direction"]
    search_fields = ["strategicPlanNo", "direction"]
    actions = [
        export_as_csv_action(
            translations=[
                "id",
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
                "id",
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


@register(Outcomes)
class OutcomesAdmin(ModelAdmin):
    list_display = ["fy", "q1Input"]
    list_filter = ["fy__financialYear"]
    actions = [
        export_as_csv_action(
            translations=["id", "financialYear", "q1Input", "q2Input", "q3Input", "q4Input"],
            fields=["id", "fy", "q1Input", "q2Input", "q3Input", "q4Input"],
        )
    ]


@register(ServicePriorityMappings)
class ServicePriorityMappings(ModelAdmin):
    list_display = ["costCentreNo", "fy", "wildlifeManagement", "parksManagement", "forestManagement"]
    list_filter = ["fy__financialYear", "costCentreNo"]
    actions = [
        export_as_csv_action(
            translations=["financialYear", "costCentreNo", "wildlifeManagement", "parksManagement", "forestManagement"],
            fields=["fy", "costCentreNo", "wildlifeManagement", "parksManagement", "forestManagement"],
        )
    ]
