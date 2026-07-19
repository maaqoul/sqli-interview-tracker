from rest_framework import serializers

from apps.accounts.models import Role
from apps.scorecards.models import Scorecard

SKILL_KEYS = (
    "technical",
    "communication",
    "problem_solving",
    "culture_fit",
    "leadership",
)


class ScorecardSerializer(serializers.ModelSerializer):
    interviewer_name = serializers.SerializerMethodField(read_only=True)
    candidate_name = serializers.SerializerMethodField(read_only=True)
    interview_type = serializers.CharField(source="interview.type", read_only=True)

    class Meta:
        model = Scorecard
        fields = (
            "id",
            "interview",
            "interview_type",
            "interviewer",
            "interviewer_name",
            "candidate_name",
            "overall_rating",
            "skill_ratings",
            "strengths",
            "weaknesses",
            "recommendation",
            "private_notes",
            "submitted_at",
        )
        read_only_fields = (
            "id",
            "interviewer",
            "interviewer_name",
            "candidate_name",
            "interview_type",
            "submitted_at",
        )

    def get_interviewer_name(self, obj):
        return f"{obj.interviewer.first_name} {obj.interviewer.last_name}".strip()

    def get_candidate_name(self, obj):
        c = obj.interview.candidate
        return f"{c.first_name} {c.last_name}"

    def validate_overall_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_skill_ratings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("skill_ratings must be an object.")
        for key in SKILL_KEYS:
            if key not in value:
                raise serializers.ValidationError(f"Missing skill rating: {key}")
            rating = value[key]
            if not isinstance(rating, int) or not 1 <= rating <= 5:
                raise serializers.ValidationError(f"{key} must be an integer 1–5.")
        return value

    def validate_interview(self, interview):
        request = self.context["request"]
        if request.user.role == Role.INTERVIEWER:
            if not interview.interviewers.filter(id=request.user.id).exists():
                raise serializers.ValidationError(
                    "You are not assigned to this interview."
                )
        return interview

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.user.role == Role.INTERVIEWER:
            data.pop("private_notes", None)
        return data

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["interviewer"] = request.user
        return super().create(validated_data)
