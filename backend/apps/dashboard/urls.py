from django.urls import path

from apps.dashboard.views import (
    DashboardActivityView,
    DashboardFunnelView,
    DashboardStatsView,
)

urlpatterns = [
    path("stats/", DashboardStatsView.as_view(), name="dashboard_stats"),
    path("funnel/", DashboardFunnelView.as_view(), name="dashboard_funnel"),
    path("activity/", DashboardActivityView.as_view(), name="dashboard_activity"),
]
