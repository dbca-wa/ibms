from django.urls import reverse
from django.test.client import Client
from mixer.backend.django import mixer

from ibms.tests import IbmsTestCase
from sfm.models import FinancialYear, Quarter, SFMMetric, MeasurementType, CostCentre, MeasurementValue


class SfmViewsTest(IbmsTestCase):
    """Test that sfm application views render.
    """
    client = Client()

    def test_sfm_views_render(self):
        """Test that all the SFM views render.
        """
        self.client.login(username='admin', password='test')

        for view in ['outcome-entry', 'output-upload', 'output-report']:
            url = reverse(view)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_sfm_views_req_auth(self):
        """Test that all the sfm views will redirect a non-auth'ed user.
        """
        for view in ['outcome-entry', 'output-upload', 'output-report']:
            url = reverse(view)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_sfm_output_report_validation(self):
        """Test sfm form validation errors.
        """
        self.client.login(username='admin', password='test')

        url = reverse('output-report')
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
        mixer.cycle(3).blend(CostCentre)
        mixer.cycle(3).blend(FinancialYear)
        mixer.cycle(3).blend(SFMMetric, financialYear=mixer.SELECT)
        mixer.cycle(3).blend(Quarter, financialYear=mixer.SELECT)
        mixer.cycle(3).blend(MeasurementType)
        mixer.cycle(3).blend(
            MeasurementValue, quarter=mixer.SELECT, sfmMetric=mixer.SELECT,
            measurementType=mixer.SELECT, costCentre=mixer.SELECT)

        self.client.login(username='admin', password='test')
        for endpoint in [
                'ajax_quarter', 'ajax_outcome_financialyear',
                'ajax_sfmmetric_metricid', 'ajax_measurementvalue']:
            url = reverse(endpoint)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
