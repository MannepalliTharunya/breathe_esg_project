from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User


class DataIntegration(BaseModel):
    """External data source integration (ERP, IoT, utility APIs, etc.)."""

    class IntegrationType(models.TextChoices):
        REST_API = "rest_api", "REST API"
        SFTP = "sftp", "SFTP"
        DATABASE = "database", "Database"
        WEBHOOK = "webhook", "Webhook"
        MANUAL_UPLOAD = "manual_upload", "Manual Upload"

    class SyncStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        ERROR = "error", "Error"
        PENDING = "pending", "Pending"

    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="integrations")
    name = models.CharField(max_length=200)
    integration_type = models.CharField(max_length=20, choices=IntegrationType.choices)
    sync_status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING)
    config = models.JSONField(default=dict, help_text="Encrypted connection config")
    field_mappings = models.JSONField(default=dict, help_text="Maps source fields to ESG metric codes")
    sync_frequency = models.CharField(max_length=50, default="daily")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_records = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "data_integrations"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.organization.name} — {self.name} ({self.integration_type})"
