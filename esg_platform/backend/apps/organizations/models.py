"""
Multi-tenant organization models.
Organization → Facility → Department hierarchy.
All data is scoped to an Organization.
"""
import uuid
from django.db import models
from apps.core.models import BaseModel


class Organization(models.Model):
    """Top-level tenant. Every piece of data belongs to one org."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    legal_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, help_text="ISO 3166-1 alpha-2")
    reporting_year = models.PositiveSmallIntegerField(default=2024)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organizations"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    """Links users to organizations with a role override."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="memberships")
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organization_members"
        unique_together = [("organization", "user")]


class Facility(BaseModel):
    """
    Physical location or business unit within an organization.
    Emissions data is always traceable to a facility.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="facilities")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, help_text="Internal facility code e.g. SAP plant code")
    facility_type = models.CharField(
        max_length=30,
        choices=[
            ("manufacturing", "Manufacturing"),
            ("office", "Office"),
            ("warehouse", "Warehouse"),
            ("data_center", "Data Center"),
            ("retail", "Retail"),
            ("other", "Other"),
        ],
        default="office",
    )
    country = models.CharField(max_length=2)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "facilities"
        unique_together = [("organization", "code")]
        indexes = [models.Index(fields=["organization", "is_active"])]

    def __str__(self):
        return f"{self.organization.name} — {self.name}"


class Department(BaseModel):
    """Cost center / department within an organization."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="departments")
    facility = models.ForeignKey(Facility, null=True, blank=True, on_delete=models.SET_NULL, related_name="departments")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, help_text="SAP cost center code")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "departments"
        unique_together = [("organization", "code")]

    def __str__(self):
        return f"{self.organization.name} / {self.name}"
