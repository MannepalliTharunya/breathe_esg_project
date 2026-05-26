from django.contrib import admin
from .models import DataIntegration


@admin.register(DataIntegration)
class DataIntegrationAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "integration_type", "sync_status", "last_sync_at", "last_sync_records"]
    list_filter = ["integration_type", "sync_status"]
    search_fields = ["name", "organization__name"]
    readonly_fields = ["id", "created_at", "updated_at", "last_sync_at", "last_sync_records", "last_error"]
    ordering = ["name"]
