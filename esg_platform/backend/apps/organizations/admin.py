from django.contrib import admin
from .models import Organization, Facility, Department, OrganizationMember


class FacilityInline(admin.TabularInline):
    model = Facility
    extra = 0
    fields = ["name", "code", "facility_type", "country", "is_active"]


class MemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0
    fields = ["user", "is_active", "joined_at"]
    readonly_fields = ["joined_at"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [FacilityInline, MemberInline]
    list_display = ["name", "industry", "country", "reporting_year", "is_active", "created_at"]
    list_filter = ["industry", "country", "is_active"]
    search_fields = ["name", "legal_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "organization", "facility_type", "country", "is_active"]
    list_filter = ["facility_type", "country", "is_active"]
    search_fields = ["name", "code", "organization__name"]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "organization", "facility", "is_active"]
    search_fields = ["name", "code"]
