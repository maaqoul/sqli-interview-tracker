from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok", "service": "sqli-interview-tracker"})


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response(
        {
            "message": "SQLI Interview Tracker API",
            "tagline": "We Elevate. Digitally.",
            "docs": "/api/docs/",
            "health": "/api/health/",
        }
    )
