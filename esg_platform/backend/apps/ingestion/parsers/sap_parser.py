"""
SAP Fuel & Procurement CSV Parser (Phase 6).

Handles real-world SAP export quirks:
- German column names (Werk, Materialgruppe, Menge, etc.)
- Mixed date formats (DD.MM.YYYY, YYYY-MM-DD, MM/DD/YYYY)
- Missing/null values
- Inconsistent units (L, GAL, KG, T, MT)
- Scope assignment: Scope 1 (direct fuel combustion), Scope 3 (procurement)
"""
import re
from .base import BaseCSVParser


class SAPParser(BaseCSVParser):
    SOURCE_TYPE = "sap"

    # Maps both English and German SAP column names to internal names
    COLUMN_MAP = {
        # English variants
        "plant_code": "plant_code",
        "plant": "plant_code",
        "material_group": "material_group",
        "materialgruppe": "material_group",
        "fuel_type": "fuel_type",
        "material": "fuel_type",
        "material_description": "fuel_type",
        "quantity": "quantity",
        "menge": "quantity",
        "unit": "unit",
        "mengeneinheit": "unit",
        "me": "unit",
        "cost_center": "cost_center",
        "kostenstelle": "cost_center",
        "posting_date": "posting_date",
        "buchungsdatum": "posting_date",
        "budat": "posting_date",
        "vendor_name": "vendor_name",
        "lieferant": "vendor_name",
        "vendor": "vendor_name",
        "amount": "amount_local",
        "betrag": "amount_local",
        "currency": "currency",
        "wahrung": "currency",
        "document_number": "document_number",
        "belegnummer": "document_number",
    }

    REQUIRED_FIELDS = ["plant_code", "quantity", "unit", "posting_date"]

    # Scope assignment rules based on material group / fuel type keywords
    SCOPE1_KEYWORDS = [
        "diesel", "petrol", "gasoline", "natural gas", "erdgas", "lpg",
        "fuel oil", "heizol", "coal", "kohle", "kerosene", "kerosin",
    ]
    SCOPE3_KEYWORDS = [
        "procurement", "beschaffung", "raw material", "rohstoff",
        "packaging", "verpackung", "chemical", "chemie",
    ]

    def assign_scope(self, fuel_type: str, material_group: str) -> str:
        combined = f"{fuel_type} {material_group}".lower()
        for kw in self.SCOPE1_KEYWORDS:
            if kw in combined:
                return "scope_1"
        for kw in self.SCOPE3_KEYWORDS:
            if kw in combined:
                return "scope_3"
        return "scope_3"  # default procurement to Scope 3

    def validate_row(self, row: dict) -> list[str]:
        errors = []
        qty = row.get("quantity", "")
        unit = row.get("unit", "")
        date = row.get("posting_date", "")

        if not qty:
            errors.append("Missing quantity")
        else:
            try:
                val = float(qty.replace(",", "."))
                if val < 0:
                    errors.append(f"Negative quantity: {val}")
                if val == 0:
                    errors.append("Zero quantity — likely a reversal entry")
            except ValueError:
                errors.append(f"Non-numeric quantity: {qty!r}")

        if not unit:
            errors.append("Missing unit of measure")

        if not date:
            errors.append("Missing posting date")

        return errors
