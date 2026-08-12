from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    groups_led = serializers.SerializerMethodField()
    groups_member_of = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "leader_role", "demography", "gender", "area", "contact_number", "is_staff",
            "groups_led", "groups_member_of",
        ]
        read_only_fields = ["id", "is_staff"]

    def get_groups_led(self, obj):
        return list(obj.groups_led.values_list("name", flat=True))

    def get_groups_member_of(self, obj):
        return list(
            obj.group_memberships.select_related("group").values_list("group__name", flat=True)
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "password",
            "leader_role", "demography", "gender", "area", "contact_number",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
