from django.contrib import admin

from apps.scorecards.models import Scorecard


@admin.register(Scorecard)
class ScorecardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "interview",
        "interviewer",
        "overall_rating",
        "recommendation",
        "submitted_at",
    )
    list_filter = ("recommendation",)
    search_fields = (
        "interview__candidate__first_name",
        "interview__candidate__last_name",
        "interviewer__email",
    )
