from django.conf import settings
from django.db import models


class AISessionType(models.TextChoices):
    QUESTIONS = "questions", "Questions"
    SUMMARY = "summary", "Summary"
    MOCK = "mock", "Mock"


class AISession(models.Model):
    """Logged AI interactions (INT-038 will expand list/filter UI)."""

    type = models.CharField(max_length=20, choices=AISessionType.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_sessions",
    )
    candidate = models.ForeignKey(
        "candidates.Candidate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_sessions",
    )
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} by {self.user_id} @ {self.created_at}"
