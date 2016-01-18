from django.conf.urls import patterns, url
from ibms.models import GLPivDownload, IBMData
from ibms.views import (DownloadView, UploadView, ReloadView, CodeUpdateView,
                        ServicePriorityDataView, DataAmendmentView,
                        IbmsModelFieldJSON)

urlpatterns = patterns(
    'ibms.views',
    url(r'^upload/$', UploadView.as_view(), name='upload'),
    url(r'^download/$', DownloadView.as_view(), name='download'),
    url(r'^reload/$', ReloadView.as_view(), name='reload'),
    url(r'^code-update/$', CodeUpdateView.as_view(), name='code_update'),
    url(r'^alternative-form/$', CodeUpdateView.as_view(form_alternative=True)),
    url(r'^service-priority-data/$', ServicePriorityDataView.as_view(),
        name='serviceprioritydata'),
    url(r'^data-amendment/$', DataAmendmentView.as_view(), name='dataamendment'),
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
    url(r'^ajax/ibmdata/budget-area/$',
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname='budgetArea'),
        name='ajax_ibmdata_budgetarea'),
    url(r'^ajax/ibmdata/project-sponsor/$',
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname='projectSponsor'),
        name='ajax_ibmdata_projectsponsor'),
    url(r'^ajax/ibmdata/service/$',
        IbmsModelFieldJSON.as_view(model=IBMData, fieldname='service'),
        name='ajax_ibmdata_service'),
    url(r'^ajax/glpivdownload/financial-year/$',
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='financialYear'),
        name='ajax_glpivdownload_financialyear'),
    url(r'^ajax/glpivdownload/service/$',
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='service'),
        name='ajax_glpivdownload_service'),
    url(r'^ajax/glpivdownload/cost-centre/$',
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='costCentre'),
        name='ajax_glpivdownload_costcentre'),
    url(r'^ajax/glpivdownload/region-branch/$',
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='regionBranch'),
        name='ajax_glpivdownload_regionbranch'),
    url(r'^ajax/glpivdownload/division/$',
        IbmsModelFieldJSON.as_view(model=GLPivDownload, fieldname='division'),
        name='ajax_glpivdownload_division'),
)
