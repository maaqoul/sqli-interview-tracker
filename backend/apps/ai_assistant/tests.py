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
