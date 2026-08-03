from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardView,
    DiscipleshipStageViewSet,
    GroupMembershipViewSet,
    MemberViewSet,
    MinistryViewSet,
    SchoolViewSet,
)

router = DefaultRouter()
router.register("members", MemberViewSet, basename="member")
router.register("group-memberships", GroupMembershipViewSet, basename="group-membership")
router.register("discipleship-stages", DiscipleshipStageViewSet, basename="discipleship-stage")
router.register("ministries", MinistryViewSet, basename="ministry")
router.register("schools", SchoolViewSet, basename="school")

urlpatterns = router.urls + [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
