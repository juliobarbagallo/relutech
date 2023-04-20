from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from assets.models import Asset
from django.urls import reverse
# from .serializers import AssetSerializer
from assets.serializers import AssetSerializer
from licenses.serializers import LicenseSerializer
from licenses.models import License

class DeveloperAPIViewTests(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username='root',
            email='root@acme.com',
            password='testpass123'
        )
        self.user = CustomUser.objects.create_user(
            username='developer1',
            email='developer1@acme.com',
            password='testpass123'
        )
        self.user_data = {
            'username': 'testacmeuser',
            'email': 'testacmeuser@acme.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_admin': False
        }
        self.url = reverse('api:api_developers')
        self.client = APIClient()

    def test_get_developers_list_authenticated_admin(self):
        """
        Test that authenticated admin user can retrieve a list of developers
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_developers_list_unauthenticated(self):
        """
        Test that unauthenticated user cannot retrieve a list of developers
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_developers_list_authenticated_non_admin(self):
        """
        Test that authenticated non-admin user cannot retrieve a list of developers
        """
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_developers_list_authenticated_admin(self):
        """
        Test that authenticated admin can retrieve a list of developers
        """
        self.client.force_login(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'developer1')

    def test_create_developer_authenticated_admin(self):
        """
        Test that authenticated admin user can create a new developer
        """
        
        self.client.force_login(self.admin_user)
        response = self.client.post(self.url, self.user_data, format='json') 
        # print("RRR: ", response.content.decode())       
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email='testacmeuser@acme.com').exists())


    def test_create_developer_authenticated_non_admin(self):
        """
        Test that authenticated non-admin user cannot create a new developer
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(CustomUser.objects.filter(email='newdeveloper@acme.com').exists())
    
    def test_create_developer_unauthenticated(self):
        """
        Test that unauthenticated user cannot create a new developer
        """
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(CustomUser.objects.filter(email='newdeveloper@acme.com').exists())

    def test_update_developer_authenticated_admin(self):
        """
        Test that authenticated admin user can update an existing developer
        """
        developer = CustomUser.objects.create_user(
            username='testputdev',
            email='testputdev@acme.com',
            password='testpass123'
        )

        self.client.force_login(self.admin_user)
        url = reverse('api:api_developer_detail', kwargs={'pk': developer.id})
        updated_data = {'username': 'updated_developer', 'email': 'updated@test.com', 'is_admin': False}

        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        developer.refresh_from_db()
        self.assertEqual(developer.username, updated_data['username'])
        self.assertEqual(developer.email, updated_data['email'])
        self.assertEqual(developer.is_admin, updated_data['is_admin'])

class AssetViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser', email='testuser@acme.com', password='testpass', is_admin=True)
        self.developer_user = CustomUser.objects.create_user(
            username='developer',
            email='developer@acme.com',
            password='testpass',
            is_admin=False
        )
        self.admin_user = CustomUser.objects.create_superuser(
            username='root',
            email='root@acme.com',
            password='testpass123'
        )
        self.valid_payload = {
            'brand': 'Dell',
            'model': 'Latitude',
            'type': Asset.LAPTOP,
            'developer': self.user.id
        }
        self.invalid_payload = {
            'brand': '',
            'model': 'Latitude',
            'type': Asset.LAPTOP,
            'developer': self.user.id
        }
        self.asset = Asset.objects.create(
            brand='Dell', model='Latitude', type=Asset.LAPTOP, developer=self.user)
        self.developer_asset = Asset.objects.create(
            brand='Dell', model='Latitude', type=Asset.LAPTOP, developer=self.developer_user)

    def test_get_all_assets(self):
        """
        Test that authenticated admin user can retrieve a list of assets.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('api:all_assets'))
        assets = Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_assets_by_developer(self):
        """
        Test that authenticated admin user can retrieve a list of assets by developer
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('api:asset-assignments', kwargs={'pk': self.user.id}))
        assets = Asset.objects.filter(developer=self.user)
        serializer = AssetSerializer(assets, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_assets_unauthorized(self):
        """
        Test that unauthorized user cannot retrieve a list of assets
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('api:all_assets'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_asset_assignment_success(self):
        """
        Test that an authenticated admin user can create an asset assignment for a developer.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'brand': 'Dell',
            'model': 'Latitude',
            'type': Asset.LAPTOP,
        }
        response = self.client.post(reverse('api:asset-assignments', kwargs={'pk': self.developer_user.id}), data=data)
        # print("RRR: ", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        asset = Asset.objects.filter(brand='Dell', model='Latitude', type=Asset.LAPTOP, developer=self.developer_user).first()
        self.assertIsNotNone(asset)

    def test_create_asset_assignment_unauthorized(self):
        """
        Test that an unauthorized user cannot create an asset assignment.
        """
        self.client.force_authenticate(user=None)
        data = {
            'brand': 'Dell',
            'model': 'Latitude',
            'type': Asset.LAPTOP,
        }
        response = self.client.post(reverse('api:asset-assignments', kwargs={'pk': self.developer_user.id}), data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_asset_assignment_developer_not_found(self):
        """
        Test that an asset assignment cannot be created if the developer is not found.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'brand': 'Dell',
            'model': 'Latitude',
            'type': Asset.LAPTOP,
        }
        response = self.client.post(reverse('api:asset-assignments', kwargs={'pk': 123}), data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_asset_assignment_bad_request(self):
        """
        Test that an asset assignment cannot be created with invalid data.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'brand': '',
            'model': 'Latitude',
            'type': Asset.LAPTOP,
        }
        response = self.client.post(reverse('api:asset-assignments', kwargs={'pk': self.developer_user.id}), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_asset_by_admin(self):
        """
        Test that authenticated admin user can delete an asset.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('api:asset-delete', kwargs={'developer_id': self.developer_user.id, 'asset_id': self.developer_asset.id}))
        # print("RRR: ", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_asset_by_unauthorized_user(self):
        """
        Test that unauthorized user cannot delete an asset.
        """
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse('api:asset-delete', kwargs={'developer_id': self.user.id, 'asset_id': self.asset.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_asset(self):
        """
        Test that trying to delete a nonexistent asset returns a 404 status code.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('api:asset-delete', kwargs={'developer_id': self.user.id, 'asset_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_asset_by_non_admin_user(self):
        """
        Test that non-admin user cannot delete an asset.
        """
        non_admin_user = CustomUser.objects.create_user(
            username='nonadmin', email='nonadmin@acme.com', password='testpass', is_admin=False)
        self.client.force_authenticate(user=non_admin_user)
        response = self.client.delete(reverse('api:asset-delete', kwargs={'developer_id': self.user.id, 'asset_id': self.asset.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class LicenseViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username='root',
            email='root@acme.com',
            password='testpass123'
        )
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@acme.com',
            password='testpass'
        )
        self.license = License.objects.create(
            software='Test License',
            developer=self.user
        )
        self.valid_payload = {
            'software': 'New License',            
        }
        self.invalid_payload = {
            'key': '',            
        }

    def test_get_all_licenses(self):
        """
        Test that authenticated admin user can retrieve a list of licenses.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('api:all_licenses'))
        licenses = License.objects.all()
        serializer = LicenseSerializer(licenses, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_licenses_by_developer(self):
        """
        Test that authenticated admin user can retrieve a list of licenses by user
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('api:license-assignments', kwargs={'pk': self.user.id}))
        licenses = License.objects.filter(developer=self.user)
        serializer = LicenseSerializer(licenses, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_licenses_unauthorized(self):
        """
        Test that unauthorized user cannot retrieve a list of licenses
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('api:all_licenses'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_license_success(self):
        """
        Test that an authenticated admin user can create a license.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('api:license-assignments', kwargs={'pk': self.user.id}), data=self.valid_payload)        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        license = License.objects.filter(software='New License', developer=self.user).first()        
        self.assertEqual(license.software, self.valid_payload['software'])


    def test_create_license_unauthorized(self):
        """
        Test that an unauthorized user cannot create a license.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('api:license-assignments', kwargs={'pk': self.user.id}), data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_license_assignment_developer_not_found(self):
        """
        Test that an license assignment cannot be created if the developer is not found.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = self.valid_payload
        response = self.client.post(reverse('api:license-assignments', kwargs={'pk': 123}), data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_license_assignment_bad_request(self):
        """
        Test that an license assignment cannot be created with invalid data.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = self.invalid_payload
        response = self.client.post(reverse('api:license-assignments', kwargs={'pk': self.user.id}), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_license_by_admin(self):
        """
        Test that authenticated admin user can delete a license.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('api:license-delete', kwargs={'developer_id': self.user.id, 'license_id': self.license.id}))
        # print("RRR: ", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_license_by_unauthorized_user(self):
        """
        Test that unauthorized user cannot delete an license.
        """
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse('api:license-delete', kwargs={'developer_id': self.user.id, 'license_id': self.license.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_license(self):
        """
        Test that trying to delete a nonexistent license returns a 404 status code.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('api:license-delete', kwargs={'developer_id': self.user.id, 'license_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_license_by_non_admin_user(self):
        """
        Test that non-admin user cannot delete an license.
        """
        non_admin_user = CustomUser.objects.create_user(
            username='nonadmin', email='nonadmin@acme.com', password='testpass', is_admin=False)
        self.client.force_authenticate(user=non_admin_user)
        response = self.client.delete(reverse('api:license-delete', kwargs={'developer_id': self.user.id, 'license_id': self.license.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)