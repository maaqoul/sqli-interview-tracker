from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.core.management.commands.seed_demo import DEMO_PASSWORD
from apps.interviews.models import Interview
from apps.jobs.models import JobOpening
from apps.scorecards.models import Scorecard


class SeedDemoCommandTests(TestCase):
    def test_seed_demo_creates_required_counts(self):
        out = StringIO()
        call_command("seed_demo", stdout=out)

        self.assertEqual(User.objects.filter(role=Role.ADMIN, email="admin@sqli.com").count(), 1)
        self.assertEqual(
            User.objects.filter(role=Role.RECRUITER, email__endswith="@sqli.com").count(),
            2,
        )
        self.assertEqual(
            User.objects.filter(role=Role.INTERVIEWER, email__endswith="@sqli.com").count(),
            3,
        )
        self.assertEqual(JobOpening.objects.filter(title__in=[
            "Senior Python Developer",
            "Frontend Vue Engineer",
            "UX Designer",
        ]).count(), 3)
        self.assertEqual(Candidate.objects.filter(email__startswith="candidate").count(), 15)
        self.assertEqual(Interview.objects.count(), 8)
        self.assertEqual(Scorecard.objects.count(), 5)

        admin = User.objects.get(email="admin@sqli.com")
        self.assertTrue(admin.check_password(DEMO_PASSWORD))
        self.assertIn("Demo data ready", out.getvalue())
        self.assertIn(DEMO_PASSWORD, out.getvalue())

    def test_seed_demo_is_idempotent(self):
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(Candidate.objects.filter(email__startswith="candidate").count(), 15)
        self.assertEqual(Interview.objects.count(), 8)
        self.assertEqual(Scorecard.objects.count(), 5)
