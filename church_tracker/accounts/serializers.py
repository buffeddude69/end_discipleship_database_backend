from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


def validate_student_fields(attrs, instance=None):
    """
    Shared rule for both serializers below: student status is derived
    from demography (High School / College), not a separate field. If
    the resulting demography is one of those, year_level and school
    become required.
    """
    demography = attrs.get("demography", getattr(instance, "demography", None))
    year_level = attrs.get("year_level", getattr(instance, "year_level", ""))
    school = attrs.get("school", getattr(instance, "school", None))

    if demography in User.STUDENT_DEMOGRAPHIES and (not year_level or not school):
        raise serializers.ValidationError(
            "Year level and school/campus are required when demography is High School or College."
        )
    return attrs


class UserSerializer(serializers.ModelSerializer):
    groups_led = serializers.SerializerMethodField()
    groups_member_of = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True, default=None)
    is_student = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "leader_role", "demography", "gender", "area", "contact_number", "is_staff",
            "is_student", "year_level", "school", "school_name",
            "groups_led", "groups_member_of",
        ]
        read_only_fields = ["id", "is_staff"]

    def get_groups_led(self, obj):
        return list(obj.groups_led.values_list("name", flat=True))

    def get_groups_member_of(self, obj):
        return list(
            obj.group_memberships.select_related("group").values_list("group__name", flat=True)
        )

    def validate(self, attrs):
        return validate_student_fields(attrs, self.instance)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    is_student = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "password",
            "leader_role", "demography", "gender", "area", "contact_number",
            "is_student", "year_level", "school",
        ]

    def validate(self, attrs):
        return validate_student_fields(attrs, self.instance)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
