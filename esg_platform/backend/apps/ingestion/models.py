"""
Ingestion models: UploadBatch → RawRecord → (feeds normalization)

Design decisions:
- UploadBatch is the unit of work. One CSV = one batch.
- RawRecord stores the original row verbatim as JSON — never mutated.
- Normalization creates a separate NormalizedRecord linked to RawRecord.
- This gives full lineage: normalized ← raw ← batch ← upload.
"""
import uuid
from django.db import models
from apps.core.models import TenantModel


class UploadBatch(TenantModel):
    """
    Represents a single file upload event.
    Tracks the full lifecycle from upload → processing → completion.
    """
    class SourceType(models.TextChoices):
        SAP = "sap", "SAP Fuel & Procurement"
        UTILITY = "utility", "Utility Electricity"
        TRAVEL = "travel", "Corporate Travel"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PARTIAL = "partial", "Partial (some rows failed)"

    source_type = models.CharField(max_length=20, choices=SourceType.choices, db_index=True)
    original_filename = models.CharField(max_length=500)
    file = models.FileField(upload_to="uploads/%Y/%m/")
    file_size_bytes = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    # Counters updated as processing progresses
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    suspicious_rows = models.PositiveIntegerField(default=0)

    # Metadata
    facility = models.ForeignKey(
        "organizations.Facility", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="upload_batches",
    )
    notes = models.TextField(blank=True)
    error_summary = models.TextField(blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "upload_batches"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "source_type", "status"]),
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self):
        return f"{self.source_type} | {self.original_filename} | {self.status}"

    @property
    def success_rate(self):
        if not self.total_rows:
            return 0
        return round((self.processed_rows - self.failed_rows) / self.total_rows * 100, 1)


class RawRecord(TenantModel):
    """
    Immutable store of a single CSV row exactly as uploaded.
    raw_data is the original dict from the CSV parser — never modified.
    This is the source of truth for audit purposes.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Normalization"
        NORMALIZED = "normalized", "Normalized"
        FAILED = "failed", "Normalization Failed"
        SKIPPED = "skipped", "Skipped (duplicate)"

    batch = models.ForeignKey(UploadBatch, on_delete=models.CASCADE, related_name="raw_records")
    row_number = models.PositiveIntegerField(help_text="1-based row number in the source file")
    raw_data = models.JSONField(help_text="Original CSV row as key-value dict")
    source_type = models.CharField(max_length=20, choices=UploadBatch.SourceType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    parse_errors = models.JSONField(default=list, help_text="List of parsing error messages")

    class Meta:
        db_table = "raw_records"
        ordering = ["batch", "row_number"]
        indexes = [
            models.Index(fields=["batch", "status"]),
            models.Index(fields=["organization", "source_type", "status"]),
        ]

    def __str__(self):
        return f"Row {self.row_number} | {self.batch.original_filename}"
