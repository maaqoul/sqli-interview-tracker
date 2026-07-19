from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.scorecards.views import ScorecardViewSet

router = DefaultRouter()
router.register("", ScorecardViewSet, basename="scorecard")

urlpatterns = [
    path("", include(router.urls)),
]
