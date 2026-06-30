from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.jobs.views import JobOpeningViewSet

router = DefaultRouter()
router.register("", JobOpeningViewSet, basename="job")

urlpatterns = [
    path("", include(router.urls)),
]
