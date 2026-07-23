from rest_framework import serializers


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
