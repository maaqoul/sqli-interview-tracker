from django.conf import settings
from django.db import models

from apps.candidates.models import Candidate
from apps.jobs.models import JobOpening


class InterviewType(models.TextChoices):
    PHONE = "phone", "Phone"
    VIDEO = "video", "Video"
    ONSITE = "onsite", "Onsite"


class InterviewStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    NO_SHOW = "no_show", "No show"


class Interview(models.Model):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="interviews",
    )
    job = models.ForeignKey(
        JobOpening,
        on_delete=models.CASCADE,
        related_name="interviews",
    )
    type = models.CharField(max_length=20, choices=InterviewType.choices)
    scheduled_at = models.DateTimeField()
    duration_min = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=255, blank=True)
    video_link = models.URLField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=InterviewStatus.choices,
        default=InterviewStatus.SCHEDULED,
    )
    interviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_interviews",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_interviews",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"{self.candidate} — {self.type} @ {self.scheduled_at}"
