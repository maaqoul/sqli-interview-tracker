from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.candidates.views import CandidateViewSet

router = DefaultRouter()
router.register("", CandidateViewSet, basename="candidate")

urlpatterns = [
    path("", include(router.urls)),
]
