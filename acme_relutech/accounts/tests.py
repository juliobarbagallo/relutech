from django.test import TestCase

from .models import CustomUser


class CustomUserTestCase(TestCase):
    def test_create_developer_user(self):
        user = CustomUser.objects.create_user(
            email="dev@acme.com", username="devuser", password="devuserpassword"
        )
        self.assertEqual(user.email, "dev@acme.com")
        self.assertEqual(user.username, "devuser")
        self.assertFalse(user.is_admin)

    def test_create_admin_user(self):
        user = CustomUser.objects.create_superuser(
            email="admin@acme.com", username="root", password="rootpassword"
        )
        self.assertEqual(user.email, "admin@acme.com")
        self.assertEqual(user.username, "root")
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
