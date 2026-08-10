from django.utils import timezone
from rest_framework import serializers

from .models import DiscipleshipStage, GroupMembership, Member, Ministry, School


class MinistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ministry
        fields = ["id", "name"]


class DiscipleshipStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscipleshipStage
        fields = ["id", "name", "order"]


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name"]


class MemberSerializer(serializers.ModelSerializer):
    """
    The shared student/member profile -- independent of any one group.
    """
    discipleship_stage_name = serializers.CharField(
        source="discipleship_stage.name", read_only=True, default=None
    )
    ministry_names = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    needs_update = serializers.SerializerMethodField()
    group_names = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id", "first_name", "last_name", "gender", "role", "year_level",
            "school", "school_name",
            "is_in_ministry", "ministries", "ministry_names",
            "discipleship_stage", "discipleship_stage_name",
            "remarks", "remarks_photo",
            "needs_update", "group_names",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_ministry_names(self, obj):
        return [m.name for m in obj.ministries.all()]

    def get_needs_update(self, obj):
        now = timezone.now()
        return not (obj.updated_at.year == now.year and obj.updated_at.month == now.month)

    def get_group_names(self, obj):
        return [gm.group.name for gm in obj.memberships.select_related("group").all()]

    def validate(self, attrs):
        # Prevent creating a second profile for the same person. Names are
        # compared case-insensitively and with surrounding whitespace
        # trimmed, since "juan dela cruz " and "Juan Dela Cruz" are almost
        # certainly the same person, not two different ones.
        first_name = attrs.get("first_name", getattr(self.instance, "first_name", None))
        last_name = attrs.get("last_name", getattr(self.instance, "last_name", None))

        if first_name and last_name:
            qs = Member.objects.filter(
                first_name__iexact=first_name.strip(),
                last_name__iexact=last_name.strip(),
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "A member profile with this name already exists. "
                    "Please search the existing members list instead of creating a duplicate."
                )

        return attrs


class GroupMembershipSerializer(serializers.ModelSerializer):
    """
    Links an existing Member profile to a Group. Used both when adding
    a member to a group (picking an existing profile, or one just
    created) and when updating their monthly attendance status.
    """
    member_detail = MemberSerializer(source="member", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    needs_update = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = [
            "id", "group", "group_name", "member", "member_detail",
            "attendance_status",
            "date_joined_group", "status_updated_at", "needs_update",
        ]
        read_only_fields = ["id", "date_joined_group", "status_updated_at"]

    def get_needs_update(self, obj):
        now = timezone.now()
        return not (obj.status_updated_at.year == now.year and obj.status_updated_at.month == now.month)

    def validate_group(self, group):
        request = self.context["request"]
        if not request.user.is_staff and group.leader_id != request.user.id:
            raise serializers.ValidationError("You can only manage members in your own group.")
        return group
