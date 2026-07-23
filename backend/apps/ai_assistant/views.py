from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_assistant.models import AISession, AISessionType
from apps.ai_assistant.rate_limit import check_ai_rate_limit
from apps.ai_assistant.serializers import GenerateQuestionsSerializer
from apps.ai_assistant.services import get_ai_service


class GenerateQuestionsView(APIView):
    """POST /api/ai/generate-questions/ — INT-035."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateQuestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        check_ai_rate_limit(request.user)

        try:
            questions = get_ai_service().generate_questions(
                job_title=data["job_title"],
                level=data["level"],
                skills=data.get("skills") or [],
                interview_type=data.get("interview_type") or "technical",
                n=data.get("n") or 10,
            )
        except Exception as exc:  # noqa: BLE001 — surface provider errors cleanly
            return Response(
                {"detail": f"AI generation failed: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        session_id = None
        if data.get("save", True):
            session = AISession.objects.create(
                type=AISessionType.QUESTIONS,
                user=request.user,
                input_data={
                    "job_id": data.get("job_id"),
                    "job_title": data["job_title"],
                    "level": data["level"],
                    "skills": data.get("skills") or [],
                    "interview_type": data.get("interview_type"),
                },
                output_data={"questions": questions},
            )
            session_id = session.id

        return Response(
            {
                "questions": questions,
                "count": len(questions),
                "session_id": session_id,
            },
            status=status.HTTP_200_OK,
        )
