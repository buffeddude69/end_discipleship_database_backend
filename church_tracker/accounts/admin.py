from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Leader Info", {
            "fields": ("leader_role", "demography", "gender", "area", "contact_number"),
        }),
        ("Student Status (shown when demography is High School or College)", {
            "fields": ("year_level", "school"),
        }),
        ("One2One", {
            "fields": ("is_doing_one_on_one", "one_on_one_with"),
        }),
    )
    list_display = (
        "username", "first_name", "last_name", "leader_role", "area", "is_student",
        "is_doing_one_on_one", "is_active",
    )
    list_filter = ("leader_role", "demography", "gender", "area", "is_doing_one_on_one")


admin.site.register(User, UserAdmin)
