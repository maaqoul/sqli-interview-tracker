from django.contrib import admin

from apps.candidates.models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "job",
        "current_stage",
        "status",
        "created_at",
    )
    list_filter = ("status", "source", "job", "current_stage")
    search_fields = ("first_name", "last_name", "email")
