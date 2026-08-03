from django.contrib import admin

from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "leader", "group_type", "is_active", "meeting_day", "meeting_time")
    list_filter = ("group_type", "gender_composition", "is_active")
    search_fields = ("name", "leader__username", "leader__first_name", "leader__last_name")
