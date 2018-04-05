from django.urls import path
from ibms.views import IbmsModelFieldJSON
from sfm.models import Quarter, SFMMetric
from sfm.views import FMUploadView, FMOutputReport, FMOutputsView, MeasurementValueJSON

urlpatterns = [
    path('fm/', FMOutputsView.as_view(), name='sfmoutcome'),
    path('fm-upload/', FMUploadView.as_view(), name='sfmupload'),
    path('fm-download/', FMOutputReport.as_view(), name='sfmdownload'),
    # AJAX model field endpoints.
    path('ajax/quarter/', IbmsModelFieldJSON.as_view(model=Quarter, fieldname='description', return_pk=True), name='ajax_quarter'),
    path('ajax/outcome/financial-year/', IbmsModelFieldJSON.as_view(model=Quarter, fieldname='quarter', return_pk=True), name='ajax_outcome_financialyear'),
    path('ajax/sfmmetric/metricid/', IbmsModelFieldJSON.as_view(model=SFMMetric, fieldname='metricID', return_pk=True), name='ajax_sfmmetric_metricid'),
    path('ajax/measurementvalue/', MeasurementValueJSON.as_view(), name='ajax_measurementvalue'),
]
