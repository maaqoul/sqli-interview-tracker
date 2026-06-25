from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.accounts.models import Role, User
from apps.accounts.permissions import IsAdmin, IsRecruiter


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


class _FakeJobCreateView(APIView):
    permission_classes = [IsRecruiter]

    def post(self, request):
        return Response({"created": True}, status=status.HTTP_201_CREATED)


class _FakeCandidateDeleteView(APIView):
    permission_classes = [IsRecruiter]

    def delete(self, request, pk):
        return Response(status=status.HTTP_204_NO_CONTENT)


class RBACPermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.recruiter = User.objects.create_user(
            email="recruiter@sqli.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role=Role.RECRUITER,
        )
        self.interviewer = User.objects.create_user(
            email="interviewer@sqli.com",
            password="testpass123",
            first_name="Sara",
            last_name="Lee",
            role=Role.INTERVIEWER,
        )
        self.admin = User.objects.create_superuser(
            email="admin@sqli.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
        )

    def test_recruiter_can_create_job(self):
        request = self.factory.post("/api/jobs/")
        force_authenticate(request, user=self.recruiter)
        response = _FakeJobCreateView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_interviewer_cannot_create_job(self):
        request = self.factory.post("/api/jobs/")
        force_authenticate(request, user=self.interviewer)
        response = _FakeJobCreateView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_interviewer_cannot_delete_candidate(self):
        request = self.factory.delete("/api/candidates/1/")
        force_authenticate(request, user=self.interviewer)
        response = _FakeCandidateDeleteView.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recruiter_can_delete_candidate(self):
        request = self.factory.delete("/api/candidates/1/")
        force_authenticate(request, user=self.recruiter)
        response = _FakeCandidateDeleteView.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_create_job(self):
        request = self.factory.post("/api/jobs/")
        force_authenticate(request, user=self.admin)
        response = _FakeJobCreateView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_is_admin_allows_only_admin(self):
        perm = IsAdmin()

        recruiter_http_request = self.factory.get("/")
        force_authenticate(recruiter_http_request, user=self.recruiter)
        self.assertFalse(perm.has_permission(Request(recruiter_http_request), None))

        admin_http_request = self.factory.get("/")
        force_authenticate(admin_http_request, user=self.admin)
        self.assertTrue(perm.has_permission(Request(admin_http_request), None))


class AuthExtrasAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recruiter = User.objects.create_user(
            email="recruiter@sqli.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role=Role.RECRUITER,
        )
        self.admin = User.objects.create_superuser(
            email="admin@sqli.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
        )

    def test_me_returns_current_user(self):
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["email"], "recruiter@sqli.com")
        self.assertEqual(data["role"], Role.RECRUITER)
        self.assertEqual(data["first_name"], "Jean")
        self.assertNotIn("password", data)

    def test_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_register_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "new@sqli.com",
                "password": "newpass123",
                "first_name": "New",
                "last_name": "User",
                "role": Role.INTERVIEWER,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@sqli.com").exists())

    def test_recruiter_cannot_register_user(self):
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "blocked@sqli.com",
                "password": "newpass123",
                "first_name": "Blocked",
                "last_name": "User",
                "role": Role.INTERVIEWER,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.post(
            "/api/auth/change-password/",
            {
                "current_password": "testpass123",
                "new_password": "newpass456",
                "confirm_password": "newpass456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recruiter.refresh_from_db()
        self.assertTrue(self.recruiter.check_password("newpass456"))

    def test_change_password_wrong_current_password(self):
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.post(
            "/api/auth/change-password/",
            {
                "current_password": "wrong",
                "new_password": "newpass456",
                "confirm_password": "newpass456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.post(
            "/api/auth/change-password/",
            {
                "current_password": "testpass123",
                "new_password": "newpass456",
                "confirm_password": "different",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
