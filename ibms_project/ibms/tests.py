from datetime import date

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from mixer.backend.django import mixer

from ibms.models import GLPivDownload, IBMData


class IbmsTestCase(TestCase):
    """Defines fixtures and setup common to all ibms test cases."""

    fixtures = [
        "test-user-data.json",
    ]
    cleans_up_after_itself = True


class IbmsViewsTest(IbmsTestCase):
    """Test the ibms app views load ok."""

    client = Client()

    def test_auth_views_render(self):
        """Test that the login/logout view render correctly"""
        url = reverse("login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.client.login(username="admin", password="test")
        url = reverse("logout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "logged_out.html")

    def test_login_template(self):
        """Test that the login view renders correctly"""
        url = reverse("login")
        response = self.client.get(url)
        # View template shouldn't contain the navbar login URL.
        self.assertNotContains(response, '<a href="/login/">Log in</a>')

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
        self.client.login(username="testuser", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "site_home.html")
        self.assertNotContains(response, '<li id="superuser_upload">')

    def test_ibms_views_render(self):
        """Test that all the IBMS views render"""
        self.client.login(username="admin", password="test")

        for view in [
            "upload",
            "download",
            "reload",
            "code_update",
            "code_update_admin",
            "serviceprioritydata",
            "dataamendment",
        ]:
            url = reverse(view)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_ibms_views_req_auth(self):
        """Test that all the IBMS views will redirect a non-auth'ed user."""
        for view in [
            "site_home",
            "upload",
            "download",
            "reload",
            "code_update",
            "code_update_admin",
            "serviceprioritydata",
            "dataamendment",
        ]:
            url = reverse(view)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_upload_view_redirect(self):
        """Test upload view redirects normal users, but not superusers."""
        self.client.login(username="testuser", password="test")
        url = reverse("upload")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_clearglpivot_view_redirect(self):
        """Test clearglpivot view redirects normal users, but not superusers."""
        self.client.login(username="testuser", password="test")
        url = reverse("clearglpivot")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_code_update_admin_view_redirect(self):
        """Test code_update_admin view redirects normal users, but not superusers."""
        self.client.login(username="testuser", password="test")
        url = reverse("code_update_admin")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ibms_admin_views(self):
        """Test that the Django ibms app admin works"""
        self.client.login(username="admin", password="test")
        url = reverse("admin:ibms_ibmdata_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ibms_ajax_endpoints(self):
        # For this, we need a few dozen dummy records.
        for i in range(20):
            ibmdata = mixer.blend(IBMData)
            mixer.blend(
                GLPivDownload, codeID=ibmdata.ibmIdentifier[0:29], downloadPeriod=date.today().strftime("%d/%m/%Y")
            )

        self.client.login(username="admin", password="test")
        for endpoint in [
            "ajax_ibmdata_budgetarea",
            "ajax_ibmdata_projectsponsor",
            "ajax_ibmdata_service",
            "ajax_glpivdownload_financialyear",
            "ajax_glpivdownload_service",
            "ajax_glpivdownload_costcentre",
            "ajax_glpivdownload_regionbranch",
            "ajax_glpivdownload_division",
            "ajax_mappings",
        ]:
            url = reverse(endpoint)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
