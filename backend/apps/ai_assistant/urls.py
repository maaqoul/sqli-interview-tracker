from django.urls import path

from apps.ai_assistant.views import (
    GenerateQuestionsView,
    MockInterviewView,
    SummarizeFeedbackView,
)

urlpatterns = [
    path(
        "generate-questions/",
        GenerateQuestionsView.as_view(),
        name="ai_generate_questions",
    ),
    path(
        "summarize-feedback/",
        SummarizeFeedbackView.as_view(),
        name="ai_summarize_feedback",
    ),
    path(
        "mock-interview/",
        MockInterviewView.as_view(),
        name="ai_mock_interview",
    ),
]
