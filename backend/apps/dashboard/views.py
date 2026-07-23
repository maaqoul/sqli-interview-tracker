from collections import defaultdict
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_assistant.models import AISession, AISessionType
from apps.candidates.models import Candidate, CandidateActivity, CandidateStatus
from apps.interviews.models import Interview
from apps.jobs.constants import DEFAULT_PIPELINE_STAGES
from apps.jobs.models import JobOpening, JobStatus, PipelineStage


class DashboardStatsView(APIView):
    """GET /api/dashboard/stats/ — INT-040."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        week_start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        week_end = week_start + timedelta(days=7)

        open_jobs = JobOpening.objects.filter(status=JobStatus.OPEN).count()
        total_candidates = Candidate.objects.count()
        interviews_this_week = Interview.objects.filter(
            scheduled_at__gte=week_start,
            scheduled_at__lt=week_end,
        ).count()

        hired = Candidate.objects.filter(status=CandidateStatus.HIRED)
        hire_days = []
        for c in hired.only("created_at", "updated_at"):
            delta = (c.updated_at - c.created_at).total_seconds() / 86400
            if delta >= 0:
                hire_days.append(delta)
        avg_time_to_hire = round(sum(hire_days) / len(hire_days), 1) if hire_days else None

        ai_counts = {
            row["type"]: row["c"]
            for row in AISession.objects.values("type").annotate(c=Count("id"))
        }
        ai_usage = {
            "questions": ai_counts.get(AISessionType.QUESTIONS, 0),
            "summary": ai_counts.get(AISessionType.SUMMARY, 0),
            "mock": ai_counts.get(AISessionType.MOCK, 0),
            "total": sum(ai_counts.values()),
        }

        upcoming = (
            Interview.objects.filter(
                scheduled_at__gte=now,
                scheduled_at__lt=week_end,
            )
            .select_related("candidate", "job")
            .order_by("scheduled_at")[:10]
        )
        upcoming_interviews = [
            {
                "id": iv.id,
                "scheduled_at": iv.scheduled_at.isoformat(),
                "type": iv.type,
                "candidate_name": f"{iv.candidate.first_name} {iv.candidate.last_name}",
                "job_title": iv.job.title,
            }
            for iv in upcoming
        ]

        return Response(
            {
                "open_jobs": open_jobs,
                "total_candidates": total_candidates,
                "interviews_this_week": interviews_this_week,
                "avg_time_to_hire": avg_time_to_hire,
                "ai_usage": ai_usage,
                "upcoming_interviews": upcoming_interviews,
            }
        )


class DashboardFunnelView(APIView):
    """GET /api/dashboard/funnel/ — candidates per pipeline stage name."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        color_by_name = {s["name"]: s["color"] for s in DEFAULT_PIPELINE_STAGES}
        order_by_name = {s["name"]: s["order"] for s in DEFAULT_PIPELINE_STAGES}

        # Prefer stage colors from DB when available
        for stage in PipelineStage.objects.values("name", "color").distinct():
            if stage["name"] and stage["color"]:
                color_by_name[stage["name"]] = stage["color"]

        counts = (
            Candidate.objects.filter(status=CandidateStatus.ACTIVE)
            .values("current_stage__name")
            .annotate(count=Count("id"))
        )
        count_map = defaultdict(int)
        for row in counts:
            name = row["current_stage__name"] or "Unknown"
            count_map[name] += row["count"]

        # Always include default stages for a stable funnel order
        stage_names = [s["name"] for s in DEFAULT_PIPELINE_STAGES]
        for name in count_map:
            if name not in stage_names:
                stage_names.append(name)

        funnel = [
            {
                "stage": name,
                "count": count_map.get(name, 0),
                "color": color_by_name.get(name, "#6B7280"),
            }
            for name in sorted(
                stage_names,
                key=lambda n: order_by_name.get(n, 99),
            )
            if name != "Rejected"  # keep funnel focused; rejected still countable if wanted
        ]
        # Include Rejected at end if any
        if count_map.get("Rejected"):
            funnel.append(
                {
                    "stage": "Rejected",
                    "count": count_map["Rejected"],
                    "color": color_by_name.get("Rejected", "#EF4444"),
                }
            )

        return Response(funnel)


class DashboardActivityView(APIView):
    """GET /api/dashboard/activity/ — last 20 candidate events."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = (
            CandidateActivity.objects.select_related("candidate", "user")
            .order_by("-created_at")[:20]
        )
        results = []
        for a in activities:
            user_name = None
            if a.user:
                user_name = f"{a.user.first_name} {a.user.last_name}".strip() or a.user.email
            results.append(
                {
                    "id": a.id,
                    "action_type": a.action_type,
                    "description": a.description,
                    "candidate_id": a.candidate_id,
                    "candidate_name": f"{a.candidate.first_name} {a.candidate.last_name}",
                    "user_name": user_name,
                    "created_at": a.created_at.isoformat(),
                }
            )
        return Response({"count": len(results), "results": results})
