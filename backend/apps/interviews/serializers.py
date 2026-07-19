from rest_framework import serializers

from apps.accounts.models import User
from apps.interviews.models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    candidate_name = serializers.SerializerMethodField(read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    interviewer_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source="interviewers",
        required=False,
    )
    interviewer_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interview
        fields = (
            "id",
            "candidate",
            "candidate_name",
            "job",
            "job_title",
            "type",
            "scheduled_at",
            "duration_min",
            "location",
            "video_link",
            "status",
            "interviewer_ids",
            "interviewer_names",
            "created_by",
            "created_by_name",
            "created_at",
        )
        read_only_fields = (
            "id",
            "candidate_name",
            "job_title",
            "interviewer_names",
            "created_by",
            "created_by_name",
            "created_at",
        )

    def get_candidate_name(self, obj):
        return f"{obj.candidate.first_name} {obj.candidate.last_name}"

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_interviewer_names(self, obj):
        return [
            f"{u.first_name} {u.last_name}".strip() or u.email
            for u in obj.interviewers.all()
        ]

    def validate(self, attrs):
        candidate = attrs.get("candidate") or (self.instance.candidate if self.instance else None)
        job = attrs.get("job") or (self.instance.job if self.instance else None)

        if candidate and job and candidate.job_id != job.id:
            raise serializers.ValidationError(
                {"job": "Job must match the candidate's job opening."}
            )

        return attrs

    def create(self, validated_data):
        interviewers = validated_data.pop("interviewers", [])
        interview = Interview.objects.create(**validated_data)
        if interviewers:
            interview.interviewers.set(interviewers)
        return interview

    def update(self, instance, validated_data):
        interviewers = validated_data.pop("interviewers", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if interviewers is not None:
            instance.interviewers.set(interviewers)
        return instance
