"""
Immutable audit log. Every significant action is recorded here.
Records are never updated or deleted — append-only.
"""
import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Append-only audit trail for all data mutations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        null=True, on_delete=models.SET_NULL,
        related_name="audit_logs", db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    user_email = models.EmailField(blank=True)
    action = models.CharField(max_length=100, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.CharField(max_length=100, blank=True, db_index=True)
    before_value = models.JSONField(default=dict)
    after_value = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    source_system = models.CharField(max_length=100, default="web_ui")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "action", "created_at"]),
            models.Index(fields=["resource_type", "resource_id"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user_email} | {self.action} | {self.resource_type} | {self.created_at:%Y-%m-%d %H:%M}"
