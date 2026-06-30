from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.jobs.constants import DEFAULT_PIPELINE_STAGES
from apps.jobs.models import JobOpening, JobStatus, PipelineStage
from apps.jobs.services import copy_default_stages_to_job, seed_default_pipeline_stages


class JobOpeningAPITests(TestCase):
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
        self.job_payload = {
            "title": "Senior Python Developer",
            "department": "Engineering",
            "location": "Paris",
            "level": "senior",
            "description": "Build interview tracker APIs.",
            "skills": ["Python", "Django", "DRF"],
            "status": "open",
        }

    def _login(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_recruiter_can_create_job(self):
        self._login(self.recruiter)
        response = self.client.post("/api/jobs/", self.job_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], "Senior Python Developer")
        self.assertEqual(response.json()["created_by"], self.recruiter.id)
        self.assertEqual(response.json()["created_by_name"], "Jean Dupont")

    def test_interviewer_cannot_create_job(self):
        self._login(self.interviewer)
        response = self.client.post("/api/jobs/", self.job_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_jobs_is_paginated(self):
        JobOpening.objects.create(
            title="Backend Developer",
            department="Engineering",
            location="Lyon",
            level="mid",
            description="API work",
            skills=["Python"],
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self._login(self.interviewer)
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["count"], 1)

    def test_filter_jobs_by_status(self):
        JobOpening.objects.create(
            title="Open Role",
            department="Engineering",
            location="Paris",
            level="senior",
            description="Open job",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        JobOpening.objects.create(
            title="Closed Role",
            department="Engineering",
            location="Paris",
            level="senior",
            description="Closed job",
            status=JobStatus.CLOSED,
            created_by=self.recruiter,
        )
        self._login(self.recruiter)
        response = self.client.get("/api/jobs/?status=open")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Open Role")

    def test_retrieve_job_detail(self):
        job = JobOpening.objects.create(
            title="DevOps Engineer",
            department="Platform",
            location="Remote",
            level="lead",
            description="Infrastructure",
            skills=["Docker", "Kubernetes"],
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self._login(self.interviewer)
        response = self.client.get(f"/api/jobs/{job.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "DevOps Engineer")

    def test_recruiter_can_update_job(self):
        job = JobOpening.objects.create(
            title="Old Title",
            department="Engineering",
            location="Paris",
            level="mid",
            description="Old description",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self._login(self.recruiter)
        response = self.client.patch(
            f"/api/jobs/{job.id}/",
            {"title": "New Title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "New Title")

    def test_recruiter_can_delete_job(self):
        job = JobOpening.objects.create(
            title="To Delete",
            department="Engineering",
            location="Paris",
            level="junior",
            description="Temporary",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self._login(self.recruiter)
        response = self.client.delete(f"/api/jobs/{job.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(JobOpening.objects.filter(id=job.id).exists())

    def test_invalid_level_returns_400(self):
        self._login(self.recruiter)
        payload = {**self.job_payload, "level": "invalid"}
        response = self.client.post("/api/jobs/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PipelineStageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recruiter = User.objects.create_user(
            email="recruiter@sqli.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role=Role.RECRUITER,
        )
        self.job_payload = {
            "title": "Senior Python Developer",
            "department": "Engineering",
            "location": "Paris",
            "level": "senior",
            "description": "Build interview tracker APIs.",
            "skills": ["Python", "Django"],
            "status": "open",
        }

    def _login(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.recruiter.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_seed_default_pipeline_stages(self):
        created = seed_default_pipeline_stages()
        self.assertEqual(created, 7)
        self.assertEqual(PipelineStage.objects.filter(job__isnull=True).count(), 7)

        # Idempotent — second run creates nothing
        self.assertEqual(seed_default_pipeline_stages(), 0)

    def test_seed_uses_brand_colors(self):
        seed_default_pipeline_stages()
        applied = PipelineStage.objects.get(job__isnull=True, name="Applied")
        self.assertEqual(applied.color, "#6B7280")
        self.assertEqual(applied.order, 1)

    def test_job_create_auto_adds_stages(self):
        self._login()
        response = self.client.post("/api/jobs/", self.job_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_id = response.json()["id"]

        stages = PipelineStage.objects.filter(job_id=job_id).order_by("order")
        self.assertEqual(stages.count(), 7)
        self.assertEqual(stages.first().name, "Applied")
        self.assertEqual(stages.last().name, "Rejected")

    def test_get_job_stages_endpoint(self):
        self._login()
        create_response = self.client.post("/api/jobs/", self.job_payload, format="json")
        job_id = create_response.json()["id"]

        response = self.client.get(f"/api/jobs/{job_id}/stages/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0]["name"], "Applied")
        self.assertEqual(data[0]["color"], "#6B7280")
        self.assertEqual(data[3]["name"], "Culture Fit")

    def test_copy_default_stages_to_job_is_idempotent(self):
        job = JobOpening.objects.create(
            title="Backend Developer",
            department="Engineering",
            location="Lyon",
            level="mid",
            description="API work",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        # Signal already created stages on create
        self.assertEqual(job.pipeline_stages.count(), 7)

        copy_default_stages_to_job(job)
        self.assertEqual(job.pipeline_stages.count(), 7)

    def test_stages_ordered_by_order_field(self):
        job = JobOpening.objects.create(
            title="DevOps Engineer",
            department="Platform",
            location="Remote",
            level="lead",
            description="Infrastructure",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        names = list(job.pipeline_stages.order_by("order").values_list("name", flat=True))
        expected = [stage["name"] for stage in DEFAULT_PIPELINE_STAGES]
        self.assertEqual(names, expected)
