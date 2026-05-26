"""
NormalizedRecord — the clean, transformed version of a RawRecord.

Design:
- One NormalizedRecord per RawRecord (1:1 after normalization)
- Stores both the normalized values AND the transformation history
- Suspicious flags are set here, not on RawRecord
- ApprovalWorkflow tracks analyst review decisions
- Approved records become immutable (is_locked=True)
"""
from django.db import models
from apps.core.models import TenantModel


class EmissionScope(models.TextChoices):
    SCOPE_1 = "scope_1", "Scope 1 — Direct Emissions"
    SCOPE_2 = "scope_2", "Scope 2 — Indirect (Electricity)"
    SCOPE_3 = "scope_3", "Scope 3 — Value Chain"


class NormalizedRecord(TenantModel):
    """
    The normalized, analyst-reviewable version of a raw ingestion row.
    All values are in SI units: kg CO2e, kWh, km, dates as ISO 8601.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        LOCKED = "locked", "Audit Locked"
        FLAGGED = "flagged", "Flagged — Needs Review"

    raw_record = models.OneToOneField(
        "ingestion.RawRecord",
        on_delete=models.CASCADE,
        related_name="normalized",
    )
    batch = models.ForeignKey(
        "ingestion.UploadBatch",
        on_delete=models.CASCADE,
        related_name="normalized_records",
    )
    facility = models.ForeignKey(
        "organizations.Facility",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="normalized_records",
    )
    department = models.ForeignKey(
        "organizations.Department",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="normalized_records",
    )

    # ── Emission classification ───────────────────────────────────────────────
    scope = models.CharField(max_length=10, choices=EmissionScope.choices, db_index=True)
    emission_category = models.ForeignKey(
        "EmissionCategory",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="records",
    )
    source_type = models.CharField(max_length=20, db_index=True)

    # ── Normalized values (SI units) ──────────────────────────────────────────
    activity_value = models.DecimalField(
        max_digits=20, decimal_places=6,
        help_text="Normalized activity quantity (liters, kWh, km, nights)",
    )
    activity_unit = models.CharField(max_length=20, help_text="Normalized unit: L, kWh, km, nights")
    activity_date = models.DateField(db_index=True)
    activity_period_start = models.DateField(null=True, blank=True)
    activity_period_end = models.DateField(null=True, blank=True)

    # ── Emission factor applied ───────────────────────────────────────────────
    emission_factor = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True,
        help_text="kg CO2e per unit of activity",
    )
    emission_factor_source = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. IPCC 2021, DEFRA 2023, EPA 2023",
    )
    co2e_kg = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True,
        help_text="Calculated CO2e in kilograms",
    )

    # ── Source metadata ───────────────────────────────────────────────────────
    vendor_name = models.CharField(max_length=255, blank=True)
    cost_center = models.CharField(max_length=100, blank=True)
    document_reference = models.CharField(max_length=200, blank=True)
    original_unit = models.CharField(max_length=20, blank=True)
    original_value = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)

    # ── Workflow ──────────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    is_suspicious = models.BooleanField(default=False, db_index=True)
    is_locked = models.BooleanField(default=False, db_index=True)
    suspicious_reasons = models.JSONField(default=list)
    validation_errors = models.JSONField(default=list)
    transformation_log = models.JSONField(
        default=list,
        help_text="Ordered list of transformations applied: [{step, from, to, note}]",
    )

    class Meta:
        db_table = "normalized_records"
        ordering = ["-activity_date", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "scope", "status"]),
            models.Index(fields=["organization", "source_type", "activity_date"]),
            models.Index(fields=["batch", "status"]),
            models.Index(fields=["is_suspicious", "status"]),
        ]

    def __str__(self):
        return f"{self.scope} | {self.activity_value} {self.activity_unit} | {self.activity_date}"

    def lock(self):
        """Make this record immutable after audit approval."""
        if not self.is_locked:
            self.is_locked = True
            self.status = self.Status.LOCKED
            self.save(update_fields=["is_locked", "status"])


class EmissionCategory(models.Model):
    """
    Master list of GHG Protocol emission categories.
    e.g. Scope 1 — Stationary Combustion, Scope 3 Cat 6 — Business Travel
    """
    scope = models.CharField(max_length=10, choices=EmissionScope.choices)
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ghg_protocol_category = models.CharField(max_length=100, blank=True)
    source_types = models.JSONField(default=list, help_text="Which source types map to this category")

    class Meta:
        db_table = "emission_categories"
        ordering = ["scope", "code"]

    def __str__(self):
        return f"{self.scope} — {self.name}"


class ApprovalWorkflow(TenantModel):
    """
    Tracks every analyst decision on a NormalizedRecord.
    Immutable — decisions are never deleted, only superseded.
    """
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        FLAGGED = "flagged", "Flagged for Review"
        ESCALATED = "escalated", "Escalated"

    normalized_record = models.ForeignKey(
        NormalizedRecord,
        on_delete=models.CASCADE,
        related_name="approvals",
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comment = models.TextField(blank=True)
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)

    class Meta:
        db_table = "approval_workflows"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["normalized_record", "created_at"])]

    def __str__(self):
        return f"{self.decision} by {self.created_by} on {self.created_at:%Y-%m-%d}"
