from django.contrib import admin

from apps.candidates.models import Candidate, CandidateActivity


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


@admin.register(CandidateActivity)
class CandidateActivityAdmin(admin.ModelAdmin):
    list_display = ("candidate", "action_type", "user", "created_at")
    list_filter = ("action_type",)
    search_fields = ("candidate__first_name", "candidate__last_name", "description")
    readonly_fields = ("created_at",)
