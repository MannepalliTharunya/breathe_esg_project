from django.contrib import admin
from .models import Organization, Facility, OrganizationMembership


class FacilityInline(admin.TabularInline):
    model = Facility
    extra = 0
    fields = ["name", "facility_type", "city", "country", "is_active"]


class MembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    fields = ["user", "role", "is_active", "joined_at"]
    readonly_fields = ["joined_at"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [FacilityInline, MembershipInline]
    list_display = ["name", "industry", "country", "subscription_tier", "is_active", "created_at"]
    list_filter = ["industry", "subscription_tier", "is_active"]
    search_fields = ["name", "legal_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "facility_type", "city", "country", "is_active"]
    list_filter = ["facility_type", "is_active"]
    search_fields = ["name", "organization__name", "city"]


@admin.register(OrganizationMembership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "role", "is_active", "joined_at"]
    list_filter = ["role", "is_active"]
    search_fields = ["user__email", "organization__name"]
