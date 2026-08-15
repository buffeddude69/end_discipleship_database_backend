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
        HIGH_SCHOOL = "high_school", "High School"
        COLLEGE = "college", "College"
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

    class YearLevel(models.TextChoices):
        GRADE_7 = "grade_7", "Grade 7"
        GRADE_8 = "grade_8", "Grade 8"
        GRADE_9 = "grade_9", "Grade 9"
        GRADE_10 = "grade_10", "Grade 10"
        GRADE_11 = "grade_11", "Grade 11"
        GRADE_12 = "grade_12", "Grade 12"
        COLLEGE_1 = "college_1", "1st Year College"
        COLLEGE_2 = "college_2", "2nd Year College"
        COLLEGE_3 = "college_3", "3rd Year College"
        COLLEGE_4 = "college_4", "4th Year College"
        COLLEGE_5_PLUS = "college_5_plus", "5th+ Year College"

    leader_role = models.CharField(max_length=30, choices=LeaderRole.choices)
    demography = models.CharField(max_length=30, choices=Demography.choices)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    area = models.CharField(
        max_length=20, choices=Area.choices, default=Area.BINAN,
        help_text="Which area this leader is assigned to for discipling students.",
    )
    contact_number = models.CharField(max_length=20, blank=True)

    year_level = models.CharField(
        max_length=20, choices=YearLevel.choices, blank=True,
        help_text="Required when demography is High School or College.",
    )
    school = models.ForeignKey(
        "members.School", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_leaders",
        help_text="Required when demography is High School or College.",
    )

    STUDENT_DEMOGRAPHIES = (Demography.HIGH_SCHOOL, Demography.COLLEGE)

    @property
    def is_student(self):
        """Derived from demography -- no separate field, so there's only one place to update this."""
        return self.demography in self.STUDENT_DEMOGRAPHIES

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_leader_role_display()})"
