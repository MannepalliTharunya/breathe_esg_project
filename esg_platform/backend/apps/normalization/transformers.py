"""
Source-specific transformers.
Each transformer takes a RawRecord and produces a NormalizedRecord dict.
"""
import logging
from decimal import Decimal, InvalidOperation
from .engine import UnitConverter, DateNormalizer, SuspiciousDataDetector, NormalizationError

logger = logging.getLogger(__name__)


def _safe_decimal(value: str) -> Decimal:
    """Parse a string to Decimal, handling commas and whitespace."""
    if not value:
        raise NormalizationError("Empty numeric value")
    cleaned = value.strip().replace(",", "").replace(" ", "")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise NormalizationError(f"Cannot parse number: {value!r}")


class SAPTransformer:
    """
    Transforms a SAP raw row into normalized fields.
    Handles fuel combustion (Scope 1) and procurement (Scope 3).
    """

    SCOPE1_FUEL_KEYWORDS = [
        "diesel", "petrol", "gasoline", "natural gas", "erdgas", "lpg",
        "fuel oil", "heizol", "coal", "kohle", "kerosene", "kerosin",
        "benzin", "kraftstoff",
    ]

    def transform(self, raw_data: dict, batch) -> dict:
        log = []
        errors = []

        # ── Quantity ──────────────────────────────────────────────────────────
        qty_str = raw_data.get("quantity", "") or raw_data.get("menge", "") or raw_data.get("Menge", "")
        unit_str = raw_data.get("unit", "") or raw_data.get("mengeneinheit", "") or raw_data.get("ME", "") or "L"

        try:
            qty = _safe_decimal(qty_str)
            log.append({"step": "parse_quantity", "from": qty_str, "to": str(qty)})
        except NormalizationError as e:
            errors.append(str(e))
            qty = Decimal("0")

        # ── Unit conversion ───────────────────────────────────────────────────
        try:
            norm_value, norm_unit, unit_log = UnitConverter.auto_convert(qty, unit_str)
            log.append({"step": "unit_conversion", "from": f"{qty} {unit_str}", "to": f"{norm_value} {norm_unit}", "note": unit_log})
        except NormalizationError as e:
            errors.append(str(e))
            norm_value, norm_unit = qty, unit_str

        # ── Date ──────────────────────────────────────────────────────────────
        date_str = raw_data.get("posting_date", "") or raw_data.get("buchungsdatum", "") or raw_data.get("BUDAT", "")
        try:
            activity_date, date_log = DateNormalizer.parse(date_str)
            log.append({"step": "date_normalization", "from": date_str, "to": str(activity_date), "note": date_log})
        except NormalizationError as e:
            errors.append(str(e))
            from django.utils import timezone
            activity_date = timezone.now().date()

        # ── Scope assignment ──────────────────────────────────────────────────
        fuel_type = (raw_data.get("fuel_type", "") or raw_data.get("material", "") or "").lower()
        mat_group = (raw_data.get("material_group", "") or raw_data.get("materialgruppe", "") or "").lower()
        combined = f"{fuel_type} {mat_group}"
        scope = "scope_1" if any(kw in combined for kw in self.SCOPE1_FUEL_KEYWORDS) else "scope_3"
        log.append({"step": "scope_assignment", "to": scope, "note": f"Based on fuel_type={fuel_type!r}"})

        # ── Suspicious check ──────────────────────────────────────────────────
        suspicious_reasons = SuspiciousDataDetector.check("sap", norm_value, norm_unit, activity_date)

        return {
            "scope": scope,
            "source_type": "sap",
            "activity_value": norm_value,
            "activity_unit": norm_unit,
            "activity_date": activity_date,
            "original_value": qty,
            "original_unit": unit_str,
            "vendor_name": raw_data.get("vendor_name", "") or raw_data.get("lieferant", "") or "",
            "cost_center": raw_data.get("cost_center", "") or raw_data.get("kostenstelle", "") or "",
            "document_reference": raw_data.get("document_number", "") or raw_data.get("belegnummer", "") or "",
            "transformation_log": log,
            "validation_errors": errors,
            "suspicious_reasons": suspicious_reasons,
            "is_suspicious": bool(suspicious_reasons),
        }


