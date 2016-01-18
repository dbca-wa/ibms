from django.core.urlresolvers import reverse
from django.test.client import Client
from django_dynamic_fixture import G

from ibms.tests import IbmsTestCase
from sfm.models import (Quarter, SFMMetric, MeasurementType, CostCentre,
                     MeasurementValue)


class SfmViewsTest(IbmsTestCase):
    """Test that sfm application views render.
    """
    client = Client()

    def test_sfm_views_render(self):
        """Test that all the SFM views render.
        """
        self.client.login(username='admin', password='test')

        for view in ['sfmoutcome', 'sfmupload', 'sfmdownload']:
            url = reverse(view)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_sfm_views_req_auth(self):
        """Test that all the sfm views will redirect a non-auth'ed user.
        """
        for view in ['sfmoutcome', 'sfmupload', 'sfmdownload']:
            url = reverse(view)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_sfm_output_report_validation(self):
        """Test sfm form validation errors.
        """
        self.client.login(username='admin', password='test')

        url = reverse('sfmdownload')
        response = self.client.post(url)
        self.assertFormError(
            response, 'form', 'financial_year', 'This field is required.')
        self.assertFormError(
            response, 'form', 'quarter', 'This field is required.')
        self.assertFormError(
            response, 'form', 'cost_centre', 'This field is required.')

    def test_sfm_ajax_endpoints(self):
        """Test sfm JSON endpoints for AJAX requests.
        """
        # For this, we need some dummy records.
        for i in range(10):
            G(Quarter)
            G(SFMMetric)
            G(MeasurementType)
            G(CostCentre)
            G(MeasurementValue)

        self.client.login(username='admin', password='test')
        for endpoint in [
                'ajax_quarter', 'ajax_outcome_financialyear',
                'ajax_sfmmetric_metricid', 'ajax_measurementvalue']:
            url = reverse(endpoint)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
