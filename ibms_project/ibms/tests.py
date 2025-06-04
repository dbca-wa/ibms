from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker
from mixer.backend.django import mixer

from ibms.models import FinancialYear, IBMData


class IbmsTestCase(TestCase):
    """Defines fixtures and setup common to all ibms test cases."""

    def setUp(self):
        self.fake = Faker()
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            username="admin",
            password="test",
            email=self.fake.email(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="test",
            email=self.fake.email(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
        )
        self.user.save()
        self.fy = mixer.blend(FinancialYear, financialYear="2024/25")
        self.ibmdata = mixer.blend(
            IBMData,
            fy=self.fy,
            costCentre="999",
            budgetArea="Admin",
            activity="AA1",
            projectSponsor=self.fake.name(),
        )
        self.client.login(username="testuser", password="test")
