from django.contrib import admin

from .models import DiscipleshipStage, GroupMembership, Member, Ministry, School


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "first_name", "last_name", "role", "gender", "year_level", "school",
        "ministry_list", "discipleship_stage", "updated_at",
    )
    list_filter = ("role", "gender", "year_level", "school", "discipleship_stage")
    search_fields = ("first_name", "last_name")
    filter_horizontal = ("ministries",)

    @admin.display(description="Ministries")
    def ministry_list(self, obj):
        return ", ".join(m.name for m in obj.ministries.all())


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("person", "group", "attendance_status", "status_updated_at")
    list_filter = ("attendance_status", "group")
    search_fields = (
        "member__first_name", "member__last_name",
        "leader__first_name", "leader__last_name",
        "group__name",
    )

    @admin.display(description="Person")
    def person(self, obj):
        person = obj.member or obj.leader
        tag = " (Leader)" if obj.leader_id else ""
        return f"{person}{tag}"


@admin.register(DiscipleshipStage)
class DiscipleshipStageAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "area", "demography")
    search_fields = ("name", "area", "demography")
