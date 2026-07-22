from django.urls import path

from apps.ai_assistant.views import GenerateQuestionsView

urlpatterns = [
    path(
        "generate-questions/",
        GenerateQuestionsView.as_view(),
        name="ai_generate_questions",
    ),
]
