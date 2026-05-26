"""
Core ESG data models: metrics, data points, targets, and materiality.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel, SoftDeleteModel
from apps.users.models import User


class ESGCategory(models.TextChoices):
    ENVIRONMENTAL = "E", "Environmental"
    SOCIAL = "S", "Social"
    GOVERNANCE = "G", "Governance"


class DataStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PUBLISHED = "published", "Published"


class EmissionCategory(BaseModel):
    """classification of greenhouse gas or environmental emissions."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    scope = models.CharField(
        max_length=20,
        choices=[("scope1", "Scope 1"), ("scope2", "Scope 2"), ("scope3", "Scope 3"), ("other", "Other")],
        default="other",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "emission_categories"
        ordering = ["scope", "code"]

    def __str__(self) -> str:
        return f"[{self.scope}] {self.code} — {self.name}"


class MetricDefinition(BaseModel):
    """
    Master catalogue of ESG metrics (e.g. GHG Scope 1, Water Withdrawal).
    Shared across all organizations.
    """

    emission_category = models.ForeignKey(
        EmissionCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="metrics"
    )

    class Unit(models.TextChoices):
        TONNES_CO2E = "tCO2e", "Tonnes CO2e"
        MWH = "MWh", "Megawatt-hours"
        CUBIC_METERS = "m3", "Cubic Meters"
        PERCENTAGE = "%", "Percentage"
        NUMBER = "#", "Number"
        CURRENCY = "USD", "USD"
        RATIO = "ratio", "Ratio"
        HOURS = "hours", "Hours"
        TONNES = "tonnes", "Tonnes"

    category = models.CharField(max_length=1, choices=ESGCategory.choices, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    unit = models.CharField(max_length=20, choices=Unit.choices)
    data_type = models.CharField(
        max_length=20,
        choices=[("numeric", "Numeric"), ("text", "Text"), ("boolean", "Boolean"), ("percentage", "Percentage")],
        default="numeric",
    )
    is_required = models.BooleanField(default=False)
    calculation_guidance = models.TextField(blank=True)
    framework_mappings = models.JSONField(default=dict, help_text="Maps to GRI, SASB, TCFD, etc.")
    tags = models.JSONField(default=list)

    class Meta:
        db_table = "esg_metric_definitions"
        ordering = ["category", "code"]

    def __str__(self) -> str:
        return f"[{self.category}] {self.code} — {self.name}"


class ReportingPeriod(BaseModel):
    """A fiscal or calendar reporting period for an organization."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="reporting_periods"
    )
    name = models.CharField(max_length=100)
    period_type = models.CharField(
        max_length=20,
        choices=[("annual", "Annual"), ("quarterly", "Quarterly"), ("monthly", "Monthly")],
        default="annual",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_locked = models.BooleanField(default=False)

    class Meta:
        db_table = "esg_reporting_periods"
        unique_together = [("organization", "start_date", "end_date")]
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.organization} — {self.name}"


class ESGDataPoint(BaseModel, SoftDeleteModel):
    """
    A single ESG metric value for a given organization, period, and scope.
    This is the central fact table of the platform.
    """

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="data_points"
    )
    metric = models.ForeignKey(MetricDefinition, on_delete=models.PROTECT, related_name="data_points")
    reporting_period = models.ForeignKey(ReportingPeriod, on_delete=models.CASCADE, related_name="data_points")
    facility = models.ForeignKey(
        "organizations.Facility", on_delete=models.SET_NULL, null=True, blank=True, related_name="data_points"
    )

    # Value storage — numeric or text
    numeric_value = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    text_value = models.TextField(blank=True)
    boolean_value = models.BooleanField(null=True, blank=True)

    # Provenance
    status = models.CharField(max_length=20, choices=DataStatus.choices, default=DataStatus.DRAFT, db_index=True)
    data_source = models.CharField(max_length=100, blank=True)
    collection_method = models.CharField(
        max_length=30,
        choices=[("manual", "Manual"), ("automated", "Automated"), ("estimated", "Estimated"), ("calculated", "Calculated")],
        default="manual",
    )
    confidence_level = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Data confidence 0-100%",
    )
    notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list, help_text="List of S3 keys for supporting documents")

    # Workflow
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="submitted_data_points")
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reviewed_data_points")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        db_table = "esg_data_points"
        unique_together = [("organization", "metric", "reporting_period", "facility")]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["metric", "reporting_period"]),
            models.Index(fields=["status", "submitted_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization} | {self.metric.code} | {self.reporting_period}"

    @property
    def value(self):
        if self.metric.data_type == "numeric":
            return self.numeric_value
        if self.metric.data_type == "boolean":
            return self.boolean_value
        return self.text_value


class ESGTarget(BaseModel):
    """Science-based or internal ESG targets."""

    class TargetType(models.TextChoices):
        ABSOLUTE = "absolute", "Absolute Reduction"
        INTENSITY = "intensity", "Intensity Reduction"
        PERCENTAGE = "percentage", "Percentage Improvement"

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="esg_targets"
    )
    metric = models.ForeignKey(MetricDefinition, on_delete=models.PROTECT, related_name="targets")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_type = models.CharField(max_length=20, choices=TargetType.choices)
    baseline_year = models.PositiveSmallIntegerField()
    baseline_value = models.DecimalField(max_digits=20, decimal_places=6)
    target_year = models.PositiveSmallIntegerField()
    target_value = models.DecimalField(max_digits=20, decimal_places=6)
    is_science_based = models.BooleanField(default=False)
    framework_alignment = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "esg_targets"
        ordering = ["target_year", "metric__category"]

    def __str__(self) -> str:
        return f"{self.organization} — {self.name} (by {self.target_year})"


class MaterialityAssessment(BaseModel):
    """Double materiality assessment linking topics to stakeholder impact."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="materiality_assessments"
    )
    reporting_period = models.ForeignKey(ReportingPeriod, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    category = models.CharField(max_length=1, choices=ESGCategory.choices)
    financial_materiality_score = models.DecimalField(
        max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    impact_materiality_score = models.DecimalField(
        max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    is_material = models.BooleanField(default=False)
    rationale = models.TextField(blank=True)
    stakeholder_groups = models.JSONField(default=list)

    class Meta:
        db_table = "esg_materiality_assessments"
        unique_together = [("organization", "reporting_period", "topic")]
