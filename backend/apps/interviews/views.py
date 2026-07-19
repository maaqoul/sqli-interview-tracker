from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import Role
from apps.accounts.permissions import IsRecruiter
from apps.interviews.models import Interview
from apps.interviews.serializers import InterviewSerializer
from apps.interviews.services import log_interview_scheduled, notify_interviewers


class InterviewViewSet(viewsets.ModelViewSet):
    """CRUD for interviews at /api/interviews/."""

    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsRecruiter()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Interview.objects.select_related(
            "candidate",
            "job",
            "created_by",
        ).prefetch_related("interviewers")

        # Interviewers only see interviews they are assigned to
        if user.role == Role.INTERVIEWER:
            queryset = queryset.filter(interviewers=user)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        interviewer = self.request.query_params.get("interviewer")
        if interviewer:
            queryset = queryset.filter(interviewers__id=interviewer)

        date_from = self.request.query_params.get("date_from")
        if date_from:
            parsed = parse_datetime(date_from) or parse_date(date_from)
            if parsed:
                if hasattr(parsed, "year") and not hasattr(parsed, "hour"):
                    queryset = queryset.filter(scheduled_at__date__gte=parsed)
                else:
                    queryset = queryset.filter(scheduled_at__gte=parsed)

        date_to = self.request.query_params.get("date_to")
        if date_to:
            parsed = parse_datetime(date_to) or parse_date(date_to)
            if parsed:
                if hasattr(parsed, "year") and not hasattr(parsed, "hour"):
                    queryset = queryset.filter(scheduled_at__date__lte=parsed)
                else:
                    queryset = queryset.filter(scheduled_at__lte=parsed)

        candidate_id = self.request.query_params.get("candidate_id")
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)

        return queryset.distinct()

    def perform_create(self, serializer):
        interview = serializer.save(created_by=self.request.user)
        interviewer_ids = list(interview.interviewers.values_list("id", flat=True))
        if interviewer_ids:
            notify_interviewers(interview=interview, interviewer_ids=interviewer_ids)
        log_interview_scheduled(interview=interview, user=self.request.user)

    def perform_update(self, serializer):
        previous_ids = set(serializer.instance.interviewers.values_list("id", flat=True))
        interview = serializer.save()
        current_ids = set(interview.interviewers.values_list("id", flat=True))
        newly_assigned = current_ids - previous_ids
        if newly_assigned:
            notify_interviewers(interview=interview, interviewer_ids=list(newly_assigned))
