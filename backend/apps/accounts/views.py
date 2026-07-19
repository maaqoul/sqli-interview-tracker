from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsRecruiter
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    """GET /api/auth/me/ — current logged-in user profile."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """GET /api/auth/users/ — list users for interviewer assignment (recruiter+)."""

    permission_classes = [IsAuthenticated, IsRecruiter]
    serializer_class = UserSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = User.objects.filter(is_active=True).order_by("first_name", "last_name")
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — admin-only user creation."""

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = RegisterSerializer


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ — change own password."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
