from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate, CandidateSource, CandidateStatus
from apps.jobs.models import JobOpening, JobStatus, PipelineStage


class CandidateAPITests(TestCase):
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
        self.job = JobOpening.objects.create(
            title="Senior Python Developer",
            department="Engineering",
            location="Paris",
            level="senior",
            description="Build interview tracker APIs.",
            skills=["Python", "Django"],
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self.applied_stage = self.job.pipeline_stages.get(order=1)
        self.screening_stage = self.job.pipeline_stages.get(order=2)
        self.other_job = JobOpening.objects.create(
            title="UX Designer",
            department="Design",
            location="Lyon",
            level="mid",
            description="Design systems.",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self.other_job_stage = self.other_job.pipeline_stages.get(order=1)
        self.candidate_payload = {
            "first_name": "Marie",
            "last_name": "Martin",
            "email": "marie.martin@example.com",
            "phone": "+33612345678",
            "linkedin": "https://linkedin.com/in/mariemartin",
            "source": CandidateSource.LINKEDIN,
            "job": self.job.id,
        }

    def _login(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def _create_candidate(self, **overrides):
        payload = {**self.candidate_payload, **overrides}
        return Candidate.objects.create(
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            email=payload.get("email", "other@example.com"),
            phone=payload.get("phone", ""),
            linkedin=payload.get("linkedin", ""),
            source=payload.get("source", ""),
            job_id=payload["job"],
            current_stage_id=payload.get("current_stage", self.applied_stage.id),
            status=payload.get("status", CandidateStatus.ACTIVE),
        )

    def test_recruiter_can_create_candidate(self):
        self._login(self.recruiter)
        response = self.client.post("/api/candidates/", self.candidate_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["first_name"], "Marie")
        self.assertEqual(data["job"], self.job.id)
        self.assertEqual(data["job_title"], "Senior Python Developer")
        self.assertEqual(data["current_stage_name"], "Applied")
        self.assertEqual(data["status"], "active")

    def test_create_defaults_to_applied_stage(self):
        self._login(self.recruiter)
        response = self.client.post("/api/candidates/", self.candidate_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["current_stage"], self.applied_stage.id)

    def test_interviewer_cannot_create_candidate(self):
        self._login(self.interviewer)
        response = self.client.post("/api/candidates/", self.candidate_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_interviewer_cannot_delete_candidate(self):
        candidate = self._create_candidate()
        self._login(self.interviewer)
        response = self.client.delete(f"/api/candidates/{candidate.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Candidate.objects.filter(id=candidate.id).exists())

    def test_recruiter_can_delete_candidate(self):
        candidate = self._create_candidate()
        self._login(self.recruiter)
        response = self.client.delete(f"/api/candidates/{candidate.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Candidate.objects.filter(id=candidate.id).exists())

    def test_list_candidates_is_paginated(self):
        self._create_candidate()
        self._login(self.interviewer)
        response = self.client.get("/api/candidates/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["count"], 1)

    def test_filter_candidates_by_job_id(self):
        self._create_candidate(job=self.job.id)
        self._create_candidate(
            first_name="Paul",
            last_name="Durand",
            email="paul@example.com",
            job=self.other_job.id,
            current_stage=self.other_job_stage.id,
        )
        self._login(self.recruiter)
        response = self.client.get(f"/api/candidates/?job_id={self.job.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["first_name"], "Marie")

    def test_filter_candidates_by_stage(self):
        self._create_candidate(current_stage=self.applied_stage.id)
        self._create_candidate(
            first_name="Paul",
            last_name="Durand",
            email="paul@example.com",
            current_stage=self.screening_stage.id,
        )
        self._login(self.recruiter)
        response = self.client.get(f"/api/candidates/?stage={self.screening_stage.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["first_name"], "Paul")

    def test_search_candidates_by_name_or_email(self):
        self._create_candidate()
        self._create_candidate(
            first_name="Paul",
            last_name="Durand",
            email="paul.durand@example.com",
        )
        self._login(self.recruiter)

        by_first_name = self.client.get("/api/candidates/?search=marie")
        self.assertEqual(by_first_name.json()["count"], 1)
        self.assertEqual(by_first_name.json()["results"][0]["email"], "marie.martin@example.com")

        by_email = self.client.get("/api/candidates/?search=durand@example")
        self.assertEqual(by_email.json()["count"], 1)
        self.assertEqual(by_email.json()["results"][0]["first_name"], "Paul")

    def test_filter_candidates_by_date_range(self):
        older = self._create_candidate(email="older@example.com")
        Candidate.objects.filter(id=older.id).update(
            created_at=timezone.now() - timedelta(days=10)
        )

        newer = self._create_candidate(
            first_name="Nina",
            last_name="Rossi",
            email="nina@example.com",
        )

        self._login(self.recruiter)
        today = timezone.localdate()
        week_ago = today - timedelta(days=7)

        response = self.client.get(f"/api/candidates/?date_from={week_ago.isoformat()}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = {item["email"] for item in response.json()["results"]}
        self.assertIn("nina@example.com", emails)
        self.assertNotIn("older@example.com", emails)

        only_old = self.client.get(
            f"/api/candidates/?date_to={(today - timedelta(days=8)).isoformat()}"
        )
        old_emails = {item["email"] for item in only_old.json()["results"]}
        self.assertIn("older@example.com", old_emails)
        self.assertNotIn("nina@example.com", old_emails)

    def test_stage_must_belong_to_job(self):
        self._login(self.recruiter)
        payload = {
            **self.candidate_payload,
            "current_stage": self.other_job_stage.id,
        }
        response = self.client.post("/api/candidates/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("current_stage", response.json())

    def test_recruiter_can_update_candidate(self):
        candidate = self._create_candidate()
        self._login(self.recruiter)
        response = self.client.patch(
            f"/api/candidates/{candidate.id}/",
            {"current_stage": self.screening_stage.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["current_stage_name"], "Screening")

    def test_retrieve_candidate_detail(self):
        candidate = self._create_candidate()
        self._login(self.interviewer)
        response = self.client.get(f"/api/candidates/{candidate.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "marie.martin@example.com")

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get("/api/candidates/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CandidateResumeUploadTests(TestCase):
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
        self.job = JobOpening.objects.create(
            title="Senior Python Developer",
            department="Engineering",
            location="Paris",
            level="senior",
            description="Build interview tracker APIs.",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self.candidate = Candidate.objects.create(
            first_name="Marie",
            last_name="Martin",
            email="marie.martin@example.com",
            job=self.job,
            current_stage=self.job.pipeline_stages.get(order=1),
            status=CandidateStatus.ACTIVE,
        )

    def _login(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def _pdf_file(self, name="resume.pdf", content=None, content_type="application/pdf"):
        from django.core.files.uploadedfile import SimpleUploadedFile

        if content is None:
            content = b"%PDF-1.4 Marie Martin resume"
        return SimpleUploadedFile(name, content, content_type=content_type)

    def test_recruiter_can_upload_pdf_resume(self):
        self._login(self.recruiter)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/upload-resume/",
            {"file": self._pdf_file()},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("/media/resumes/", data["resume_file"])
        self.assertTrue(data["resume_file"].endswith(".pdf"))

        self.candidate.refresh_from_db()
        self.assertTrue(self.candidate.resume_file.name.startswith("resumes/"))

    def test_candidate_detail_returns_resume_download_url(self):
        self._login(self.recruiter)
        self.client.post(
            f"/api/candidates/{self.candidate.id}/upload-resume/",
            {"file": self._pdf_file()},
            format="multipart",
        )

        response = self.client.get(f"/api/candidates/{self.candidate.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resume_url = response.json()["resume_file"]
        self.assertIsNotNone(resume_url)
        self.assertIn("/media/resumes/", resume_url)

        self.candidate.refresh_from_db()
        self.assertTrue(self.candidate.resume_file.storage.exists(self.candidate.resume_file.name))

    def test_rejects_non_pdf_file(self):
        self._login(self.recruiter)
        from django.core.files.uploadedfile import SimpleUploadedFile

        docx = SimpleUploadedFile(
            "resume.docx",
            b"not a pdf",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/upload-resume/",
            {"file": docx},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.json())

    def test_rejects_file_over_5mb(self):
        self._login(self.recruiter)
        oversized = self._pdf_file(content=b"%PDF" + b"x" * (5 * 1024 * 1024))
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/upload-resume/",
            {"file": oversized},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("5MB", response.json()["file"])

    def test_upload_without_file_returns_400(self):
        self._login(self.recruiter)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/upload-resume/",
            {},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_interviewer_cannot_upload_resume(self):
        self._login(self.interviewer)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/upload-resume/",
            {"file": self._pdf_file()},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CandidateMoveStageAndTimelineTests(TestCase):
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
        self.job = JobOpening.objects.create(
            title="Senior Python Developer",
            department="Engineering",
            location="Paris",
            level="senior",
            description="Build interview tracker APIs.",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self.applied = self.job.pipeline_stages.get(order=1)
        self.screening = self.job.pipeline_stages.get(order=2)
        self.hired = self.job.pipeline_stages.get(name="Hired")
        self.rejected = self.job.pipeline_stages.get(name="Rejected")
        self.other_job = JobOpening.objects.create(
            title="UX Designer",
            department="Design",
            location="Lyon",
            level="mid",
            description="Design systems.",
            status=JobStatus.OPEN,
            created_by=self.recruiter,
        )
        self.other_job_stage = self.other_job.pipeline_stages.get(order=1)
        self.candidate = Candidate.objects.create(
            first_name="Marie",
            last_name="Martin",
            email="marie.martin@example.com",
            job=self.job,
            current_stage=self.applied,
            status=CandidateStatus.ACTIVE,
        )

    def _login(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

    def test_create_candidate_logs_created_activity(self):
        self._login(self.recruiter)
        response = self.client.post(
            "/api/candidates/",
            {
                "first_name": "Paul",
                "last_name": "Durand",
                "email": "paul@example.com",
                "job": self.job.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        candidate_id = response.json()["id"]

        timeline = self.client.get(f"/api/candidates/{candidate_id}/timeline/")
        self.assertEqual(timeline.status_code, status.HTTP_200_OK)
        events = timeline.json()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["action_type"], "created")
        self.assertEqual(events[0]["user"]["email"], "recruiter@sqli.com")
        self.assertIn("Senior Python Developer", events[0]["description"])

    def test_recruiter_can_move_candidate_stage(self):
        self._login(self.recruiter)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/move-stage/",
            {"stage_id": self.screening.id, "reason": "Passed phone screen"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["current_stage"], self.screening.id)
        self.assertEqual(response.json()["current_stage_name"], "Screening")
        self.assertEqual(response.json()["status"], "active")

        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.current_stage_id, self.screening.id)

    def test_move_stage_creates_activity_log(self):
        self._login(self.recruiter)
        self.client.post(
            f"/api/candidates/{self.candidate.id}/move-stage/",
            {"stage_id": self.screening.id, "reason": "Passed phone screen"},
            format="json",
        )

        timeline = self.client.get(f"/api/candidates/{self.candidate.id}/timeline/")
        events = timeline.json()
        stage_events = [e for e in events if e["action_type"] == "stage_change"]
        self.assertEqual(len(stage_events), 1)
        event = stage_events[0]
        self.assertEqual(event["metadata"]["from_stage_name"], "Applied")
        self.assertEqual(event["metadata"]["to_stage_name"], "Screening")
        self.assertEqual(event["metadata"]["reason"], "Passed phone screen")
        self.assertEqual(event["user"]["first_name"], "Jean")

    def test_reject_from_any_stage(self):
        self._login(self.recruiter)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/move-stage/",
            {"stage_id": self.rejected.id, "reason": "Not a culture fit"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["current_stage_name"], "Rejected")
        self.assertEqual(response.json()["status"], "rejected")

    def test_move_to_hired_sets_status(self):
        self._login(self.recruiter)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/move-stage/",
            {"stage_id": self.hired.id, "reason": "Offer accepted"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "hired")

    def test_stage_from_other_job_returns_400(self):
        self._login(self.recruiter)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/move-stage/",
            {"stage_id": self.other_job_stage.id, "reason": "Wrong job"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_reason_returns_400(self):
        self._login(self.recruiter)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/move-stage/",
            {"stage_id": self.screening.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", response.json())

    def test_interviewer_cannot_move_stage(self):
        self._login(self.interviewer)
        response = self.client.post(
            f"/api/candidates/{self.candidate.id}/move-stage/",
            {"stage_id": self.screening.id, "reason": "Nope"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_timeline_newest_first(self):
        self._login(self.recruiter)
        create_response = self.client.post(
            "/api/candidates/",
            {
                "first_name": "Nina",
                "last_name": "Rossi",
                "email": "nina@example.com",
                "job": self.job.id,
            },
            format="json",
        )
        candidate_id = create_response.json()["id"]
        self.client.post(
            f"/api/candidates/{candidate_id}/move-stage/",
            {"stage_id": self.screening.id, "reason": "Advance"},
            format="json",
        )

        timeline = self.client.get(f"/api/candidates/{candidate_id}/timeline/")
        events = timeline.json()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["action_type"], "stage_change")
        self.assertEqual(events[1]["action_type"], "created")

    def test_unauthenticated_timeline_returns_401(self):
        response = self.client.get(f"/api/candidates/{self.candidate.id}/timeline/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
