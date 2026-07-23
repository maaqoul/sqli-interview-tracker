from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.notifications.models import Notification


class NotificationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="notify@sqli.com",
            password="testpass123",
            first_name="No",
            last_name="Tify",
            role=Role.RECRUITER,
        )
        self.other = User.objects.create_user(
            email="other@sqli.com",
            password="testpass123",
            first_name="O",
            last_name="Ther",
            role=Role.INTERVIEWER,
        )
        self.n1 = Notification.objects.create(
            user=self.user,
            title="Interview assigned",
            message="You have an interview",
            link="/my-interviews",
        )
        self.n2 = Notification.objects.create(
            user=self.user,
            title="Stage change",
            message="Candidate moved",
            link="/candidates/1",
            is_read=True,
        )
        Notification.objects.create(
            user=self.other,
            title="Other",
            message="Not yours",
        )

    def _login(self, user=None):
        user = user or self.user
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_list_own_notifications(self):
        self._login()
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data if isinstance(data, list) else data["results"]
        self.assertEqual(len(results), 2)

    def test_unread_count(self):
        self._login()
        response = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_mark_read(self):
        self._login()
        response = self.client.post(f"/api/notifications/{self.n1.id}/mark-read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.n1.refresh_from_db()
        self.assertTrue(self.n1.is_read)

    def test_mark_all_read(self):
        self._login()
        response = self.client.post("/api/notifications/mark-all-read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["updated"], 1)
        self.assertEqual(
            Notification.objects.filter(user=self.user, is_read=False).count(),
            0,
        )

    def test_cannot_mark_others(self):
        self._login()
        other_note = Notification.objects.filter(user=self.other).first()
        response = self.client.post(f"/api/notifications/{other_note.id}/mark-read/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
