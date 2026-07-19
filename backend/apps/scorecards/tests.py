from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.candidates.models import ActivityActionType, Candidate, CandidateActivity, CandidateStatus
from apps.interviews.models import Interview, InterviewStatus, InterviewType
from apps.jobs.models import JobOpening, JobStatus
from apps.scorecards.models import Scorecard


class ScorecardAPITests(TestCase):
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
        self.interview = Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.VIDEO,
            scheduled_at=timezone.now() + timedelta(days=1),
            created_by=self.recruiter,
        )
        self.interview.interviewers.add(self.interviewer)
        self.payload = {
            "interview": self.interview.id,
            "overall_rating": 4,
            "skill_ratings": {
                "technical": 4,
                "communication": 3,
                "problem_solving": 4,
                "culture_fit": 3,
                "leadership": 2,
            },
            "strengths": "Strong Django skills",
            "weaknesses": "Limited Vue",
            "recommendation": "yes",
            "private_notes": "Secret recruiter note",
        }

    def _login(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_interviewer_can_submit_scorecard(self):
        self._login(self.interviewer)
        response = self.client.post("/api/scorecards/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["overall_rating"], 4)
        self.assertEqual(data["interviewer"], self.interviewer.id)
        self.assertNotIn("private_notes", data)

        self.interview.refresh_from_db()
        self.assertEqual(self.interview.status, InterviewStatus.COMPLETED)

    def test_unique_scorecard_per_interviewer(self):
        self._login(self.interviewer)
        first = self.client.post("/api/scorecards/", self.payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post("/api/scorecards/", self.payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unassigned_interviewer_cannot_submit(self):
        self._login(self.other_interviewer)
        response = self.client.post("/api/scorecards/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recruiter_sees_private_notes(self):
        Scorecard.objects.create(
            interview=self.interview,
            interviewer=self.interviewer,
            overall_rating=4,
            skill_ratings=self.payload["skill_ratings"],
            recommendation="yes",
            private_notes="Secret",
        )
        self._login(self.recruiter)
        response = self.client.get(f"/api/scorecards/?interview_id={self.interview.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        self.assertEqual(results[0]["private_notes"], "Secret")

    def test_interviewer_list_hides_others_scorecards(self):
        Scorecard.objects.create(
            interview=self.interview,
            interviewer=self.interviewer,
            overall_rating=4,
            skill_ratings=self.payload["skill_ratings"],
            recommendation="yes",
            private_notes="Secret",
        )
        self.interview.interviewers.add(self.other_interviewer)
        self._login(self.other_interviewer)
        response = self.client.get("/api/scorecards/")
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        self.assertEqual(len(results), 0)

    def test_submit_logs_candidate_activity(self):
        self._login(self.interviewer)
        self.client.post("/api/scorecards/", self.payload, format="json")
        self.assertTrue(
            CandidateActivity.objects.filter(
                candidate=self.candidate,
                action_type=ActivityActionType.SCORECARD_SUBMITTED,
            ).exists()
        )

    def test_filter_by_candidate_id(self):
        Scorecard.objects.create(
            interview=self.interview,
            interviewer=self.interviewer,
            overall_rating=5,
            skill_ratings=self.payload["skill_ratings"],
            recommendation="strong_yes",
        )
        self._login(self.recruiter)
        response = self.client.get(f"/api/scorecards/?candidate_id={self.candidate.id}")
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        self.assertEqual(len(results), 1)

    def test_summary_aggregate(self):
        Scorecard.objects.create(
            interview=self.interview,
            interviewer=self.interviewer,
            overall_rating=4,
            skill_ratings=self.payload["skill_ratings"],
            recommendation="yes",
        )
        Scorecard.objects.create(
            interview=self.interview,
            interviewer=self.other_interviewer,
            overall_rating=2,
            skill_ratings={
                "technical": 2,
                "communication": 2,
                "problem_solving": 2,
                "culture_fit": 2,
                "leadership": 2,
            },
            recommendation="no",
        )
        self.interview.interviewers.add(self.other_interviewer)

        self._login(self.recruiter)
        response = self.client.get(
            f"/api/scorecards/summary/?candidate_id={self.candidate.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["average_overall"], 3.0)
        self.assertEqual(data["yes_count"], 1)
        self.assertEqual(data["consensus_label"], "1/2 recommend Yes")
        self.assertEqual(data["average_skills"]["technical"], 3.0)

    def test_summary_requires_candidate_id(self):
        self._login(self.recruiter)
        response = self.client.get("/api/scorecards/summary/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
