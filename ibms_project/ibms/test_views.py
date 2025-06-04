import os
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from mixer.backend.django import mixer

from ibms.models import GLPivDownload, IBMData
from ibms.tests import IbmsTestCase


class IbmsViewsTest(IbmsTestCase):
    """Test the ibms app views load ok."""

    client = Client()

    def test_homepage_superuser(self):
        """Test homepage view contains required elements for a superuser"""
        url = reverse("site_home")
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "site_home.html")
        self.assertContains(response, 'id="superuser_upload"')

    def test_homepage_user(self):
        """Site homepage view should not contain some elements for a normal user"""
        url = reverse("site_home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "site_home.html")
        self.assertNotContains(response, '<li id="superuser_upload">')

    def test_ibms_views_get(self):
        """Test that all the 'normal user' IBMS views respond"""
        for view in [
            "download",
            "reload",
            "code_update",
            "ibmdata_list",
        ]:
            url = reverse(f"ibms:{view}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_ibms_views_req_auth(self):
        """Test that all the IBMS views will redirect a non-auth'ed user."""
        self.client.logout()
        for view in [
            "upload",
            "download",
            "reload",
            "code_update",
            "code_update_admin",
            "ibmdata_list",
        ]:
            url = reverse(f"ibms:{view}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_upload_view_redirect(self):
        """Test upload view redirects normal users, but not superusers."""
        url = reverse("ibms:upload")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_view_ibmdata_post(self):
        """Test a valid CSV upload for IBM data."""
        url = reverse("ibms:upload")
        test_data = open(os.path.join("ibms_project", "ibms", "test_data", "ibmdata_upload_test.csv"), "rb")
        upload = SimpleUploadedFile("ibmdata_upload.csv", test_data.read())
        resp = self.client.post(url, {"upload_file_type": "IBMData", "upload_file": upload})
        self.assertEqual(resp.status_code, 200)

    def test_clearglpivot_view_redirect(self):
        """Test clearglpivot view redirects normal users, but not superusers."""
        url = reverse("ibms:clearglpivot")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_code_update_admin_view_redirect(self):
        """Test code_update_admin view redirects normal users, but not superusers."""
        url = reverse("ibms:code_update_admin")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ibms_admin_views(self):
        """Test that the Django ibms app admin works"""
        self.client.login(username="admin", password="test")
        # Changelist view.
        url = reverse("admin:ibms_ibmdata_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Change view.
        url = reverse("admin:ibms_ibmdata_change", kwargs={"object_id": self.ibmdata.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ibms_ajax_endpoints(self):
        """Test that the IBMS AJAX endpoints work"""
        for _ in range(20):
            mixer.blend(GLPivDownload, codeID=self.ibmdata.ibmIdentifier[0:29], downloadPeriod=date.today().strftime("%d/%m/%Y"))

        for endpoint in [
            "ajax_glpivdownload_financialyear",
            "ajax_ibmdata_costcentre",
            "ajax_glpivdownload_costcentre",
            "ajax_glpivdownload_regionbranch",
            "ajax_ibmdata_service",
            "ajax_ibmdata_project",
            "ajax_ibmdata_job",
            "ajax_ibmdata_budgetarea",
            "ajax_ibmdata_projectsponsor",
            "ajax_glpivdownload_division",
            "ajax_mappings",
        ]:
            url = reverse(f"ibms:{endpoint}")
            response = self.client.get(url, {"financialYear": self.fy.financialYear})
            self.assertEqual(response.status_code, 200)

    def test_ibms_ibmdata_list_filter(self):
        """Test that the IbmDataList view returns filtered records"""
        url = reverse("ibms:ibmdata_list")
        response = self.client.get(url, {"cost_centre": "999"})
        self.assertContains(response, self.ibmdata.ibmIdentifier)

    def test_ibms_ibmdata_list_rule_budgetarea(self):
        """Test the IbmDataList view business rule: filter out blank budgetArea"""
        ibmdata2 = mixer.blend(IBMData, fy=self.fy, costCentre="999", budgetArea="", activity="AB1", projectSponsor=self.fake.name())
        url = reverse("ibms:ibmdata_list")
        response = self.client.get(url, {"cost_centre": "999"})
        # The new IBMData record shouldn't be in the response.
        self.assertNotContains(response, ibmdata2.ibmIdentifier)
        self.assertContains(response, self.ibmdata.ibmIdentifier)

    def test_ibms_ibmdata_list_rule_dj0(self):
        """Test the IbmDataList view business rule: filter out activity DJ0"""
        ibmdata2 = mixer.blend(IBMData, fy=self.fy, costCentre="999", activity="DJ0", projectSponsor=self.fake.name())
        url = reverse("ibms:ibmdata_list")
        response = self.client.get(url, {"cost_centre": "999"})
        self.assertNotContains(response, ibmdata2.ibmIdentifier)
        self.assertContains(response, self.ibmdata.ibmIdentifier)

    def test_ibms_ibmdata_update_get(self):
        """Test that the IbmDataUpdate view responds"""
        url = reverse("ibms:ibmdata_update", kwargs={"pk": self.ibmdata.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cancel(self):
        """Test the cancelling the IbmDataUpdate view redirects to the list view"""
        url = reverse("ibms:ibmdata_update", kwargs={"pk": self.ibmdata.pk})
        resp = self.client.post(url, {"cancel": "Cancel"})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("ibms:ibmdata_list"))

    def test_ibms_ibmdata_update_post(self):
        """Test that the IbmDataUpdate view responds correctly to a POST request"""
        url = reverse("ibms:ibmdata_update", kwargs={"pk": self.ibmdata.pk})
        response = self.client.post(url, {"budgetArea": "Operations"})
        self.assertEqual(response.status_code, 302)
        ibmdata = IBMData.objects.first()
        self.assertEqual(ibmdata.budgetArea, "Operations")
