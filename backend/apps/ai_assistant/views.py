from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_assistant.models import AISession, AISessionType
from apps.ai_assistant.rate_limit import check_ai_rate_limit
from apps.ai_assistant.serializers import (
    GenerateQuestionsSerializer,
    MockInterviewSerializer,
    SummarizeFeedbackSerializer,
)
from apps.ai_assistant.services import get_ai_service
from apps.candidates.models import ActivityActionType, Candidate, CandidateActivity
from apps.scorecards.models import Scorecard


def _scorecard_payload(scorecard: Scorecard) -> dict:
    return {
        "interviewer": f"{scorecard.interviewer.first_name} {scorecard.interviewer.last_name}",
        "overall_rating": scorecard.overall_rating,
        "skill_ratings": scorecard.skill_ratings,
        "strengths": scorecard.strengths,
        "weaknesses": scorecard.weaknesses,
        "recommendation": scorecard.recommendation,
        "private_notes": scorecard.private_notes,
    }


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


class SummarizeFeedbackView(APIView):
    """POST /api/ai/summarize-feedback/ — INT-036."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SummarizeFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidate_id = serializer.validated_data["candidate_id"]

        try:
            candidate = Candidate.objects.select_related("job").get(pk=candidate_id)
        except Candidate.DoesNotExist:
            return Response(
                {"detail": "Candidate not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        check_ai_rate_limit(request.user)

        scorecards = list(
            Scorecard.objects.filter(interview__candidate=candidate).select_related(
                "interviewer"
            )
        )
        notes = list(
            CandidateActivity.objects.filter(
                candidate=candidate,
                action_type=ActivityActionType.NOTE_ADDED,
            ).values_list("description", flat=True)
        )
        scorecard_data = [_scorecard_payload(s) for s in scorecards]

        try:
            brief = get_ai_service().summarize_feedback(scorecard_data, notes)
        except Exception as exc:  # noqa: BLE001
            return Response(
                {"detail": f"AI summary failed: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        session = AISession.objects.create(
            type=AISessionType.SUMMARY,
            user=request.user,
            candidate=candidate,
            input_data={
                "candidate_id": candidate.id,
                "scorecard_count": len(scorecard_data),
                "notes_count": len(notes),
            },
            output_data=brief,
        )

        return Response(
            {
                **brief,
                "session_id": session.id,
                "scorecard_count": len(scorecard_data),
                "notes_count": len(notes),
                "disclaimer": "AI-assisted — human decision required",
            },
            status=status.HTTP_200_OK,
        )


class MockInterviewView(APIView):
    """POST /api/ai/mock-interview/ — INT-037."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MockInterviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        check_ai_rate_limit(request.user)

        history = list(data.get("history") or [])
        user_answer = data.get("user_answer") or ""
        end = bool(data.get("end"))

        try:
            turn = get_ai_service().mock_interview_turn(
                role=data["role"],
                level=data["level"],
                history=history,
                user_answer="" if end and not user_answer else user_answer,
            )
            if end:
                turn = {
                    **turn,
                    "done": True,
                    "next_question": "",
                    "summary": turn.get("summary")
                    or (
                        f"Practice session ended for {data['level']} {data['role']}. "
                        "Review your answers and try again to improve."
                    ),
                }
        except Exception as exc:  # noqa: BLE001
            return Response(
                {"detail": f"Mock interview failed: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Build updated transcript
        new_history = list(history)
        if user_answer and not end:
            new_history.append({"role": "user", "content": user_answer})
        if turn.get("feedback"):
            new_history.append({"role": "assistant", "content": turn["feedback"]})
        if turn.get("next_question"):
            new_history.append({"role": "assistant", "content": turn["next_question"]})
        elif turn.get("done") and turn.get("summary"):
            new_history.append({"role": "assistant", "content": turn["summary"]})

        session_id = data.get("session_id")
        session = None
        if session_id:
            session = AISession.objects.filter(
                id=session_id,
                user=request.user,
                type=AISessionType.MOCK,
            ).first()

        if session is None:
            session = AISession.objects.create(
                type=AISessionType.MOCK,
                user=request.user,
                input_data={"role": data["role"], "level": data["level"]},
                output_data={"history": new_history, "done": turn.get("done", False)},
            )
        else:
            session.output_data = {
                "history": new_history,
                "done": turn.get("done", False),
                "summary": turn.get("summary", ""),
            }
            session.save(update_fields=["output_data"])

        return Response(
            {
                "feedback": turn.get("feedback", ""),
                "next_question": turn.get("next_question", ""),
                "done": bool(turn.get("done")),
                "summary": turn.get("summary", ""),
                "history": new_history,
                "session_id": session.id,
            },
            status=status.HTTP_200_OK,
        )
