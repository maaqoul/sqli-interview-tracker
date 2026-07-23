from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.ai_assistant.mock_provider import MockProvider
from apps.ai_assistant.models import AISession, AISessionType
from apps.ai_assistant.parsing import validate_questions
from apps.ai_assistant.rate_limit import reset_ai_rate_limit
from apps.ai_assistant.services import get_ai_service


class AIServiceUnitTests(TestCase):
    def test_mock_generate_questions_shape(self):
        questions = MockProvider().generate_questions(
            job_title="Python Developer",
            level="senior",
            skills=["Django", "Vue"],
            interview_type="technical",
            n=10,
        )
        self.assertGreaterEqual(len(questions), 8)
        self.assertLessEqual(len(questions), 12)
        for q in questions:
            self.assertIn("question", q)
            self.assertIn(q["type"], {"technical", "behavioral"})
            self.assertIn(q["difficulty"], {"easy", "medium", "hard"})

    def test_validate_questions_rejects_short_list(self):
        with self.assertRaises(ValueError):
            validate_questions(
                [{"question": "Only one?", "type": "technical", "difficulty": "easy"}]
            )

    @override_settings(AI_PROVIDER="mock")
    def test_factory_returns_mock(self):
        self.assertIsInstance(get_ai_service(), MockProvider)

    @override_settings(AI_PROVIDER="openai", OPENAI_API_KEY="")
    def test_factory_falls_back_without_openai_key(self):
        self.assertIsInstance(get_ai_service(), MockProvider)


@override_settings(AI_PROVIDER="mock")
class GenerateQuestionsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="recruiter@sqli.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role=Role.RECRUITER,
        )
        reset_ai_rate_limit(self.user)

    def _login(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.user.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_generate_questions_endpoint(self):
        self._login()
        response = self.client.post(
            "/api/ai/generate-questions/",
            {
                "job_title": "Senior Python Developer",
                "level": "senior",
                "skills": ["Django", "PostgreSQL"],
                "interview_type": "technical",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(data["count"], 8)
        self.assertEqual(len(data["questions"]), data["count"])
        self.assertTrue(
            AISession.objects.filter(
                user=self.user,
                type=AISessionType.QUESTIONS,
            ).exists()
        )

    def test_generate_requires_auth(self):
        response = self.client.post(
            "/api/ai/generate-questions/",
            {"job_title": "Dev", "level": "mid"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_limit(self):
        self._login()
        payload = {
            "job_title": "Dev",
            "level": "mid",
            "skills": [],
            "interview_type": "technical",
            "save": False,
        }
        for _ in range(20):
            resp = self.client.post("/api/ai/generate-questions/", payload, format="json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

        blocked = self.client.post("/api/ai/generate-questions/", payload, format="json")
        self.assertEqual(blocked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


@override_settings(AI_PROVIDER="mock")
class SummarizeAndMockAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recruiter = User.objects.create_user(
            email="recruiter2@sqli.com",
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
        from datetime import timedelta

        from django.utils import timezone

        from apps.candidates.models import Candidate, CandidateStatus
        from apps.interviews.models import Interview, InterviewType
        from apps.jobs.models import JobOpening, JobStatus
        from apps.scorecards.models import Scorecard

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
        interview = Interview.objects.create(
            candidate=self.candidate,
            job=self.job,
            type=InterviewType.VIDEO,
            scheduled_at=timezone.now() + timedelta(days=1),
            created_by=self.recruiter,
        )
        interview.interviewers.add(self.interviewer)
        Scorecard.objects.create(
            interview=interview,
            interviewer=self.interviewer,
            overall_rating=4,
            skill_ratings={
                "technical": 4,
                "communication": 3,
                "problem_solving": 4,
                "culture_fit": 3,
                "leadership": 2,
            },
            strengths="Strong Django skills",
            weaknesses="Limited Vue experience",
            recommendation="yes",
        )
        reset_ai_rate_limit(self.recruiter)

    def _login(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.recruiter.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_summarize_feedback(self):
        self._login()
        response = self.client.post(
            "/api/ai/summarize-feedback/",
            {"candidate_id": self.candidate.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("strengths", data)
        self.assertIn("concerns", data)
        self.assertIn("recommendation", data)
        self.assertIn("suggested_next_step", data)
        self.assertEqual(data["scorecard_count"], 1)
        self.assertIn("human decision", data["disclaimer"].lower())
        self.assertTrue(
            AISession.objects.filter(
                user=self.recruiter,
                type=AISessionType.SUMMARY,
                candidate=self.candidate,
            ).exists()
        )

    def test_summarize_missing_candidate(self):
        self._login()
        response = self.client.post(
            "/api/ai/summarize-feedback/",
            {"candidate_id": 99999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mock_interview_flow(self):
        self._login()
        start = self.client.post(
            "/api/ai/mock-interview/",
            {
                "role": "Python Developer",
                "level": "senior",
                "history": [],
                "user_answer": "",
            },
            format="json",
        )
        self.assertEqual(start.status_code, status.HTTP_200_OK)
        start_data = start.json()
        self.assertTrue(start_data["next_question"])
        self.assertFalse(start_data["done"])
        session_id = start_data["session_id"]

        turn = self.client.post(
            "/api/ai/mock-interview/",
            {
                "role": "Python Developer",
                "level": "senior",
                "history": start_data["history"],
                "user_answer": "I enjoy building APIs and mentoring juniors.",
                "session_id": session_id,
            },
            format="json",
        )
        self.assertEqual(turn.status_code, status.HTTP_200_OK)
        turn_data = turn.json()
        self.assertTrue(turn_data["feedback"] or turn_data["next_question"])
        self.assertEqual(turn_data["session_id"], session_id)
        self.assertTrue(
            AISession.objects.filter(id=session_id, type=AISessionType.MOCK).exists()
        )
