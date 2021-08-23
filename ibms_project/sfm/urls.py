from django.urls import path
from ibms.views import IbmsModelFieldJSON
from sfm.models import Quarter, SFMMetric, CostCentre
from sfm.views import OutputEntry, OutputUpload, OutputReport, MeasurementValueJSON

urlpatterns = [
    path('output-entry/', OutputEntry.as_view(), name='outcome-entry'),
    path('output-upload/', OutputUpload.as_view(), name='output-upload'),
    path('output-report/', OutputReport.as_view(), name='output-report'),
    # AJAX model field endpoints.
    path('ajax/quarter/', IbmsModelFieldJSON.as_view(model=Quarter, fieldname='description', return_pk=True), name='ajax_quarter'),
    path('ajax/outcome/financial-year/', IbmsModelFieldJSON.as_view(model=Quarter, fieldname='quarter', return_pk=True), name='ajax_outcome_financialyear'),
    path('ajax/sfmmetric/metricid/', IbmsModelFieldJSON.as_view(model=SFMMetric, fieldname='metricID', return_pk=True), name='ajax_sfmmetric_metricid'),
    path('ajax/measurementvalue/', MeasurementValueJSON.as_view(), name='ajax_measurementvalue'),
    path('ajax/costcentre/', IbmsModelFieldJSON.as_view(model=CostCentre, fieldname='__str__', return_pk=True), name='ajax_costcentre'),
]
