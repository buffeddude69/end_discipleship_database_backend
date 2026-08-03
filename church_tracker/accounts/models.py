from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    A group leader's account. Extends Django's built-in user so we
    still get auth, permissions, admin support, etc. for free.
    """

    class LeaderRole(models.TextChoices):
        SMALL_GROUP_LEADER = "small_group_leader", "Small Group Leader"
        LEADERSHIP_GROUP_LEADER = "leadership_group_leader", "Leadership Group Leader"
        CAMPUS_MISSIONARY = "campus_missionary", "Campus Missionary"

    class Demography(models.TextChoices):
        STUDENT_YOUTH = "student_youth", "Student / Youth"
        SINGLE_YOUNG_PRO = "single_young_professional", "Single / Young Professional"
        MARRIED = "married", "Married"
        PARENT = "parent", "Parent"
        SENIOR = "senior", "Senior"

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    class Area(models.TextChoices):
        BINAN = "binan", "Binan"
        NUVALI = "nuvali", "Nuvali"
        SANTA_ROSA_CITY = "santa_rosa_city", "Santa Rosa City"

    leader_role = models.CharField(max_length=30, choices=LeaderRole.choices)
    demography = models.CharField(max_length=30, choices=Demography.choices)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    area = models.CharField(
        max_length=20, choices=Area.choices, default=Area.BINAN,
        help_text="Which area this leader is assigned to for discipling students.",
    )
    contact_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_leader_role_display()})"
