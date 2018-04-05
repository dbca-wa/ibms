from django.urls import path
from ibms.models import GLPivDownload, IBMData
from ibms.views import (DownloadView, UploadView, ReloadView, CodeUpdateView,
                        ServicePriorityDataView, DataAmendmentView,
                        IbmsModelFieldJSON)

urlpatterns = [
    path('upload/', UploadView.as_view(), name='upload'),
    path('download/', DownloadView.as_view(), name='download'),
    path('reload/', ReloadView.as_view(), name='reload'),
    path('code-update/', CodeUpdateView.as_view(), name='code_update'),
    path('service-priority-data/', ServicePriorityDataView.as_view(), name='serviceprioritydata'),
    path('data-amendment/', DataAmendmentView.as_view(), name='dataamendment'),
    # AJAX model field endpoints.
    # Note to future self: these views return JSON data suitable for insert
    # into form select lists. In some cases, the background query requires text
    # values for the lookup, and in other cases it requires primary keys.
    # The view can return all unique values, or can be further filtered by
    # query parameters on the GET (e.g. filter by financialYear field).
    # In each URL, we define the model and the field value to return as a list
    # of tuples, serialised to JSON.
    # Review the IbmsModelFieldJSON view for further details.
    # 2nd note to future self: you have already considered refactoring this
    # using django-rest-framework, etc. Do not bother - this works fine.
    path('ajax/ibmdata/budget-area/', IbmsModelFieldJSON.as_view(model=IBMData, fieldname='budgetArea'), name='ajax_ibmdata_budgetarea'),
    path('ajax/ibmdata/project-sponsor/', IbmsModelFieldJSON.as_view(model=IBMData, fieldname='projectSponsor'), name='ajax_ibmdata_projectsponsor'),
    path('ajax/ibmdata/service/', IbmsModelFieldJSON.as_view(model=IBMData, fieldname='service'), name='ajax_ibmdata_service'),
    path('ajax/glpivdownload/financial-year/', IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='financialYear'), name='ajax_glpivdownload_financialyear'),
    path('ajax/glpivdownload/service/', IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='service'), name='ajax_glpivdownload_service'),
    path('ajax/glpivdownload/cost-centre/', IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='costCentre'), name='ajax_glpivdownload_costcentre'),
    path('ajax/glpivdownload/region-branch/', IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='regionBranch'), name='ajax_glpivdownload_regionbranch'),
    path('ajax/glpivdownload/division/', IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='division'), name='ajax_glpivdownload_division'),
]
