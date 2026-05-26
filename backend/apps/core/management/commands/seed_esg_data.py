"""
Seed ESG master data, organizations, and sample data points for development/demo.
Run: python manage.py seed_esg_data
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.users.models import User
from apps.organizations.models import Organization, Facility, Department, OrganizationMembership
from apps.esg_data.models import (
    ESGCategory,
    EmissionCategory,
    MetricDefinition,
    ReportingPeriod,
    ESGDataPoint,
    ESGTarget,
    ESGCategoryMaster,
    EmissionScope,
    CollectionMethod,
    DataSource,
    DataStatus,
)
from apps.frameworks.models import Framework, OrganizationFramework


class Command(BaseCommand):
    help = "Seeds master data, organizations, facilities, metrics, and 50+ sample ESG records."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding ESG platform master data...")

        self._seed_global_master()
        orgs = self._seed_organizations()
        users = list(User.objects.all())
        admin_user = users[0] if users else None

        metric_map = self._ensure_metrics()

        for org in orgs:
            self._seed_org_memberships(org, users, admin_user)
            facilities = self._seed_facilities(org)
            self._seed_departments(org, facilities)
            periods = self._seed_reporting_periods(org)
            self._seed_org_frameworks(org)
            self._seed_data_points(org, facilities, periods, metric_map, admin_user)

        # Ensure legacy orgs (e.g. Breathe ESG Solutions) also get periods & membership
        for org in Organization.objects.filter(is_active=True).exclude(id__in=[o.id for o in orgs]):
            self._seed_org_memberships(org, users, admin_user)
            self._seed_reporting_periods(org)
            self._seed_org_frameworks(org)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. Organizations: {len(orgs)}, metrics: {MetricDefinition.objects.count()}, "
            f"data points: {ESGDataPoint.objects.count()}"
        ))

    def _seed_global_master(self):
        for code, name in [("E", "Environmental"), ("S", "Social"), ("G", "Governance")]:
            ESGCategoryMaster.objects.update_or_create(
                code=code,
                defaults={"name": name, "description": f"{name} ESG pillar", "is_active": True},
            )

        for code, name in [
            ("scope1", "Scope 1"),
            ("scope2", "Scope 2"),
            ("scope3", "Scope 3"),
        ]:
            EmissionScope.objects.update_or_create(
                code=code,
                defaults={"name": name, "description": f"GHG Protocol {name}", "is_active": True},
            )

        for code, name in [
            ("estimated", "Estimated"),
            ("measured", "Measured"),
            ("erp_system", "ERP System"),
            ("iot_sensor", "IoT Sensor"),
            ("utility_bill", "Utility Bill"),
            ("manual_entry", "Manual Entry"),
            ("excel_upload", "Excel Upload"),
        ]:
            CollectionMethod.objects.update_or_create(
                code=code,
                defaults={"name": name, "is_active": True},
            )

        sources = [
            ("sap", "SAP", "erp"),
            ("utility_portal", "Utility Portal", "utility"),
            ("concur", "Concur", "travel"),
            ("navan", "Navan", "travel"),
            ("excel_upload", "Excel Upload", "manual"),
            ("erp_system", "ERP System", "erp"),
        ]
        for code, name, stype in sources:
            DataSource.objects.update_or_create(
                code=code,
                defaults={"name": name, "source_type": stype, "is_active": True},
            )

        frameworks = [
            ("gri", "GRI Standards", "GRI 2021", "Global Reporting Initiative"),
            ("sasb", "SASB", "SASB 2023", "Value Reporting Foundation"),
            ("tcfd", "TCFD", "TCFD v2", "Task Force on Climate-related Financial Disclosures"),
            ("cdp", "CDP", "CDP 2024", "CDP Worldwide"),
            ("brsr", "BRSR", "BRSR 2024", "SEBI India"),
            ("ghg_protocol", "GHG Protocol", "GHG v2", "WRI/WBCSD"),
        ]
        for code, name, version, body in frameworks:
            Framework.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "version": version,
                    "description": f"{name} reporting framework.",
                    "issuing_body": body,
                    "website": "",
                    "is_active": True,
                },
            )

        emission_cats = [
            ("Stationary Combustion", "STATIONARY_COMB", "scope1"),
            ("Purchased Electricity", "ELEC_PURCH", "scope2"),
            ("Business Travel", "TRAVEL_BUS", "scope3"),
            ("Waste Disposal", "WASTE_DISP", "scope3"),
        ]
        for name, code, scope in emission_cats:
            EmissionCategory.objects.update_or_create(
                code=code,
                defaults={"name": name, "scope": scope, "is_active": True},
            )

        self.stdout.write("  Global master data seeded.")

    def _seed_organizations(self):
        org_defs = [
            {
                "name": "RGVF Manufacturing",
                "legal_name": "RGVF Manufacturing Pvt Ltd",
                "industry": "manufacturing",
                "country": "IN",
            },
            {
                "name": "GreenTech Industries",
                "legal_name": "GreenTech Industries Ltd",
                "industry": "technology",
                "country": "IN",
            },
            {
                "name": "EcoSteel Pvt Ltd",
                "legal_name": "EcoSteel Private Limited",
                "industry": "materials",
                "country": "IN",
            },
        ]
        orgs = []
        for d in org_defs:
            org, _ = Organization.objects.update_or_create(
                name=d["name"],
                defaults={
                    "legal_name": d["legal_name"],
                    "industry": d["industry"],
                    "country": d["country"],
                    "website": "https://example.com",
                    "description": f"{d['name']} ESG reporting entity.",
                    "employee_count": random.randint(200, 2000),
                    "annual_revenue": Decimal("15000000.00"),
                    "reporting_currency": "INR",
                    "is_active": True,
                    "subscription_tier": "enterprise",
                },
            )
            orgs.append(org)
        return orgs

    def _seed_org_memberships(self, org, users, admin_user):
        for i, user in enumerate(users):
            role = OrganizationMembership.Role.OWNER if i == 0 else OrganizationMembership.Role.ADMIN
            OrganizationMembership.objects.get_or_create(
                user=user,
                organization=org,
                defaults={"role": role, "is_active": True},
            )

    def _seed_facilities(self, org):
        facility_defs = [
            ("Hyderabad Plant", "manufacturing", "Hyderabad", "Telangana"),
            ("Chennai Factory", "manufacturing", "Chennai", "Tamil Nadu"),
            ("Mumbai Warehouse", "warehouse", "Mumbai", "Maharashtra"),
            ("Solar Unit 3", "renewable", "Pune", "Maharashtra"),
        ]
        facilities = []
        for name, ftype, city, state in facility_defs:
            f, _ = Facility.objects.update_or_create(
                organization=org,
                name=name,
                defaults={
                    "facility_type": ftype,
                    "city": city,
                    "state_province": state,
                    "country": "IN",
                    "floor_area_sqm": Decimal(str(random.randint(5000, 25000))),
                    "employee_count": random.randint(50, 400),
                    "is_active": True,
                },
            )
            facilities.append(f)
        return facilities

    def _seed_departments(self, org, facilities):
        dept_names = [
            "Operations", "Manufacturing", "Logistics", "Procurement",
            "HR", "IT", "Finance", "Facilities",
        ]
        hq = facilities[0] if facilities else None
        for i, name in enumerate(dept_names):
            Department.objects.update_or_create(
                organization=org,
                name=name,
                defaults={
                    "code": name[:3].upper(),
                    "facility": facilities[i % len(facilities)] if facilities else hq,
                    "is_active": True,
                },
            )

    def _seed_reporting_periods(self, org):
        periods_def = [
            ("Q1 2024", "quarterly", date(2024, 1, 1), date(2024, 3, 31)),
            ("Q2 2024", "quarterly", date(2024, 4, 1), date(2024, 6, 30)),
            ("Q3 2024", "quarterly", date(2024, 7, 1), date(2024, 9, 30)),
            ("Q4 2024", "quarterly", date(2024, 10, 1), date(2024, 12, 31)),
            ("Annual 2024", "annual", date(2024, 1, 1), date(2024, 12, 31)),
            ("Annual 2025", "annual", date(2025, 1, 1), date(2025, 12, 31)),
        ]
        period_map = {}
        for name, ptype, start, end in periods_def:
            p, _ = ReportingPeriod.objects.update_or_create(
                organization=org,
                start_date=start,
                end_date=end,
                defaults={"name": name, "period_type": ptype, "is_locked": False},
            )
            period_map[name] = p
        return period_map

    def _seed_org_frameworks(self, org):
        for fw in Framework.objects.filter(is_active=True):
            OrganizationFramework.objects.get_or_create(
                organization=org,
                framework=fw,
                defaults={
                    "adopted_at": date(2024, 1, 1),
                    "is_primary": fw.code == "gri",
                    "compliance_score": Decimal("82.50"),
                },
            )

    def _ensure_metrics(self):
        ec_map = {c.code: c for c in EmissionCategory.objects.all()}
        metrics_def = [
            ("ELECTRICITY_CONSUMPTION", "Electricity Consumption", "E", "MWh", "numeric", ec_map.get("ELEC_PURCH")),
            ("DIESEL_CONSUMPTION", "Diesel Consumption", "E", "tonnes", "numeric", ec_map.get("STATIONARY_COMB")),
            ("NATURAL_GAS_USAGE", "Natural Gas Usage", "E", "tonnes", "numeric", ec_map.get("STATIONARY_COMB")),
            ("BUSINESS_TRAVEL_EMISSIONS", "Business Travel Emissions", "E", "tCO2e", "numeric", ec_map.get("TRAVEL_BUS")),
            ("WATER_USAGE", "Water Usage", "E", "m3", "numeric", None),
            ("WASTE_GENERATED", "Waste Generated", "E", "tonnes", "numeric", ec_map.get("WASTE_DISP")),
            ("CARBON_EMISSIONS", "Carbon Emissions", "E", "tCO2e", "numeric", ec_map.get("STATIONARY_COMB")),
            ("RENEWABLE_ENERGY_USAGE", "Renewable Energy Usage", "E", "MWh", "numeric", None),
            ("FUEL_CONSUMPTION", "Fuel Consumption", "E", "tonnes", "numeric", ec_map.get("STATIONARY_COMB")),
            ("GHG_SCOPE1", "GHG Emissions Scope 1", "E", "tCO2e", "numeric", ec_map.get("STATIONARY_COMB")),
            ("GHG_SCOPE2", "GHG Emissions Scope 2", "E", "tCO2e", "numeric", ec_map.get("ELEC_PURCH")),
            ("GHG_SCOPE3", "GHG Emissions Scope 3", "E", "tCO2e", "numeric", ec_map.get("TRAVEL_BUS")),
            ("EMPLOYEE_DIVERSITY_RATIO", "Employee Diversity Ratio", "S", "ratio", "numeric", None),
            ("SAFETY_INCIDENT_RATE", "Safety Incident Rate", "S", "#", "numeric", None),
            ("BOARD_DIVERSITY", "Board Gender Diversity", "G", "%", "percentage", None),
        ]
        metric_map = {}
        for code, name, cat, unit, dtype, ec in metrics_def:
            m, _ = MetricDefinition.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "category": cat,
                    "description": f"Standard metric: {name}",
                    "unit": unit,
                    "data_type": dtype,
                    "is_required": code.startswith("GHG"),
                    "emission_category": ec,
                },
            )
            metric_map[code] = m
        return metric_map

    def _seed_data_points(self, org, facilities, periods, metric_map, admin_user):
        if not periods or not facilities:
            return

        period_list = list(periods.values())
        statuses = [
            DataStatus.APPROVED,
            DataStatus.APPROVED,
            DataStatus.APPROVED,
            DataStatus.SUBMITTED,
            DataStatus.UNDER_REVIEW,
            DataStatus.REJECTED,
            DataStatus.DRAFT,
        ]
        collection_codes = ["measured", "erp_system", "utility_bill", "estimated", "iot_sensor"]
        source_codes = ["sap", "utility_portal", "concur", "erp_system", "excel_upload"]

        numeric_metrics = [
            "ELECTRICITY_CONSUMPTION", "DIESEL_CONSUMPTION", "NATURAL_GAS_USAGE",
            "BUSINESS_TRAVEL_EMISSIONS", "WATER_USAGE", "WASTE_GENERATED",
            "CARBON_EMISSIONS", "RENEWABLE_ENERGY_USAGE", "FUEL_CONSUMPTION",
            "GHG_SCOPE1", "GHG_SCOPE2", "GHG_SCOPE3",
            "EMPLOYEE_DIVERSITY_RATIO", "SAFETY_INCIDENT_RATE",
        ]

        value_ranges = {
            "ELECTRICITY_CONSUMPTION": (8000, 18000),
            "DIESEL_CONSUMPTION": (400, 1200),
            "NATURAL_GAS_USAGE": (200, 900),
            "BUSINESS_TRAVEL_EMISSIONS": (20, 120),
            "WATER_USAGE": (300, 800),
            "WASTE_GENERATED": (50, 200),
            "CARBON_EMISSIONS": (5000, 12000),
            "RENEWABLE_ENERGY_USAGE": (1000, 5000),
            "FUEL_CONSUMPTION": (300, 1100),
            "GHG_SCOPE1": (4000, 10000),
            "GHG_SCOPE2": (2500, 7000),
            "GHG_SCOPE3": (15000, 45000),
            "EMPLOYEE_DIVERSITY_RATIO": (0.35, 0.55),
            "SAFETY_INCIDENT_RATE": (0.5, 4.5),
        }

        created_count = 0
        target_count = 55 if org.name == "RGVF Manufacturing" else 15

        for i in range(target_count):
            metric_code = numeric_metrics[i % len(numeric_metrics)]
            metric = metric_map[metric_code]
            period = period_list[i % len(period_list)]
            facility = facilities[i % len(facilities)]
            lo, hi = value_ranges.get(metric_code, (10, 1000))
            value = round(random.uniform(lo, hi), 2)
            status = statuses[i % len(statuses)]
            confidence = random.choice([72, 85, 90, 95, 100])

            defaults = {
                "numeric_value": Decimal(str(value)),
                "status": status,
                "data_source": random.choice(source_codes),
                "collection_method": random.choice(collection_codes),
                "confidence_level": confidence,
                "notes": f"Seeded record {i + 1} for {org.name}",
                "submitted_by": admin_user,
                "submitted_at": timezone.now() - timedelta(days=random.randint(1, 90)),
            }
            if status in (DataStatus.APPROVED, DataStatus.REJECTED):
                defaults["reviewed_by"] = admin_user
                defaults["reviewed_at"] = timezone.now()

            _, created = ESGDataPoint.objects.update_or_create(
                organization=org,
                metric=metric,
                reporting_period=period,
                facility=facility,
                defaults=defaults,
            )
            if created:
                created_count += 1

        if org.name == "RGVF Manufacturing" and admin_user:
            ESGTarget.objects.get_or_create(
                organization=org,
                metric=metric_map["GHG_SCOPE1"],
                name="Net Zero Scope 1 by 2030",
                defaults={
                    "description": "Science-based Scope 1 reduction target.",
                    "target_type": "absolute",
                    "baseline_year": 2024,
                    "baseline_value": Decimal("9500"),
                    "target_year": 2030,
                    "target_value": Decimal("0"),
                    "is_science_based": True,
                    "framework_alignment": "SBTi",
                    "created_by": admin_user,
                },
            )

        self.stdout.write(f"  {org.name}: {created_count} new data points.")
