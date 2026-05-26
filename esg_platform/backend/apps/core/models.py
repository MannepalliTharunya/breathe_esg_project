"""
Abstract base models used across the entire platform.
Every model inherits from BaseModel for consistent audit fields.
"""
import uuid
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    UUID PK + full audit trail on every record.
    created_by / updated_by are nullable to support system-generated records.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Caller should pass current_user= kwarg for audit tracking
        current_user = kwargs.pop("current_user", None)
        if current_user and current_user.is_authenticated:
            if not self.pk:
                self.created_by = current_user
            self.updated_by = current_user
        super().save(*args, **kwargs)


class TenantModel(BaseModel):
    """
    Extends BaseModel with mandatory organization FK.
    All tenant-scoped data inherits from this.
    """
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )

    class Meta:
        abstract = True
