from django.db import models
from apps.core.models import BaseModel


class Framework(BaseModel):
    """ESG reporting framework definition (GRI, TCFD, SASB, CSRD, etc.)."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    description = models.TextField()
    issuing_body = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "frameworks"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} v{self.version}"


class FrameworkRequirement(BaseModel):
    """A specific disclosure requirement within a framework."""

    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, related_name="requirements")
    code = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=1, choices=[("E", "Environmental"), ("S", "Social"), ("G", "Governance")])
    is_mandatory = models.BooleanField(default=True)
    guidance = models.TextField(blank=True)
    linked_metrics = models.ManyToManyField("esg_data.MetricDefinition", blank=True, related_name="framework_requirements")

    class Meta:
        db_table = "framework_requirements"
        unique_together = [("framework", "code")]
        ordering = ["framework", "code"]

    def __str__(self) -> str:
        return f"{self.framework.code} — {self.code}: {self.title}"


class OrganizationFramework(BaseModel):
    """Tracks which frameworks an organization has adopted."""

    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="adopted_frameworks")
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    adopted_at = models.DateField()
    is_primary = models.BooleanField(default=False)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    last_assessed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "organization_frameworks"
        unique_together = [("organization", "framework")]
