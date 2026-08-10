from django.db import models

from groups.models import Group


class Ministry(models.Model):
    """
    Configurable lookup table for ministry teams a member can serve in
    (e.g. Music, Technical/TSM, Ushering, Prayer Team). Kept as a model
    rather than hardcoded choices since new ministry teams get added
    over time and shouldn't require a code change.
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "ministries"

    def __str__(self):
        return self.name


class DiscipleshipStage(models.Model):
    """
    Configurable lookup table for the ministry's discipleship journey
    stages (e.g. New Believer, Growing, Committed, Leader-in-training).
    Kept as a model instead of hardcoded choices because these labels
    are specific to the organization and may change over time.
    """

    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(
        default=0, help_text="Controls display order in the journey sequence."
    )

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class School(models.Model):
    """
    Configurable lookup table for schools/campuses a member may be
    attending. Staff manage this list (e.g. adding a new campus),
    rather than leaders free-typing institution names inconsistently.
    Also used for members who aren't students (e.g. an "N/A" entry).
    """

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    A single shared profile for a person being discipled. This is
    intentionally NOT owned by one group -- a person has exactly one
    profile, and that profile can be linked to one or more groups via
    GroupMembership. This avoids leaders accidentally creating
    duplicate profiles for the same person across different groups.
    """

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    class Role(models.TextChoices):
        MEMBER = "member", "Member"
        INTERN = "intern", "Intern"

    class YearLevel(models.TextChoices):
        ELEMENTARY = "elementary", "Elementary"
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
        OUT_OF_SCHOOL = "out_of_school", "Out of School"
        ADULT = "adult", "Adult"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.MEMBER,
        help_text="Whether this person is a regular member or an intern being developed. "
                  "People who are already Leaders have their own Leader account instead of "
                  "a Member profile, so 'Leader' isn't an option here.",
    )
    year_level = models.CharField(max_length=20, choices=YearLevel.choices)
    school = models.ForeignKey(
        School, on_delete=models.PROTECT, related_name="members",
        help_text="Use an 'N/A' school entry for members who aren't students.",
    )

    is_in_ministry = models.BooleanField(
        default=False, help_text="Whether this member is also serving within the ministry."
    )
    ministries = models.ManyToManyField(
        Ministry, blank=True, related_name="members",
        help_text="Which ministry team(s) this member serves in, if any.",
    )
    discipleship_stage = models.ForeignKey(
        DiscipleshipStage, on_delete=models.SET_NULL, null=True, blank=True, related_name="members"
    )

    remarks = models.TextField(
        blank=True, help_text="An encouraging note or story about this member, from their leader."
    )
    remarks_photo = models.ImageField(upload_to="member_remarks/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class GroupMembership(models.Model):
    """
    Links a Member profile to a Group, tracking their attendance for the
    current month within that group. A member can belong to more than
    one group at once (e.g. a small group AND a leadership group).
    Their role (member/intern/leader) lives on the Member profile
    itself, not here -- it's one designation per person, not per group.
    """

    class AttendanceStatus(models.TextChoices):
        NEW = "new", "New (joined this month)"
        ACTIVE = "active", "Active (attended at least once this month)"
        INACTIVE = "inactive", "Inactive (no attendance this month)"

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="memberships")

    attendance_status = models.CharField(max_length=10, choices=AttendanceStatus.choices)

    date_joined_group = models.DateField(auto_now_add=True)
    # Updated automatically whenever this record is saved -- used to flag
    # memberships whose attendance status hasn't been reviewed this month.
    status_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["group", "member"]
        ordering = ["member__last_name", "member__first_name"]

    def __str__(self):
        return f"{self.member} in {self.group}"
