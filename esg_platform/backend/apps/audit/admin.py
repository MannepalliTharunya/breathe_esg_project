from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user_email", "action", "resource_type", "resource_id", "ip_address", "created_at"]
    list_filter = ["action", "resource_type"]
    search_fields = ["user_email", "resource_type", "resource_id"]
    readonly_fields = [f.name for f in AuditLog._meta.get_fields() if hasattr(f, "name")]
    ordering = ["-created_at"]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
