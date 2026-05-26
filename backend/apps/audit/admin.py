from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user_email", "action", "resource_type", "resource_id", "ip_address", "status_code", "created_at"]
    list_filter = ["action", "resource_type", "status_code"]
    search_fields = ["user_email", "resource_type", "resource_id", "request_path"]
    readonly_fields = [f.name for f in AuditLog._meta.get_fields()]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
