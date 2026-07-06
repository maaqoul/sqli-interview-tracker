from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User


class UserModelTests(TestCase):
    def test_create_user_with_email_and_role(self):
        user = User.objects.create_user(
            email="recruiter@sqli.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role=Role.RECRUITER,
        )
        self.assertEqual(user.email, "recruiter@sqli.com")
        self.assertEqual(user.role, Role.RECRUITER)
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_email_must_be_unique(self):
        User.objects.create_user(
            email="dup@sqli.com",
            password="testpass123",
            first_name="A",
            last_name="B",
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="dup@sqli.com",
                password="testpass123",
                first_name="C",
                last_name="D",
            )

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@sqli.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, Role.ADMIN)

    def test_user_str_returns_email(self):
        user = User.objects.create_user(
            email="test@sqli.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(str(user), "test@sqli.com")


class JWTAuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(
            email="recruiter@sqli.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role=Role.RECRUITER,
        )

    def test_login_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "recruiter@sqli.com", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_invalid_password_returns_401(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "recruiter@sqli.com", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_email_returns_401(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "nobody@sqli.com", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {"email": "recruiter@sqli.com", "password": "testpass123"},
            format="json",
        )
        refresh_token = login_response.json()["refresh"]

        response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())

    def test_refresh_invalid_token_returns_401(self):
        response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": "invalid-token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
