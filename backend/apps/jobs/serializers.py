from rest_framework import serializers

from apps.jobs.models import JobOpening, PipelineStage


class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = ("id", "name", "order", "color")


class JobOpeningSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JobOpening
        fields = (
            "id",
            "title",
            "department",
            "location",
            "level",
            "description",
            "skills",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_by", "created_by_name", "created_at")

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def validate_skills(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Skills must be a list.")
        if not all(isinstance(skill, str) for skill in value):
            raise serializers.ValidationError("Each skill must be a string.")
        return value
