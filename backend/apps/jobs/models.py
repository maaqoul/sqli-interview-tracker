from django.conf import settings
from django.db import models


class JobLevel(models.TextChoices):
    JUNIOR = "junior", "Junior"
    MID = "mid", "Mid"
    SENIOR = "senior", "Senior"
    LEAD = "lead", "Lead"


class JobStatus(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    ON_HOLD = "on_hold", "On hold"


class JobOpening(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=JobLevel.choices)
    description = models.TextField()
    skills = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.OPEN,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="job_openings",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PipelineStage(models.Model):
    job = models.ForeignKey(
        JobOpening,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pipeline_stages",
    )
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField()
    color = models.CharField(max_length=7)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "order"],
                name="unique_stage_order_per_job",
            ),
        ]

    def __str__(self):
        job_label = self.job.title if self.job else "default"
        return f"{job_label} — {self.name}"
