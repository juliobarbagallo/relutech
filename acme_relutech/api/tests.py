from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from django.urls import reverse

class DeveloperListCreateAPIViewTests(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.user = CustomUser.objects.create_user(
            username='developer1',
            email='developer1@test.com',
            password='testpass123'
        )
        self.user_data = {
            'username': 'testacmeuser',
            'email': 'testacmeuser@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_admin': False
        }
        self.url = reverse('api:api_developers')
        self.client = APIClient()

    def test_get_developers_list_authenticated_admin(self):
        self.client.force_authenticate(user=self.admin_user)  # authenticate admin user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_developers_list_unauthenticated(self):
        self.client.logout()  # ensure user is not authenticated
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
        self.assertTrue(CustomUser.objects.filter(email='testacmeuser@test.com').exists())


    def test_create_developer_authenticated_non_admin(self):
        """
        Test that authenticated non-admin user cannot create a new developer
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(CustomUser.objects.filter(email='newdeveloper@example.com').exists())
    
    def test_create_developer_unauthenticated(self):
        """
        Test that unauthenticated user cannot create a new developer
        """
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(CustomUser.objects.filter(email='newdeveloper@example.com').exists())

    def test_update_developer_authenticated_admin(self):
        """
        Test that authenticated admin user can update an existing developer
        """
        developer = CustomUser.objects.create_user(
            username='testputdev',
            email='testputdev@test.com',
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

