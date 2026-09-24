from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DiscipleshipStage, GroupMembership, Member, Ministry, School
from .serializers import (
    DiscipleshipStageSerializer,
    GroupMembershipSerializer,
    MemberSerializer,
    MinistrySerializer,
    SchoolSerializer,
)


class IsStaffOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can view; only staff can create/edit/delete."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


def _current_month_bounds():
    now = timezone.now()
    return now.year, now.month


class MemberViewSet(viewsets.ModelViewSet):
    """
    Shared student/member profiles. Visible to every authenticated
    leader, editable by any authenticated leader too, since a
    profile isn't "owned" by a single group.
    """
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Member.objects.select_related("school", "discipleship_stage").prefetch_related(
            "ministries", "memberships__group"
        )

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))

        school_id = self.request.query_params.get("school")
        if school_id:
            qs = qs.filter(school_id=school_id)

        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)

        needs_update = self.request.query_params.get("needs_update")
        if needs_update == "true":
            year, month = _current_month_bounds()
            qs = qs.exclude(updated_at__year=year, updated_at__month=month)

        meeting_day = self.request.query_params.get("meeting_day")
        if meeting_day:
            qs = qs.filter(memberships__group__meeting_day=meeting_day)

        return qs.distinct()


class GroupMembershipViewSet(viewsets.ModelViewSet):
    """
    Links a person (Member profile or Leader account) to a Group, with
    this month's attendance status.
    """
    serializer_class = GroupMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = GroupMembership.objects.select_related(
            "group", "member", "member__school", "member__discipleship_stage", "leader"
        ).prefetch_related("member__ministries")

        if not user.is_staff:
            qs = qs.filter(group__leader=user)

        group_id = self.request.query_params.get("group")
        if group_id:
            qs = qs.filter(group_id=group_id)

        attendance_status = self.request.query_params.get("attendance_status")
        if attendance_status:
            qs = qs.filter(attendance_status=attendance_status)

        role = self.request.query_params.get("role")
        if role == "leader":
            qs = qs.filter(leader__isnull=False)
        elif role:
            qs = qs.filter(member__role=role)

        school_id = self.request.query_params.get("school")
        if school_id:
            qs = qs.filter(member__school_id=school_id)

        meeting_day = self.request.query_params.get("meeting_day")
        if meeting_day:
            qs = qs.filter(group__meeting_day=meeting_day)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(member__first_name__icontains=search) | Q(member__last_name__icontains=search)
                | Q(leader__first_name__icontains=search) | Q(leader__last_name__icontains=search)
            )

        needs_update = self.request.query_params.get("needs_update")
        if needs_update == "true":
            year, month = _current_month_bounds()
            qs = qs.exclude(status_updated_at__year=year, status_updated_at__month=month)

        return qs.distinct()

    """Below are only authenticated leader can view; only staff can add/edit/delete."""


class DiscipleshipStageViewSet(viewsets.ModelViewSet):
    
    queryset = DiscipleshipStage.objects.all()
    serializer_class = DiscipleshipStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


class MinistryViewSet(viewsets.ModelViewSet):
    """Any authenticated leader can view; only staff can add/edit/delete ministries."""
    queryset = Ministry.objects.all()
    serializer_class = MinistrySerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


class SchoolViewSet(viewsets.ModelViewSet):
    """
    Publicly readable. Only staff can
    add/edit/delete.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsStaffOrReadOnly]


class DashboardView(APIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        User = request.user.__class__
        memberships = GroupMembership.objects.select_related("member", "member__school", "group", "group__leader")

        by_role = {
            "member": Member.objects.filter(role="member").count(),
            "intern": Member.objects.filter(role="intern").count(),
        }

        by_status = {
            "new": memberships.filter(attendance_status="new").count(),
            "active": memberships.filter(attendance_status="active").count(),
            "inactive": memberships.filter(attendance_status="inactive").count(),
        }

        by_school = {}
        for school in School.objects.all():
            count = Member.objects.filter(school=school).count()
            if count:
                by_school[school.name] = count

        by_area = {}
        for area_value, area_label in User.Area.choices:
            count = memberships.filter(group__leader__area=area_value).distinct().values("member").count()
            if count:
                by_area[area_label] = count

        leaders_by_area = {}
        for area_value, area_label in User.Area.choices:
            count = User.objects.filter(area=area_value).count()
            if count:
                leaders_by_area[area_label] = count

        return Response({
            "total_members": Member.objects.count(),
            "total_memberships": memberships.count(),
            "total_leaders": User.objects.count(),
            "by_role": by_role,
            "by_attendance_status": by_status,
            "by_school": by_school,
            "by_area": by_area,
            "leaders_by_area": leaders_by_area,
        })
