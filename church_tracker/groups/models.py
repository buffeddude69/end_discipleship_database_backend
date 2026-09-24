from django.conf import settings
from django.db import models


class Group(models.Model):

    class GroupType(models.TextChoices):
        SMALL_GROUP = "small_group", "Small Group"
        LEADERSHIP_GROUP = "leadership_group", "Leadership Group"
        CAMPUS_MINISTRY = "campus_ministry", "Campus Ministry"

    class GenderComposition(models.TextChoices):
        MEN = "men", "Men"
        WOMEN = "women", "Women"
        MIXED = "mixed", "Mixed"

    class MeetingFrequency(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        OTHER = "other", "Other"

    class MeetingDay(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"

    class GroupDemography(models.TextChoices):
        HIGH_SCHOOL = "high_school", "High School"
        COLLEGE = "college", "College"
        MIXED = "mixed", "Mixed"
        OTHERS = "others", "Others"

    name = models.CharField(max_length=150)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="groups_led",
    )
    group_type = models.CharField(max_length=20, choices=GroupType.choices)
    demography = models.CharField(
        max_length=20, choices=GroupDemography.choices, default=GroupDemography.MIXED,
        help_text="What kind of group this is, demographically.",
    )
    demography_other = models.CharField(
        max_length=100, blank=True,
        help_text="Required when demography is 'Others' -- describe it.",
    )
    gender_composition = models.CharField(
        max_length=10, choices=GenderComposition.choices, default=GenderComposition.MIXED
    )
    meeting_frequency = models.CharField(
        max_length=10, choices=MeetingFrequency.choices, default=MeetingFrequency.WEEKLY
    )
    meeting_frequency_note = models.CharField(
        max_length=100, blank=True, help_text="Free-text detail, e.g. 'every 2nd Saturday'."
    )
    meeting_day = models.CharField(max_length=10, choices=MeetingDay.choices, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=255, blank=True)

    # Whether the group itself is currently considered active.
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"
