from django.contrib import admin
from .models import UploadBatch, RawRecord


class RawRecordInline(admin.TabularInline):
    model = RawRecord
    extra = 0
    fields = ["row_number", "source_type", "status", "parse_errors"]
    readonly_fields = fields
    max_num = 20
    can_delete = False


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    inlines = [RawRecordInline]
    list_display = [
        "original_filename", "organization", "source_type", "status",
        "total_rows", "failed_rows", "suspicious_rows", "created_by", "created_at",
    ]
    list_filter = ["source_type", "status", "organization"]
    search_fields = ["original_filename", "organization__name"]
    readonly_fields = [
        "id", "status", "total_rows", "processed_rows", "failed_rows",
        "suspicious_rows", "error_summary", "processing_started_at",
        "processing_completed_at", "created_at", "updated_at",
    ]
    ordering = ["-created_at"]


@admin.register(RawRecord)
class RawRecordAdmin(admin.ModelAdmin):
    list_display = ["row_number", "batch", "source_type", "status", "created_at"]
    list_filter = ["source_type", "status"]
    search_fields = ["batch__original_filename"]
    readonly_fields = ["id", "batch", "row_number", "raw_data", "source_type", "status", "parse_errors", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
