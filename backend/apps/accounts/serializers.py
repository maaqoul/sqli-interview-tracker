from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import User


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login with email instead of username."""

    username_field = "email"


class UserSerializer(serializers.ModelSerializer):
    """Public user profile — used by GET /api/auth/me/"""

    class Meta:
        model = User
        fields = ("id", "email", "role", "first_name", "last_name")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Admin creates a new user — POST /api/auth/register/"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "role")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """Logged-in user changes own password — POST /api/auth/change-password/"""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        validate_password(attrs["new_password"], self.context["request"].user)
        return attrs

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
