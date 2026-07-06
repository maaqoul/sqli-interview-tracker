from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsRecruiter
from apps.candidates.models import Candidate
from apps.candidates.serializers import CandidateSerializer
from apps.candidates.validators import validate_resume_file


class CandidateViewSet(viewsets.ModelViewSet):
    """CRUD for candidates at /api/candidates/."""

    queryset = Candidate.objects.select_related("job", "current_stage").all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "upload_resume"):
            return [IsAuthenticated(), IsRecruiter()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"], url_path="upload-resume")
    def upload_resume(self, request, pk=None):
        """POST /api/candidates/{id}/upload-resume/ — attach a PDF resume (max 5MB)."""
        candidate = self.get_object()
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response({"file": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        error = validate_resume_file(uploaded_file)
        if error:
            return Response({"file": error}, status=status.HTTP_400_BAD_REQUEST)

        if candidate.resume_file:
            candidate.resume_file.delete(save=False)

        candidate.resume_file = uploaded_file
        candidate.save(update_fields=["resume_file", "updated_at"])

        serializer = self.get_serializer(candidate)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()

        job_id = self.request.query_params.get("job_id")
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        stage_id = self.request.query_params.get("stage")
        if stage_id:
            queryset = queryset.filter(current_stage_id=stage_id)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        date_from = parse_date(self.request.query_params.get("date_from", ""))
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = parse_date(self.request.query_params.get("date_to", ""))
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset
