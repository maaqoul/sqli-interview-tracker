from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsRecruiter
from apps.jobs.models import JobOpening
from apps.jobs.serializers import JobOpeningSerializer, PipelineStageSerializer


class JobOpeningViewSet(viewsets.ModelViewSet):
    """CRUD for job openings at /api/jobs/."""

    queryset = JobOpening.objects.select_related("created_by").all()
    serializer_class = JobOpeningSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsRecruiter()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def stages(self, request, pk=None):
        """GET /api/jobs/{id}/stages/ — ordered pipeline stages for a job."""
        job = self.get_object()
        stages = job.pipeline_stages.order_by("order")
        serializer = PipelineStageSerializer(stages, many=True)
        return Response(serializer.data)
