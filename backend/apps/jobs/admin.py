from django.contrib import admin

from apps.jobs.models import JobOpening, PipelineStage


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "location", "level", "status", "created_by", "created_at")
    list_filter = ("status", "level", "department")
    search_fields = ("title", "department", "location")


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ("name", "job", "order", "color")
    list_filter = ("job",)
    ordering = ("job", "order")
