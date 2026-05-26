from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User


class Report(BaseModel):
    class ReportType(models.TextChoices):
        GRI = "gri", "GRI Standards"
        TCFD = "tcfd", "TCFD"
        SASB = "sasb", "SASB"
        CDP = "cdp", "CDP"
        CSRD = "csrd", "CSRD"
        BRSR = "brsr", "BRSR"
        GHG_PROTOCOL = "ghg_protocol", "GHG Protocol"
        CUSTOM = "custom", "Custom"

    class ReportStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATING = "generating", "Generating"
        READY = "ready", "Ready"
        PUBLISHED = "published", "Published"
        FAILED = "failed", "Failed"

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="reports"
    )
    reporting_period = models.ForeignKey(
        "esg_data.ReportingPeriod", on_delete=models.CASCADE, related_name="reports"
    )
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.DRAFT)
    file_url = models.CharField(max_length=500, blank=True)
    file_size_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    generation_config = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "reports"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.organization} — {self.name} ({self.report_type})"
