from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Leader Info", {"fields": ("leader_role", "demography", "gender", "contact_number")}),
    )
    list_display = ("username", "first_name", "last_name", "leader_role", "gender", "is_active")
    list_filter = ("leader_role", "demography", "gender")


admin.site.register(User, UserAdmin)
