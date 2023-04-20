from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Asset


class AssetTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testwithasset@acme.com",
            username="testwithasset",
            password="testpass",
        )
        self.asset = Asset.objects.create(
            brand="Dell", model="Latitude", type=Asset.LAPTOP, developer=self.user
        )

    def test_asset_created(self):
        """Test that an Asset instance is created properly"""
        asset_count = Asset.objects.count()
        self.assertEqual(asset_count, 1)

    def test_developer_assets(self):
        """Test that the developer has an Asset"""
        assets = Asset.objects.filter(developer=self.user)
        self.assertEqual(assets.count(), 1)

    def test_developer_name(self):
        """Test that the developer name is correct"""
        assets = Asset.objects.filter(developer=self.user)
        for asset in assets:
            self.assertEqual(asset.developer.username, "testwithasset")
