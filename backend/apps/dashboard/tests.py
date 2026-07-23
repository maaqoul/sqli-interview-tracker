from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.candidates.models import (
    ActivityActionType,
    Candidate,
    CandidateActivity,
    CandidateStatus,
)
from apps.interviews.models import Interview, InterviewType
from apps.jobs.models import JobOpening, JobStatus


class DashboardAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="dash@sqli.com",
            password="testpass123",
            first_name="Dash",
            last_name="Board",
            role=Role.RECRUITER,
        )
        self.job = JobOpening.objects.create(
            title="Python Dev",
            department="Engineering",
            location="Paris",
            level="mid",
            description="Build things.",
            status=JobStatus.OPEN,
            created_by=self.user,
        )
        stage = self.job.pipeline_stages.get(order=1)
        self.candidate = Candidate.objects.create(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            job=self.job,
            current_stage=stage,
            status=CandidateStatus.ACTIVE,
        )
        CandidateActivity.objects.create(
            candidate=self.candidate,
            user=self.user,
            action_type=ActivityActionType.CREATED,
            description="Candidate added",
        )
        Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.VIDEO,
            scheduled_at=timezone.now() + timedelta(days=1),
            created_by=self.user,
        )

    def _login(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.user.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_stats(self):
        self._login()
        response = self.client.get("/api/dashboard/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["open_jobs"], 1)
        self.assertEqual(data["total_candidates"], 1)
        self.assertGreaterEqual(data["interviews_this_week"], 1)
        self.assertIn("ai_usage", data)
        self.assertIn("upcoming_interviews", data)

    def test_funnel(self):
        self._login()
        response = self.client.get("/api/dashboard/funnel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(any(row["stage"] == "Applied" and row["count"] >= 1 for row in data))

    def test_activity(self):
        self._login()
        response = self.client.get("/api/dashboard/activity/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["candidate_name"], "Ada Lovelace")

    def test_requires_auth(self):
        response = self.client.get("/api/dashboard/stats/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
