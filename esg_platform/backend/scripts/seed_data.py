"""
Seed script — creates demo org, links admin user, seeds emission categories.
Run: python manage.py shell < scripts/seed_data.py
"""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_local")
django.setup()

from apps.accounts.models import CustomUser
from apps.organizations.models import Organization, OrganizationMember
from apps.normalization.models import EmissionCategory

# ── Organization ──────────────────────────────────────────────────────────────
org, created = Organization.objects.get_or_create(
    name="Acme Corp",
    defaults={"industry": "manufacturing", "country": "DE", "reporting_year": 2024},
)
print(f"{'Created' if created else 'Found'} org: {org.name}")

# ── Link admin user ───────────────────────────────────────────────────────────
admin = CustomUser.objects.filter(email="admin@esg.local").first()
if admin:
    admin.organization = org
    admin.role = "admin"
    admin.save()
    OrganizationMember.objects.get_or_create(organization=org, user=admin)
    print(f"Linked {admin.email} to {org.name}")

# ── Emission categories ───────────────────────────────────────────────────────
CATEGORIES = [
    ("scope_1", "S1-STATIONARY", "Stationary Combustion", "Scope 1 — Stationary combustion of fuels in owned/controlled equipment", "GHG Protocol Scope 1", ["sap"]),
    ("scope_1", "S1-MOBILE",     "Mobile Combustion",     "Scope 1 — Combustion of fuels in owned/controlled vehicles", "GHG Protocol Scope 1", ["sap"]),
    ("scope_2", "S2-ELECTRICITY","Purchased Electricity", "Scope 2 — Indirect emissions from purchased electricity", "GHG Protocol Scope 2", ["utility"]),
    ("scope_3", "S3-CAT1",       "Purchased Goods & Services", "Scope 3 Category 1 — Upstream emissions from purchased goods", "GHG Protocol Scope 3 Cat 1", ["sap"]),
    ("scope_3", "S3-CAT6",       "Business Travel",       "Scope 3 Category 6 — Emissions from employee business travel", "GHG Protocol Scope 3 Cat 6", ["travel"]),
    ("scope_3", "S3-CAT7",       "Employee Commuting",    "Scope 3 Category 7 — Emissions from employee commuting", "GHG Protocol Scope 3 Cat 7", ["travel"]),
]

for scope, code, name, desc, ghg, sources in CATEGORIES:
    cat, created = EmissionCategory.objects.get_or_create(
        code=code,
        defaults={"scope": scope, "name": name, "description": desc,
                  "ghg_protocol_category": ghg, "source_types": sources},
    )
    print(f"{'Created' if created else 'Found'} category: {code}")

print("\nSeed complete.")
print(f"  Admin login: admin@esg.local / Admin123!")
print(f"  Organization: {org.name} (id={org.id})")
