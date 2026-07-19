from django.conf import settings
from django.db import models

from apps.jobs.models import JobOpening, PipelineStage


class CandidateSource(models.TextChoices):
    LINKEDIN = "linkedin", "LinkedIn"
    REFERRAL = "referral", "Referral"
    JOB_BOARD = "job_board", "Job board"
    OTHER = "other", "Other"


class CandidateStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    REJECTED = "rejected", "Rejected"
    HIRED = "hired", "Hired"


class ActivityActionType(models.TextChoices):
    CREATED = "created", "Created"
    STAGE_CHANGE = "stage_change", "Stage change"
    NOTE_ADDED = "note_added", "Note added"
    INTERVIEW_SCHEDULED = "interview_scheduled", "Interview scheduled"
    SCORECARD_SUBMITTED = "scorecard_submitted", "Scorecard submitted"


class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    linkedin = models.URLField(blank=True)
    resume_file = models.FileField(upload_to="resumes/", blank=True, null=True)
    source = models.CharField(
        max_length=20,
        choices=CandidateSource.choices,
        blank=True,
    )
    job = models.ForeignKey(
        JobOpening,
        on_delete=models.CASCADE,
        related_name="candidates",
    )
    current_stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.PROTECT,
        related_name="candidates",
    )
    status = models.CharField(
        max_length=20,
        choices=CandidateStatus.choices,
        default=CandidateStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CandidateActivity(models.Model):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="candidate_activities",
    )
    action_type = models.CharField(max_length=40, choices=ActivityActionType.choices)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "candidate activities"

    def __str__(self):
        return f"{self.candidate} — {self.action_type}"
