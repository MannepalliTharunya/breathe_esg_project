from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User


class Notification(BaseModel):
    class NotificationType(models.TextChoices):
        DATA_SUBMITTED = "data_submitted", "Data Submitted"
        DATA_APPROVED = "data_approved", "Data Approved"
        DATA_REJECTED = "data_rejected", "Data Rejected"
        REPORT_READY = "report_ready", "Report Ready"
        TARGET_ALERT = "target_alert", "Target Alert"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read", "created_at"])]

    def mark_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])
        
