from rest_framework import serializers

from apps.ai_assistant.models import AISession, AISessionType


class GenerateQuestionsSerializer(serializers.Serializer):
    job_id = serializers.IntegerField(required=False, allow_null=True)
    job_title = serializers.CharField(max_length=200)
    level = serializers.CharField(max_length=20)
    skills = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
    )
    interview_type = serializers.CharField(max_length=40, default="technical")
    n = serializers.IntegerField(required=False, default=10, min_value=8, max_value=12)
    save = serializers.BooleanField(required=False, default=True)


class SummarizeFeedbackSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()


class MockInterviewSerializer(serializers.Serializer):
    role = serializers.CharField(max_length=200)
    level = serializers.CharField(max_length=20)
    history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )
    user_answer = serializers.CharField(required=False, allow_blank=True, default="")
    session_id = serializers.IntegerField(required=False, allow_null=True)
    end = serializers.BooleanField(required=False, default=False)


class AISessionSerializer(serializers.ModelSerializer):
    candidate_name = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()

    class Meta:
        model = AISession
        fields = (
            "id",
            "type",
            "user",
            "candidate",
            "candidate_name",
            "input_data",
            "output_data",
            "preview",
            "created_at",
        )
        read_only_fields = fields

    def get_candidate_name(self, obj):
        if not obj.candidate:
            return None
        return f"{obj.candidate.first_name} {obj.candidate.last_name}"

    def get_preview(self, obj):
        """Short label for list UI."""
        if obj.type == AISessionType.QUESTIONS:
            title = (obj.input_data or {}).get("job_title") or "Questions"
            count = len((obj.output_data or {}).get("questions") or [])
            return f"{title} · {count} questions"
        if obj.type == AISessionType.SUMMARY:
            rec = (obj.output_data or {}).get("recommendation") or "—"
            name = self.get_candidate_name(obj) or "Candidate"
            return f"{name} · recommend {rec}"
        if obj.type == AISessionType.MOCK:
            role = (obj.input_data or {}).get("role") or "Mock interview"
            done = (obj.output_data or {}).get("done")
            status = "completed" if done else "in progress"
            return f"{role} · {status}"
        return obj.type
