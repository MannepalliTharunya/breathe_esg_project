"""
Organization, Facility, and Membership models.
"""
from django.db import models
from apps.core.models import BaseModel, SoftDeleteModel
from apps.users.models import User


class Organization(BaseModel, SoftDeleteModel):
    """Top-level tenant entity."""

    class Industry(models.TextChoices):
        ENERGY = "energy", "Energy"
        MANUFACTURING = "manufacturing", "Manufacturing"
        FINANCE = "finance", "Finance"
        TECHNOLOGY = "technology", "Technology"
        HEALTHCARE = "healthcare", "Healthcare"
        RETAIL = "retail", "Retail"
        REAL_ESTATE = "real_estate", "Real Estate"
        TRANSPORTATION = "transportation", "Transportation"
        AGRICULTURE = "agriculture", "Agriculture"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200, db_index=True)
    legal_name = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=30, choices=Industry.choices, default=Industry.OTHER)
    country = models.CharField(max_length=2, help_text="ISO 3166-1 alpha-2")
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="org_logos/", null=True, blank=True)
    description = models.TextField(blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    annual_revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    fiscal_year_end = models.CharField(max_length=5, default="12-31", help_text="MM-DD")
    reporting_currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)
    subscription_tier = models.CharField(
        max_length=20,
        choices=[("starter", "Starter"), ("professional", "Professional"), ("enterprise", "Enterprise")],
        default="starter",
    )
    settings = models.JSONField(default=dict)

    class Meta:
        db_table = "organizations"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Facility(BaseModel):
    """A physical location or business unit within an organization."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="facilities")
    name = models.CharField(max_length=200)
    facility_type = models.CharField(
        max_length=30,
        choices=[
            ("headquarters", "Headquarters"),
            ("office", "Office"),
            ("manufacturing", "Manufacturing"),
            ("warehouse", "Warehouse"),
            ("data_center", "Data Center"),
            ("retail", "Retail"),
            ("other", "Other"),
        ],
        default="office",
    )
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    floor_area_sqm = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "facilities"
        ordering = ["organization", "name"]

    def __str__(self) -> str:
        return f"{self.organization.name} — {self.name}"


class OrganizationMembership(BaseModel):
    """Links users to organizations with a role."""

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        ESG_MANAGER = "esg_manager", "ESG Manager"
        ANALYST = "analyst", "Analyst"
        VIEWER = "viewer", "Viewer"
        AUDITOR = "auditor", "Auditor"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_invitations")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organization_memberships"
        unique_together = [("user", "organization")]
        indexes = [models.Index(fields=["user", "is_active"])]

    def __str__(self) -> str:
        return f"{self.user.email} @ {self.organization.name} ({self.role})"


class Department(BaseModel):
    """A business department or unit within an organization, optionally linked to a facility."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="departments")
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name="departments")
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "departments"
        ordering = ["organization", "name"]

    def __str__(self) -> str:
        return f"{self.organization.name} — {self.name}"
