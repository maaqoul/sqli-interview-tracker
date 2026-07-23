from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.candidates.models import ActivityActionType, Candidate, CandidateActivity, CandidateStatus
from apps.interviews.models import Interview, InterviewStatus, InterviewType
from apps.jobs.models import JobOpening, JobStatus
from apps.notifications.models import Notification


class InterviewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.other_interviewer = User.objects.create_user(
            email="other@sqli.com",
            password="testpass123",
            first_name="Tom",
            last_name="Brown",
            role=Role.INTERVIEWER,
        )
        self.job = JobOpening.objects.create(
            title="Senior Python Developer",
            department="Engineering",
            location="Paris",
            level="senior",
            description="Build APIs.",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self.candidate = Candidate.objects.create(
            first_name="Marie",
            last_name="Martin",
            email="marie@example.com",
            job=self.job,
            current_stage=self.job.pipeline_stages.get(order=1),
            status=CandidateStatus.ACTIVE,
        )
        self.scheduled_at = timezone.now() + timedelta(days=2)
        self.payload = {
            "candidate": self.candidate.id,
            "job": self.job.id,
            "type": InterviewType.VIDEO,
            "scheduled_at": self.scheduled_at.isoformat(),
            "duration_min": 60,
            "location": "",
            "video_link": "https://meet.example.com/abc",
            "status": InterviewStatus.SCHEDULED,
            "interviewer_ids": [self.interviewer.id],
        }

    def _login(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_recruiter_can_create_interview(self):
        self._login(self.recruiter)
        response = self.client.post("/api/interviews/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["type"], "video")
        self.assertEqual(data["candidate_name"], "Marie Martin")
        self.assertEqual(data["interviewer_ids"], [self.interviewer.id])
        self.assertEqual(data["created_by"], self.recruiter.id)

    def test_create_notifies_interviewers(self):
        self._login(self.recruiter)
        response = self.client.post("/api/interviews/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notes = Notification.objects.filter(user=self.interviewer)
        self.assertEqual(notes.count(), 2)
        titles = set(notes.values_list("title", flat=True))
        self.assertIn("Interview assigned", titles)
        self.assertIn("Scorecard due", titles)

    def test_create_logs_candidate_activity(self):
        self._login(self.recruiter)
        response = self.client.post("/api/interviews/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        activity = CandidateActivity.objects.filter(
            candidate=self.candidate,
            action_type=ActivityActionType.INTERVIEW_SCHEDULED,
        )
        self.assertEqual(activity.count(), 1)

    def test_interviewer_cannot_create_interview(self):
        self._login(self.interviewer)
        response = self.client.post("/api/interviews/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_interviewer_sees_only_assigned_interviews(self):
        mine = Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.PHONE,
            scheduled_at=self.scheduled_at,
            created_by=self.recruiter,
        )
        mine.interviewers.add(self.interviewer)

        other = Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.ONSITE,
            scheduled_at=self.scheduled_at + timedelta(days=1),
            created_by=self.recruiter,
        )
        other.interviewers.add(self.other_interviewer)

        self._login(self.interviewer)
        response = self.client.get("/api/interviews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.json()["results"]}
        self.assertIn(mine.id, ids)
        self.assertNotIn(other.id, ids)

    def test_recruiter_sees_all_interviews(self):
        Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.PHONE,
            scheduled_at=self.scheduled_at,
            created_by=self.recruiter,
        )
        self._login(self.recruiter)
        response = self.client.get("/api/interviews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_filter_by_status(self):
        Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.PHONE,
            scheduled_at=self.scheduled_at,
            status=InterviewStatus.SCHEDULED,
            created_by=self.recruiter,
        )
        Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.VIDEO,
            scheduled_at=self.scheduled_at + timedelta(hours=2),
            status=InterviewStatus.CANCELLED,
            created_by=self.recruiter,
        )
        self._login(self.recruiter)
        response = self.client.get("/api/interviews/?status=scheduled")
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["status"], "scheduled")

    def test_filter_by_interviewer(self):
        interview = Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.PHONE,
            scheduled_at=self.scheduled_at,
            created_by=self.recruiter,
        )
        interview.interviewers.add(self.interviewer)
        self._login(self.recruiter)
        response = self.client.get(f"/api/interviews/?interviewer={self.interviewer.id}")
        self.assertEqual(response.json()["count"], 1)

    def test_filter_by_date_range(self):
        Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.PHONE,
            scheduled_at=timezone.now() + timedelta(days=1),
            created_by=self.recruiter,
        )
        Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.VIDEO,
            scheduled_at=timezone.now() + timedelta(days=10),
            created_by=self.recruiter,
        )
        self._login(self.recruiter)
        start = (timezone.now()).date().isoformat()
        end = (timezone.now() + timedelta(days=3)).date().isoformat()
        response = self.client.get(f"/api/interviews/?date_from={start}&date_to={end}")
        self.assertEqual(response.json()["count"], 1)

    def test_job_must_match_candidate(self):
        other_job = JobOpening.objects.create(
            title="UX Designer",
            department="Design",
            location="Lyon",
            level="mid",
            description="Design",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self._login(self.recruiter)
        payload = {**self.payload, "job": other_job.id}
        response = self.client.post("/api/interviews/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_adds_interviewer_and_notifies(self):
        interview = Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.PHONE,
            scheduled_at=self.scheduled_at,
            created_by=self.recruiter,
        )
        interview.interviewers.add(self.interviewer)
        self._login(self.recruiter)
        response = self.client.patch(
            f"/api/interviews/{interview.id}/",
            {"interviewer_ids": [self.interviewer.id, self.other_interviewer.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Notification.objects.filter(user=self.other_interviewer).count(),
            2,
        )
        self.assertEqual(
            Notification.objects.filter(user=self.interviewer).count(),
            0,
        )

    def test_unauthenticated_returns_401(self):
        response = self.client.get("/api/interviews/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
