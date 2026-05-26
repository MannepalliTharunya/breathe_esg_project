from django.contrib import admin
from django.utils.html import format_html
from .models import NormalizedRecord, ApprovalWorkflow, EmissionCategory


@admin.register(EmissionCategory)
class EmissionCategoryAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "scope", "ghg_protocol_category"]
    list_filter = ["scope"]
    search_fields = ["code", "name"]


class ApprovalInline(admin.TabularInline):
    model = ApprovalWorkflow
    extra = 0
    fields = ["decision", "comment", "previous_status", "new_status", "created_by", "created_at"]
    readonly_fields = fields
    can_delete = False


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
    inlines = [ApprovalInline]
    list_display = [
        "id_short", "organization", "scope", "source_type",
        "activity_value", "activity_unit", "activity_date",
        "status", "suspicious_flag", "is_locked", "created_at",
    ]
    list_filter = ["scope", "source_type", "status", "is_suspicious", "is_locked", "organization"]
    search_fields = ["vendor_name", "cost_center", "document_reference"]
    readonly_fields = [
        "id", "raw_record", "batch", "scope", "source_type",
        "activity_value", "activity_unit", "activity_date",
        "original_value", "original_unit",
        "suspicious_reasons", "validation_errors", "transformation_log",
        "is_locked", "created_at", "updated_at",
    ]
    ordering = ["-created_at"]

    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = "ID"

    def suspicious_flag(self, obj):
        if obj.is_suspicious:
            return format_html('<span style="color:red;font-weight:bold;">⚠ Suspicious</span>')
        return "—"
    suspicious_flag.short_description = "Suspicious"

    def has_add_permission(self, request):
        return False


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ["normalized_record", "decision", "created_by", "created_at"]
    list_filter = ["decision"]
    readonly_fields = ["id", "normalized_record", "decision", "comment",
                       "previous_status", "new_status", "created_by", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
