from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import License


class LicenseTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testwithlicense@acme.com",
            username="testwithlicense",
            password="testpass",
        )
        self.license = License.objects.create(
            software="Microsoft Office", developer=self.user
        )

    def test_license_created(self):
        """Test that a License instance is created properly"""
        license_count = License.objects.count()
        self.assertEqual(license_count, 1)

    def test_developer_licenses(self):
        """Test that the developer has a License"""
        licenses = License.objects.filter(developer=self.user)
        self.assertEqual(licenses.count(), 1)

    def test_license_software(self):
        """Test that the license software is correct"""
        licenses = License.objects.filter(developer=self.user)
        for license in licenses:
            self.assertEqual(license.software, "Microsoft Office")
