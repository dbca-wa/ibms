from django.urls import path

from ibms.models import GLPivDownload, IBMData, ServicePriorityMapping
from ibms.views import (
    ClearGLPivotView,
    CodeUpdateAdminView,
    CodeUpdateView,
    DownloadEnhancedView,
    DownloadView,
    IbmDataList,
    IbmDataUpdate,
    IbmsModelFieldJSON,
    ReloadView,
    ServicePriorityMappingJSON,
    UploadView,
)

app_name = "ibms"
urlpatterns = [
    path("upload/", UploadView.as_view(), name="upload"),
    path("download/", DownloadView.as_view(), name="download"),
    path("download-enhanced/", DownloadEnhancedView.as_view(), name="download_enhanced"),
    path("reload/", ReloadView.as_view(), name="reload"),
    path("code-update/", CodeUpdateView.as_view(), name="code_update"),
    path("code-update-admin/", CodeUpdateAdminView.as_view(), name="code_update_admin"),
    path("data-amendment/", IbmDataList.as_view(), name="ibmdata_list"),
    path("data-amendment/<int:pk>/", IbmDataUpdate.as_view(), name="ibmdata_update"),
    path("clear-gl-pivot/", ClearGLPivotView.as_view(), name="clearglpivot"),
    # AJAX model field endpoints.
    # Note to future self: these views return JSON data suitable for insert
    # into form select lists. In some cases, the background query requires text
    # values for the lookup, and in other cases it requires primary keys.
    # The view can return all unique values, or can be further filtered by
    # query parameters on the GET (e.g. filter by fy field).
    # In each URL, we define the model and the field value to return as a list
    # of tuples, serialised to JSON.
    # Review the IbmsModelFieldJSON view for further details.
    path(
        "ajax/glpivdownload/financial-year/",
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname="fy"),
        name="ajax_glpivdownload_financialyear",
    ),
    path(
        "ajax/glpivdownload/cost-centre/",
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname="costCentre"),
        name="ajax_ibmdata_costcentre",
    ),
    path(
        "ajax/glpivdownload/cost-centre/",
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname="costCentre"),
        name="ajax_glpivdownload_costcentre",
    ),
    path(
        "ajax/glpivdownload/region-branch/",
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname="regionBranch"),
        name="ajax_glpivdownload_regionbranch",
    ),
    path(
        "ajax/ibmdata/service/",
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname="service"),
        name="ajax_ibmdata_service",
    ),
    path(
        "ajax/ibmdata/project/",
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname="project"),
        name="ajax_ibmdata_project",
    ),
    path(
        "ajax/ibmdata/job/",
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname="job"),
        name="ajax_ibmdata_job",
    ),
    path(
        "ajax/ibmdata/budget-area/",
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname="budgetArea"),
        name="ajax_ibmdata_budgetarea",
    ),
    path(
        "ajax/ibmdata/project-sponsor/",
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname="projectSponsor"),
        name="ajax_ibmdata_projectsponsor",
    ),
    path(
        "ajax/glpivdownload/division/",
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname="division"),
        name="ajax_glpivdownload_division",
    ),
    path(
        "ajax/mappings",
        ServicePriorityMappingJSON.as_view(model=ServicePriorityMapping, fieldname="wildlifeManagement, parksManagement, forestManagement"),
        name="ajax_mappings",
    ),
]
