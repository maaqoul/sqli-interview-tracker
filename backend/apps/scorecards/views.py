from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.scorecards.models import Scorecard
from apps.scorecards.serializers import ScorecardSerializer
from apps.scorecards.services import finalize_scorecard_submission


class ScorecardViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Scorecards at /api/scorecards/ — create + list/retrieve."""

    serializer_class = ScorecardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Scorecard.objects.select_related(
            "interview",
            "interview__candidate",
            "interview__job",
            "interviewer",
        )

        if user.role == Role.INTERVIEWER:
            queryset = queryset.filter(interviewer=user)

        interview_id = self.request.query_params.get("interview_id")
        if interview_id:
            queryset = queryset.filter(interview_id=interview_id)

        candidate_id = self.request.query_params.get("candidate_id")
        if candidate_id:
            queryset = queryset.filter(interview__candidate_id=candidate_id)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interview = serializer.validated_data["interview"]
        if Scorecard.objects.filter(interview=interview, interviewer=request.user).exists():
            return Response(
                {"detail": "You already submitted a scorecard for this interview."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        scorecard = serializer.save()
        finalize_scorecard_submission(scorecard=scorecard, user=request.user)
        output = self.get_serializer(scorecard)
        return Response(output.data, status=status.HTTP_201_CREATED)