class UtilityTransformer:
    """Transforms utility electricity rows. Always Scope 2."""

    def transform(self, raw_data: dict, batch) -> dict:
        log = []
        errors = []

        kwh_str = raw_data.get("kwh_usage", "") or raw_data.get("kwh", "") or ""
        try:
            kwh = _safe_decimal(kwh_str)
            norm_value, norm_unit, unit_log = UnitConverter.convert_energy(kwh, "kWh")
            log.append({"step": "parse_kwh", "from": kwh_str, "to": str(norm_value), "note": unit_log})
        except NormalizationError as e:
            errors.append(str(e))
            norm_value, norm_unit = Decimal("0"), "kWh"

        start_str = raw_data.get("billing_start", "")
        end_str = raw_data.get("billing_end", "")
        try:
            start_date, _ = DateNormalizer.parse(start_str)
            log.append({"step": "billing_start", "from": start_str, "to": str(start_date)})
        except NormalizationError as e:
            errors.append(f"billing_start: {e}")
            from django.utils import timezone
            start_date = timezone.now().date()

        try:
            end_date, _ = DateNormalizer.parse(end_str)
            log.append({"step": "billing_end", "from": end_str, "to": str(end_date)})
        except NormalizationError as e:
            errors.append(f"billing_end: {e}")
            end_date = start_date

        suspicious_reasons = SuspiciousDataDetector.check("utility", norm_value, norm_unit, start_date)

        return {
            "scope": "scope_2",
            "source_type": "utility",
            "activity_value": norm_value,
            "activity_unit": norm_unit,
            "activity_date": start_date,
            "activity_period_start": start_date,
            "activity_period_end": end_date,
            "original_value": norm_value,
            "original_unit": "kWh",
            "vendor_name": raw_data.get("supplier", ""),
            "document_reference": raw_data.get("meter_id", ""),
            "transformation_log": log,
            "validation_errors": errors,
            "suspicious_reasons": suspicious_reasons,
            "is_suspicious": bool(suspicious_reasons),
        }


class TravelTransformer:
    """Transforms corporate travel rows. Always Scope 3."""

    def transform(self, raw_data: dict, batch) -> dict:
        log = []
        errors = []

        dist_str = raw_data.get("distance_km", "") or raw_data.get("distance_miles", "") or ""
        unit_str = "miles" if raw_data.get("distance_miles") and not raw_data.get("distance_km") else "km"

        if dist_str:
            try:
                dist = _safe_decimal(dist_str)
                norm_value, norm_unit, unit_log = UnitConverter.convert_distance(dist, unit_str)
                log.append({"step": "distance_conversion", "from": f"{dist} {unit_str}", "to": f"{norm_value} km", "note": unit_log})
            except NormalizationError as e:
                errors.append(str(e))
                norm_value, norm_unit = Decimal("0"), "km"
        else:
            norm_value, norm_unit = Decimal("0"), "km"
            log.append({"step": "distance_missing", "note": "No distance provided — set to 0"})

        hotel_nights_str = raw_data.get("hotel_nights", "") or "0"
        try:
            hotel_nights = int(hotel_nights_str) if hotel_nights_str.strip() else 0
        except ValueError:
            hotel_nights = 0
            errors.append(f"Invalid hotel_nights: {hotel_nights_str!r}")

        date_str = raw_data.get("travel_date", "")
        try:
            activity_date, date_log = DateNormalizer.parse(date_str)
            log.append({"step": "date_normalization", "from": date_str, "to": str(activity_date)})
        except NormalizationError as e:
            errors.append(str(e))
            from django.utils import timezone
            activity_date = timezone.now().date()

        suspicious_reasons = SuspiciousDataDetector.check("travel", norm_value, norm_unit, activity_date)

        return {
            "scope": "scope_3",
            "source_type": "travel",
            "activity_value": norm_value,
            "activity_unit": norm_unit,
            "activity_date": activity_date,
            "original_value": norm_value,
            "original_unit": unit_str,
            "vendor_name": raw_data.get("employee_name", ""),
            "cost_center": raw_data.get("department_code", ""),
            "transformation_log": log,
            "validation_errors": errors,
            "suspicious_reasons": suspicious_reasons,
            "is_suspicious": bool(suspicious_reasons),
        }


TRANSFORMER_REGISTRY = {
    "sap": SAPTransformer,
    "utility": UtilityTransformer,
    "travel": TravelTransformer,
}


def get_transformer(source_type: str):
    cls = TRANSFORMER_REGISTRY.get(source_type)
    if not cls:
        raise ValueError(f"No transformer for source type: {source_type!r}")
    return cls()
