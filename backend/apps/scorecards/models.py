from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.interviews.models import Interview


class Recommendation(models.TextChoices):
    STRONG_YES = "strong_yes", "Strong Yes"
    YES = "yes", "Yes"
    NEUTRAL = "neutral", "Neutral"
    NO = "no", "No"
    STRONG_NO = "strong_no", "Strong No"


class Scorecard(models.Model):
    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name="scorecards",
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scorecards",
    )
    overall_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    skill_ratings = models.JSONField(default=dict)
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    recommendation = models.CharField(max_length=20, choices=Recommendation.choices)
    private_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["interview", "interviewer"],
                name="unique_scorecard_per_interviewer_per_interview",
            ),
        ]

    def __str__(self):
        return f"Scorecard {self.interview_id} by {self.interviewer_id}"
