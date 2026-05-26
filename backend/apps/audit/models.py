"""
Immutable audit log — every significant action is recorded here.
"""
from django.db import models
from apps.core.models import UUIDModel, TimeStampedModel


class AuditLog(UUIDModel, TimeStampedModel):
    """
    Append-only audit trail. Never update or delete records.
    """

    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        EXPORT = "export", "Export"
        APPROVE = "approve", "Approve"
        REJECT = "reject", "Reject"
        PUBLISH = "publish", "Publish"
        IMPORT = "import", "Import"

    user_id = models.UUIDField(null=True, db_index=True)
    user_email = models.EmailField(blank=True)
    organization_id = models.UUIDField(null=True, db_index=True)
    action = models.CharField(max_length=20, choices=Action.choices, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    changes = models.JSONField(default=dict, help_text="Before/after snapshot of changed fields")
    metadata = models.JSONField(default=dict)
    status_code = models.PositiveSmallIntegerField(null=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id", "created_at"]),
            models.Index(fields=["organization_id", "action", "created_at"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_email} | {self.action} | {self.resource_type} | {self.created_at}"
