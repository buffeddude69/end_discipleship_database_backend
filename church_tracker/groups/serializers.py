from rest_framework import serializers

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source="leader.get_full_name", read_only=True)
    member_count = serializers.IntegerField(source="memberships.count", read_only=True)
    active_member_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id", "name", "leader", "leader_name", "group_type",
            "gender_composition", "meeting_frequency", "meeting_frequency_note",
            "meeting_day", "meeting_time", "venue", "is_active",
            "member_count", "active_member_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"leader": {"required": False}}

    def get_active_member_count(self, obj):
        return obj.memberships.filter(attendance_status="active").count()
