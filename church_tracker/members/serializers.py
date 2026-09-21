from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import DiscipleshipStage, GroupMembership, Member, Ministry, School

User = get_user_model()


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
        fields = ["id", "name", "area", "demography"]


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
            "is_doing_one_on_one", "one_on_one_with",
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
    Links a person to a Group -- either an existing Member profile, or
    an existing Leader account (common for leadership groups, whose
    "members" are often other leaders). Used both when adding someone
    to a group and when updating their monthly attendance status.
    """
    member_detail = MemberSerializer(source="member", read_only=True)
    leader = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    leader_detail = UserSerializer(source="leader", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    needs_update = serializers.SerializerMethodField()
    person_name = serializers.SerializerMethodField()
    person_type = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = [
            "id", "group", "group_name",
            "member", "member_detail", "leader", "leader_detail",
            "person_name", "person_type",
            "attendance_status",
            "date_joined_group", "status_updated_at", "needs_update",
        ]
        read_only_fields = ["id", "date_joined_group", "status_updated_at"]
        extra_kwargs = {"member": {"required": False, "allow_null": True}}
        # DRF auto-generates a UniqueTogetherValidator per unique_together
        # tuple on the model. For ["group", "leader"], that validator force-
        # requires "leader" on every submission (even a member-only one),
        # which breaks the "exactly one of member/leader" design. Our own
        # validate() below already handles duplicate-membership checking
        # correctly, so we disable the auto-generated ones here. The model's
        # unique_together and CheckConstraint still protect data integrity
        # at the database level regardless.
        validators = []

    def get_needs_update(self, obj):
        now = timezone.now()
        return not (obj.status_updated_at.year == now.year and obj.status_updated_at.month == now.month)

    def get_person_name(self, obj):
        person = obj.member or obj.leader
        return f"{person.first_name} {person.last_name}" if person else ""

    def get_person_type(self, obj):
        return "leader" if obj.leader_id else "member"

    def validate_group(self, group):
        request = self.context["request"]
        if not request.user.is_staff and group.leader_id != request.user.id:
            raise serializers.ValidationError("You can only manage members in your own group.")
        return group

    def validate(self, attrs):
        member = attrs.get("member", getattr(self.instance, "member", None))
        leader = attrs.get("leader", getattr(self.instance, "leader", None))

        if member and leader:
            raise serializers.ValidationError(
                "Choose either an existing member profile or a leader account, not both."
            )
        if not member and not leader:
            raise serializers.ValidationError(
                "Choose an existing member profile or a leader account to add to this group."
            )

        group = attrs.get("group", getattr(self.instance, "group", None))
        qs = GroupMembership.objects.filter(group=group)
        qs = qs.filter(member=member) if member else qs.filter(leader=leader)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This person is already in this group.")

        return attrs

    def _touch_member(self, instance):
        # Updating someone's attendance status in a group is a real,
        # meaningful review of that person -- it should count as "checked
        # on them this month" from the Members list's point of view too,
        # not just within this one group. Without this, the two "needs
        # update" indicators (profile vs. per-group attendance) drift out
        # of sync, which is confusing since a leader reasonably thinks of
        # updating someone's status as "I updated their record."
        if instance.member_id:
            instance.member.save(update_fields=["updated_at"])

    def create(self, validated_data):
        instance = super().create(validated_data)
        self._touch_member(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self._touch_member(instance)
        return instance
