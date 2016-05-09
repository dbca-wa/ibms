from django.conf.urls import url

from ibms.views import IbmsModelFieldJSON
from sfm.models import Quarter, SFMMetric
from sfm.views import (FMUploadView, FMOutputReport, FMOutputsView,
                       MeasurementValueJSON)

urlpatterns = [
    url(r'fm/$', FMOutputsView.as_view(), name='sfmoutcome'),
    url(r'^fm-upload/$', FMUploadView.as_view(), name='sfmupload'),
    url(r'^fm-download/$', FMOutputReport.as_view(), name='sfmdownload'),
    # AJAX model field endpoints.
    url(r'^ajax/quarter/$', IbmsModelFieldJSON.as_view(
        model=Quarter, fieldname='description', return_pk=True),
        name='ajax_quarter'),
    url(r'^ajax/outcome/financial-year/$', IbmsModelFieldJSON.as_view(
        model=Quarter, fieldname='quarter', return_pk=True),
        name='ajax_outcome_financialyear'),
    url(r'^ajax/sfmmetric/metricid/$', IbmsModelFieldJSON.as_view(
        model=SFMMetric, fieldname='metricID', return_pk=True),
        name='ajax_sfmmetric_metricid'),
    url(r'^ajax/measurementvalue/$', MeasurementValueJSON.as_view(),
        name='ajax_measurementvalue'),
]
