from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsRecruiter
from apps.accounts.serializers import (
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    EmailTokenObtainPairSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class MeView(APIView):
    """GET/PATCH /api/auth/me/ — current user profile."""

    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={"request": request}).data)


class UserListView(generics.ListAPIView):
    """GET /api/auth/users/ — list users (recruiter+ for assignment; admin sees all)."""

    permission_classes = [IsAuthenticated, IsRecruiter]
    serializer_class = UserSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = User.objects.filter(is_active=True).order_by("first_name", "last_name")
        # Admins managing users can request include_inactive
        if self.request.user.role == "admin" and self.request.query_params.get(
            "include_inactive"
        ):
            queryset = User.objects.all().order_by("first_name", "last_name")
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class UserDetailView(APIView):
    """PATCH /api/auth/users/<id>/ — admin updates role / active."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data)


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
