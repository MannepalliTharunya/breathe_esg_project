from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "report_type", "status", "generated_at", "created_at"]
    list_filter = ["report_type", "status"]
    search_fields = ["name", "organization__name"]
    readonly_fields = ["id", "created_at", "updated_at", "generated_at", "file_url", "file_size_bytes"]
    ordering = ["-created_at"]
