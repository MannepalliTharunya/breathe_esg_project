from django.contrib import admin
from .models import Framework, FrameworkRequirement, OrganizationFramework


class RequirementInline(admin.TabularInline):
    model = FrameworkRequirement
    extra = 0
    fields = ["code", "title", "category", "is_mandatory"]


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    inlines = [RequirementInline]
    list_display = ["code", "name", "version", "issuing_body", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "name"]


@admin.register(FrameworkRequirement)
class FrameworkRequirementAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "framework", "category", "is_mandatory"]
    list_filter = ["framework", "category", "is_mandatory"]
    search_fields = ["code", "title"]
    filter_horizontal = ["linked_metrics"]


@admin.register(OrganizationFramework)
class OrganizationFrameworkAdmin(admin.ModelAdmin):
    list_display = ["organization", "framework", "adopted_at", "is_primary", "compliance_score"]
    list_filter = ["is_primary", "framework"]
