from rest_framework import serializers

from apps.candidates.models import Candidate, CandidateActivity
from apps.jobs.models import PipelineStage


class MoveStageSerializer(serializers.Serializer):
    stage_id = serializers.PrimaryKeyRelatedField(
        queryset=PipelineStage.objects.all(),
        source="stage",
    )
    reason = serializers.CharField(max_length=500)


class CandidateActivitySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CandidateActivity
        fields = ("id", "action_type", "description", "metadata", "user", "created_at")

    def get_user(self, obj):
        if not obj.user:
            return None
        return {
            "id": obj.user.id,
            "email": obj.user.email,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
        }


class CandidateSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    current_stage_name = serializers.CharField(source="current_stage.name", read_only=True)
    current_stage_color = serializers.CharField(source="current_stage.color", read_only=True)
    resume_file = serializers.SerializerMethodField()
    current_stage = serializers.PrimaryKeyRelatedField(
        queryset=PipelineStage.objects.all(),
        required=False,
        allow_null=True,
    )

    def get_resume_file(self, obj):
        if not obj.resume_file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.resume_file.url)
        return obj.resume_file.url

    class Meta:
        model = Candidate
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "linkedin",
            "resume_file",
            "source",
            "job",
            "job_title",
            "current_stage",
            "current_stage_name",
            "current_stage_color",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "resume_file",
            "job_title",
            "current_stage_name",
            "current_stage_color",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        job = attrs.get("job") or (self.instance.job if self.instance else None)
        current_stage = attrs.get("current_stage")

        if current_stage is None and self.instance is not None:
            current_stage = self.instance.current_stage

        if job and current_stage and current_stage.job_id != job.id:
            raise serializers.ValidationError(
                {"current_stage": "Stage must belong to the selected job."}
            )

        return attrs

    def create(self, validated_data):
        job = validated_data["job"]
        if not validated_data.get("current_stage"):
            validated_data["current_stage"] = job.pipeline_stages.get(order=1)
        return super().create(validated_data)
