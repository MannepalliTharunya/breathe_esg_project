import os
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.users.models import User
from apps.organizations.models import Organization, Facility, Department, OrganizationMembership
from apps.esg_data.models import EmissionCategory, MetricDefinition, ReportingPeriod, ESGDataPoint, ESGTarget, MaterialityAssessment
from apps.frameworks.models import Framework, FrameworkRequirement, OrganizationFramework

class Command(BaseCommand):
    help = "Seeds the database with complete master data and dynamic ESG data points."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        # 1. Create or get Organization
        org, org_created = Organization.objects.get_or_create(
            name="Breathe ESG Solutions",
            defaults={
                "legal_name": "Breathe ESG Solutions Inc.",
                "industry": "technology",
                "country": "IN",
                "website": "https://breatheesg.com",
                "description": "Premium ESG reporting and analytical compliance platform.",
                "employee_count": 250,
                "annual_revenue": 12500000.00,
                "reporting_currency": "USD",
                "is_active": True,
                "subscription_tier": "enterprise",
            }
        )
        if org_created:
            self.stdout.write(f"Created Organization: {org.name}")
        else:
            self.stdout.write(f"Using existing Organization: {org.name}")

        # 2. Add memberships for all existing users to Breathe ESG Solutions
        users = User.objects.all()
        for u in users:
            membership, m_created = OrganizationMembership.objects.get_or_create(
                user=u,
                organization=org,
                defaults={
                    "role": OrganizationMembership.Role.OWNER if u.email == 'admin@esg.local' else OrganizationMembership.Role.ADMIN,
                    "is_active": True,
                }
            )
            if m_created:
                self.stdout.write(f"Added membership for user: {u.email} as {membership.role}")

        # 3. Create Facilities
        facility_hq, _ = Facility.objects.get_or_create(
            organization=org,
            name="Acme Corporate Headquarters",
            defaults={
                "facility_type": "headquarters",
                "city": "Bengaluru",
                "state_province": "Karnataka",
                "postal_code": "560001",
                "country": "IN",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "floor_area_sqm": 4500.00,
                "employee_count": 180,
                "is_active": True,
            }
        )

        facility_plant, _ = Facility.objects.get_or_create(
            organization=org,
            name="Manufacturing Plant Alpha",
            defaults={
                "facility_type": "manufacturing",
                "city": "Chennai",
                "state_province": "Tamil Nadu",
                "postal_code": "600001",
                "country": "IN",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "floor_area_sqm": 12000.00,
                "employee_count": 70,
                "is_active": True,
            }
        )
        self.stdout.write("Created Facilities: Acme HQ, Manufacturing Plant Alpha")

        # 4. Create Departments
        depts = [
            ("Operations", "OPS", facility_hq),
            ("IT Services & Support", "IT", facility_hq),
            ("Human Resources", "HR", facility_hq),
            ("Assembly Line A", "ALA", facility_plant),
            ("Quality Assurance", "QA", facility_plant),
        ]
        for dept_name, code, facility in depts:
            dept, _ = Department.objects.get_or_create(
                organization=org,
                name=dept_name,
                defaults={
                    "code": code,
                    "facility": facility,
                    "is_active": True,
                }
            )
        self.stdout.write("Created Departments.")

        # 5. Create Frameworks
        frameworks_data = [
            ("gri", "GRI Standards", "GRI 2021", "Global reporting framework focused on stakeholder materiality.", "Global Reporting Initiative", "https://www.globalreporting.org"),
            ("tcfd", "TCFD Recommendations", "TCFD v2", "Climate-related financial risk disclosure recommendations.", "Task Force on Climate-related Financial Disclosures", "https://www.fsb-tcfd.org"),
            ("sasb", "SASB Standards", "SASB 2023", "Industry-specific financially material ESG disclosures.", "Value Reporting Foundation", "https://www.sasb.org"),
            ("csrd", "CSRD Standards", "ESRS v1", "European Union Corporate Sustainability Reporting Directive rules.", "EFRAG", "https://efrag.org"),
        ]
        for code, name, version, desc, body, web in frameworks_data:
            fw, _ = Framework.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "version": version,
                    "description": desc,
                    "issuing_body": body,
                    "website": web,
                    "is_active": True,
                }
            )
            # Create organization framework mapping
            OrganizationFramework.objects.get_or_create(
                organization=org,
                framework=fw,
                defaults={
                    "adopted_at": date(2023, 1, 1),
                    "is_primary": code == "gri",
                    "compliance_score": 85.00,
                }
            )
        self.stdout.write("Created ESG Frameworks.")

        # 6. Create Emission Categories
        categories_data = [
            ("Stationary Combustion", "STATIONARY_COMB", "scope1", "Emissions from boilers, generators, and furnaces."),
            ("Mobile Combustion", "MOBILE_COMB", "scope1", "Emissions from company-owned transportation vehicles."),
            ("Purchased Electricity", "ELEC_PURCH", "scope2", "Indirect greenhouse gas emissions from electricity grid consumption."),
            ("Business Travel", "TRAVEL_BUS", "scope3", "Indirect emissions from employee business travel flights and lodging."),
            ("Employee Commuting", "COMMUTE_EMP", "scope3", "Indirect emissions from employee commuting modes."),
        ]
        cat_map = {}
        for name, code, scope, desc in categories_data:
            cat, _ = EmissionCategory.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "scope": scope,
                    "description": desc,
                    "is_active": True,
                }
            )
            cat_map[code] = cat
        self.stdout.write("Created Emission Categories.")

        # 7. Create ESG Metric Definitions
        metrics_data = [
            ("GHG_SCOPE1", "GHG Emissions Scope 1", "E", "tCO2e", "numeric", cat_map["STATIONARY_COMB"]),
            ("GHG_SCOPE2", "GHG Emissions Scope 2", "E", "tCO2e", "numeric", cat_map["ELEC_PURCH"]),
            ("GHG_SCOPE3", "GHG Emissions Scope 3", "E", "tCO2e", "numeric", cat_map["TRAVEL_BUS"]),
            ("WATER_WITHDRAWAL", "Total Water Withdrawal", "E", "m3", "numeric", None),
            ("ENERGY_CONSUMPTION", "Total Energy Consumed", "E", "MWh", "numeric", None),
            ("EMPLOYEE_TURNOVER", "Annual Employee Turnover", "S", "%", "percentage", None),
            ("GENDER_PAY_GAP", "Gender Pay Gap Ratio", "S", "ratio", "numeric", None),
            ("BOARD_DIVERSITY", "Board Gender Diversity", "G", "%", "percentage", None),
            ("CODE_OF_CONDUCT", "Code of Conduct Adoption", "G", "#", "boolean", None),
        ]
        metric_map = {}
        for code, name, category, unit, data_type, emission_cat in metrics_data:
            m, _ = MetricDefinition.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "category": category,
                    "description": f"Standard ESG measurement metric for {name}.",
                    "unit": unit,
                    "data_type": data_type,
                    "is_required": True,
                    "emission_category": emission_cat,
                }
            )
            metric_map[code] = m
        self.stdout.write("Created ESG Metric Definitions.")

        # 8. Create Reporting Periods
        periods_data = [
            ("FY2023", date(2023, 1, 1), date(2023, 12, 31)),
            ("FY2024", date(2024, 1, 1), date(2024, 12, 31)),
            ("FY2025", date(2025, 1, 1), date(2025, 12, 31)),
        ]
        period_map = {}
        for name, start, end in periods_data:
            period, _ = ReportingPeriod.objects.get_or_create(
                organization=org,
                name=name,
                defaults={
                    "period_type": "annual",
                    "start_date": start,
                    "end_date": end,
                    "is_locked": False,
                }
            )
            period_map[name] = period
        self.stdout.write("Created Reporting Periods: FY2023, FY2024, FY2025")

        # 9. Create ESG Data Points
        seed_data = [
            # FY2023
            ("GHG_SCOPE1", "FY2023", 10900.0, "approved"),
            ("GHG_SCOPE2", "FY2023", 6800.0, "approved"),
            ("GHG_SCOPE3", "FY2023", 40000.0, "approved"),
            ("WATER_WITHDRAWAL", "FY2023", 450.0, "approved"),
            # FY2024
            ("GHG_SCOPE1", "FY2024", 9800.0, "approved"),
            ("GHG_SCOPE2", "FY2024", 5900.0, "approved"),
            ("GHG_SCOPE3", "FY2024", 37000.0, "approved"),
            ("WATER_WITHDRAWAL", "FY2024", 420.0, "approved"),
            # FY2025
            ("GHG_SCOPE1", "FY2025", 8700.0, "approved"),
            ("GHG_SCOPE2", "FY2025", 5100.0, "approved"),
            ("GHG_SCOPE3", "FY2025", 34000.0, "approved"),
            ("WATER_WITHDRAWAL", "FY2025", 390.0, "submitted"),
            ("EMPLOYEE_TURNOVER", "FY2025", 12.5, "approved"),
            ("BOARD_DIVERSITY", "FY2025", 40.0, "approved"),
            ("CODE_OF_CONDUCT", "FY2025", True, "approved"),
        ]

        admin_user = users.filter(role="org_admin").first() or users.first()

        for metric_code, period_name, val, status in seed_data:
            metric = metric_map[metric_code]
            period = period_map[period_name]
            
            defaults = {
                "numeric_value": val if isinstance(val, float) else None,
                "boolean_value": val if isinstance(val, bool) else None,
                "text_value": str(val) if not isinstance(val, (float, bool)) else "",
                "status": status,
                "data_source": "Seeded Database Utility",
                "collection_method": "automated",
                "confidence_level": random.choice([85, 90, 95, 100]),
                "submitted_by": admin_user,
                "submitted_at": timezone.now() if status != "draft" else None,
            }
            if metric_code == "WATER_WITHDRAWAL" and period_name == "FY2025":
                defaults["confidence_level"] = 72  # Below 80%!

            dp, created = ESGDataPoint.objects.get_or_create(
                organization=org,
                metric=metric,
                reporting_period=period,
                facility=facility_hq,
                defaults=defaults
            )
            if not created:
                dp.status = status
                dp.numeric_value = defaults["numeric_value"]
                dp.boolean_value = defaults["boolean_value"]
                dp.confidence_level = defaults["confidence_level"]
                dp.save()

        # Seed a failed data point
        failed_dp, _ = ESGDataPoint.objects.get_or_create(
            organization=org,
            metric=metric_map["ENERGY_CONSUMPTION"],
            reporting_period=period_map["FY2025"],
            facility=facility_plant,
            defaults={
                "numeric_value": 1500.0,
                "status": "rejected",
                "data_source": "Sensor failure",
                "collection_method": "estimated",
                "confidence_level": 50,
                "submitted_by": admin_user,
                "submitted_at": timezone.now(),
                "review_notes": "Calculation methodology rejected. Please recompute using approved grid emission factors.",
            }
        )

        # 10. Seed Targets
        ESGTarget.objects.get_or_create(
            organization=org,
            metric=metric_map["GHG_SCOPE1"],
            name="Net Zero Scope 1 Emissions by 2030",
            defaults={
                "description": "Science-based target to reduce Scope 1 absolute GHG emissions to net zero.",
                "target_type": "absolute",
                "baseline_year": 2023,
                "baseline_value": 10900.0,
                "target_year": 2030,
                "target_value": 0.0,
                "is_science_based": True,
                "framework_alignment": "SBTi",
                "created_by": admin_user,
            }
        )

        ESGTarget.objects.get_or_create(
            organization=org,
            metric=metric_map["GHG_SCOPE2"],
            name="100% Renewable Energy Sourcing by 2026",
            defaults={
                "description": "Internal intensity target to source 100% of our energy grid consumption from carbon-free resources.",
                "target_type": "percentage",
                "baseline_year": 2023,
                "baseline_value": 6800.0,
                "target_year": 2026,
                "target_value": 0.0,
                "is_science_based": False,
                "created_by": admin_user,
            }
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully! All master data populated."))
