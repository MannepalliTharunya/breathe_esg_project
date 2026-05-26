"""
ESG Normalization Engine (Phase 9).

Responsibilities:
1. Unit conversion → canonical SI units (liters, kWh, km)
2. Date normalization → ISO 8601
3. Scope assignment
4. Suspicious data detection
5. Transformation logging (full lineage)
6. Duplicate detection

All transformations are logged in transformation_log so analysts
can see exactly what changed and why.
"""
import re
import logging
from decimal import Decimal, InvalidOperation
from datetime import date
from typing import Optional
from dateutil import parser as dateutil_parser

logger = logging.getLogger(__name__)

# ── Unit conversion tables ────────────────────────────────────────────────────
# All values convert TO the canonical unit

VOLUME_TO_LITERS = {
    "l": Decimal("1"),
    "liter": Decimal("1"),
    "liters": Decimal("1"),
    "litre": Decimal("1"),
    "litres": Decimal("1"),
    "gal": Decimal("3.78541"),
    "gallon": Decimal("3.78541"),
    "gallons": Decimal("3.78541"),
    "us_gal": Decimal("3.78541"),
    "uk_gal": Decimal("4.54609"),
    "imp_gal": Decimal("4.54609"),
    "m3": Decimal("1000"),
    "cbm": Decimal("1000"),
    "ft3": Decimal("28.3168"),
    "bbl": Decimal("158.987"),   # oil barrel
}

MASS_TO_KG = {
    "kg": Decimal("1"),
    "kilogram": Decimal("1"),
    "kilograms": Decimal("1"),
    "g": Decimal("0.001"),
    "gram": Decimal("0.001"),
    "t": Decimal("1000"),
    "ton": Decimal("1000"),
    "tonne": Decimal("1000"),
    "tonnes": Decimal("1000"),
    "mt": Decimal("1000"),
    "metric_ton": Decimal("1000"),
    "metric_tons": Decimal("1000"),
    "lb": Decimal("0.453592"),
    "lbs": Decimal("0.453592"),
    "pound": Decimal("0.453592"),
    "pounds": Decimal("0.453592"),
    "short_ton": Decimal("907.185"),
    "st": Decimal("907.185"),
}

ENERGY_TO_KWH = {
    "kwh": Decimal("1"),
    "kw_h": Decimal("1"),
    "mwh": Decimal("1000"),
    "gwh": Decimal("1000000"),
    "mj": Decimal("0.277778"),
    "gj": Decimal("277.778"),
    "tj": Decimal("277778"),
    "btu": Decimal("0.000293071"),
    "mmbtu": Decimal("293.071"),
    "therm": Decimal("29.3071"),
}

DISTANCE_TO_KM = {
    "km": Decimal("1"),
    "kilometer": Decimal("1"),
    "kilometers": Decimal("1"),
    "kilometre": Decimal("1"),
    "kilometres": Decimal("1"),
    "mi": Decimal("1.60934"),
    "mile": Decimal("1.60934"),
    "miles": Decimal("1.60934"),
    "nm": Decimal("1.852"),
    "nautical_mile": Decimal("1.852"),
}

# Suspicious thresholds per source type
SUSPICIOUS_THRESHOLDS = {
    "sap": {
        "max_liters_per_row": Decimal("500000"),   # 500k liters in one entry
        "max_kg_per_row": Decimal("1000000"),
    },
    "utility": {
        "max_kwh_per_row": Decimal("10000000"),    # 10 GWh in one billing period
        "min_kwh_per_row": Decimal("0.001"),
    },
    "travel": {
        "max_km_per_flight": Decimal("20000"),
        "max_hotel_nights": Decimal("365"),
    },
}


class NormalizationError(Exception):
    pass


class UnitConverter:
    """Converts a value from source unit to canonical unit."""

    @staticmethod
    def normalize_unit_str(unit: str) -> str:
        return unit.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")

    @classmethod
    def convert_volume(cls, value: Decimal, unit: str) -> tuple[Decimal, str, str]:
        """Returns (converted_value, canonical_unit, log_note)"""
        u = cls.normalize_unit_str(unit)
        factor = VOLUME_TO_LITERS.get(u)
        if factor is None:
            raise NormalizationError(f"Unknown volume unit: {unit!r}")
        converted = value * factor
        return converted, "L", f"Converted {value} {unit} → {converted:.4f} L (factor {factor})"

    @classmethod
    def convert_mass(cls, value: Decimal, unit: str) -> tuple[Decimal, str, str]:
        u = cls.normalize_unit_str(unit)
        factor = MASS_TO_KG.get(u)
        if factor is None:
            raise NormalizationError(f"Unknown mass unit: {unit!r}")
        converted = value * factor
        return converted, "kg", f"Converted {value} {unit} → {converted:.4f} kg (factor {factor})"

    @classmethod
    def convert_energy(cls, value: Decimal, unit: str) -> tuple[Decimal, str, str]:
        u = cls.normalize_unit_str(unit)
        factor = ENERGY_TO_KWH.get(u)
        if factor is None:
            raise NormalizationError(f"Unknown energy unit: {unit!r}")
        converted = value * factor
        return converted, "kWh", f"Converted {value} {unit} → {converted:.4f} kWh (factor {factor})"

    @classmethod
    def convert_distance(cls, value: Decimal, unit: str) -> tuple[Decimal, str, str]:
        u = cls.normalize_unit_str(unit)
        factor = DISTANCE_TO_KM.get(u)
        if factor is None:
            raise NormalizationError(f"Unknown distance unit: {unit!r}")
        converted = value * factor
        return converted, "km", f"Converted {value} {unit} → {converted:.4f} km (factor {factor})"

    @classmethod
    def auto_convert(cls, value: Decimal, unit: str) -> tuple[Decimal, str, str]:
        """Try all unit families, return first match."""
        u = UnitConverter.normalize_unit_str(unit)
        if u in VOLUME_TO_LITERS:
            return cls.convert_volume(value, unit)
        if u in MASS_TO_KG:
            return cls.convert_mass(value, unit)
        if u in ENERGY_TO_KWH:
            return cls.convert_energy(value, unit)
        if u in DISTANCE_TO_KM:
            return cls.convert_distance(value, unit)
        raise NormalizationError(f"Unrecognized unit: {unit!r}")


