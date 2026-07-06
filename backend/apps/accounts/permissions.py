from rest_framework.permissions import BasePermission

from apps.accounts.models import Role


class IsAdmin(BasePermission):
    """Allow only users with role=admin."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


class IsRecruiter(BasePermission):
    """Allow recruiters and admins."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.RECRUITER, Role.ADMIN)
        )


class IsInterviewer(BasePermission):
    """Allow interviewers and admins."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.INTERVIEWER, Role.ADMIN)
        )
