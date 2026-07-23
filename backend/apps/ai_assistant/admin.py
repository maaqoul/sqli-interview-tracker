from django.contrib import admin

from apps.ai_assistant.models import AISession


@admin.register(AISession)
class AISessionAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "user", "candidate", "created_at")
    list_filter = ("type",)
    search_fields = ("user__email",)
