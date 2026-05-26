from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserPreferences


class UserPreferencesInline(admin.StackedInline):
    model = UserPreferences
    can_delete = False
    verbose_name_plural = "Preferences"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserPreferencesInline]
    list_display = ["email", "full_name", "role", "is_active", "is_verified", "created_at"]
    list_filter = ["role", "is_active", "is_verified", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login_ip"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "job_title", "department", "avatar")}),
        ("Role & Status", {"fields": ("role", "is_active", "is_verified", "is_staff", "is_superuser")}),
        ("Security", {"fields": ("mfa_enabled", "last_login_ip", "failed_login_attempts", "locked_until")}),
        ("Preferences", {"fields": ("timezone", "locale")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "role"),
        }),
    )