class DateNormalizer:
    """Parses messy date strings into Python date objects."""

    DATE_FORMATS = [
        "%d.%m.%Y",   # German: 31.12.2023
        "%d.%m.%y",   # German short: 31.12.23
        "%Y-%m-%d",   # ISO: 2023-12-31
        "%m/%d/%Y",   # US: 12/31/2023
        "%m/%d/%y",   # US short: 12/31/23
        "%d/%m/%Y",   # EU: 31/12/2023
        "%d-%m-%Y",   # 31-12-2023
        "%Y%m%d",     # Compact: 20231231
        "%b %d, %Y",  # Jan 31, 2023
        "%d %b %Y",   # 31 Jan 2023
    ]

    @classmethod
    def parse(cls, value: str) -> tuple[date, str]:
        """Returns (date, log_note). Raises NormalizationError if unparseable."""
        if not value or not value.strip():
            raise NormalizationError("Empty date value")

        v = value.strip()

        # Try explicit formats first (faster, more reliable)
        import datetime
        for fmt in cls.DATE_FORMATS:
            try:
                d = datetime.datetime.strptime(v, fmt).date()
                return d, f"Parsed date {v!r} with format {fmt}"
            except ValueError:
                continue

        # Fallback to dateutil (handles many edge cases)
        try:
            d = dateutil_parser.parse(v, dayfirst=True).date()
            return d, f"Parsed date {v!r} via dateutil"
        except Exception:
            raise NormalizationError(f"Cannot parse date: {v!r}")


class SuspiciousDataDetector:
    """
    Flags records that look anomalous.
    Returns list of human-readable reason strings.
    Flagged records still get normalized — analysts decide what to do.
    """

    @staticmethod
    def check(
        source_type: str,
        activity_value: Decimal,
        activity_unit: str,
        activity_date: Optional[date] = None,
    ) -> list[str]:
        reasons = []
        thresholds = SUSPICIOUS_THRESHOLDS.get(source_type, {})

        if activity_value < 0:
            reasons.append(f"Negative activity value: {activity_value}")

        if activity_value == 0:
            reasons.append("Zero activity value — possible reversal or data error")

        if source_type == "sap":
            if activity_unit == "L" and activity_value > thresholds.get("max_liters_per_row", Decimal("999999999")):
                reasons.append(f"Extremely high volume: {activity_value:,.0f} L")
            if activity_unit == "kg" and activity_value > thresholds.get("max_kg_per_row", Decimal("999999999")):
                reasons.append(f"Extremely high mass: {activity_value:,.0f} kg")

        if source_type == "utility":
            if activity_unit == "kWh":
                if activity_value > thresholds.get("max_kwh_per_row", Decimal("999999999")):
                    reasons.append(f"Extremely high electricity: {activity_value:,.0f} kWh")
                if activity_value < thresholds.get("min_kwh_per_row", Decimal("0")):
                    reasons.append(f"Near-zero electricity: {activity_value} kWh")

        if source_type == "travel":
            if activity_unit == "km" and activity_value > thresholds.get("max_km_per_flight", Decimal("20000")):
                reasons.append(f"Flight distance {activity_value:,.0f} km exceeds max possible")

        if activity_date:
            from django.utils import timezone
            today = timezone.now().date()
            if activity_date > today:
                reasons.append(f"Future date: {activity_date}")
            from datetime import timedelta
            if activity_date < (today - timedelta(days=365 * 5)):
                reasons.append(f"Date older than 5 years: {activity_date}")

        return reasons


class DuplicateDetector:
    """
    Checks if a normalized record already exists for the same
    organization + source + date + value + unit combination.
    """

    @staticmethod
    def is_duplicate(organization_id, source_type: str, activity_date: date,
                     activity_value: Decimal, activity_unit: str,
                     exclude_batch_id=None) -> bool:
        from apps.normalization.models import NormalizedRecord
        qs = NormalizedRecord.objects.filter(
            organization_id=organization_id,
            source_type=source_type,
            activity_date=activity_date,
            activity_value=activity_value,
            activity_unit=activity_unit,
        )
        if exclude_batch_id:
            qs = qs.exclude(batch_id=exclude_batch_id)
        return qs.exists()
