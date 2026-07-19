from django.contrib import admin

from apps.interviews.models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "candidate",
        "job",
        "type",
        "scheduled_at",
        "status",
        "created_by",
    )
    list_filter = ("type", "status")
    search_fields = ("candidate__first_name", "candidate__last_name", "job__title")
    filter_horizontal = ("interviewers",)
