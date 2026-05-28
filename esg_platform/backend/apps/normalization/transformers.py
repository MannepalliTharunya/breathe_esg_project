"""
Source-specific transformers.
Each transformer takes a RawRecord and produces a NormalizedRecord dict.
"""
import re
import logging
from decimal import Decimal, InvalidOperation
from .engine import UnitConverter, DateNormalizer, SuspiciousDataDetector, NormalizationError
from .emission_factors import get_fuel_factor, get_electricity_factor, get_travel_factor

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


def _normalize_keys(raw_data: dict) -> dict:
    """
    Normalize all keys in raw_data using the same logic as BaseCSVParser.normalize_header.
    This lets transformers use internal names regardless of original column format.
    e.g. 'Quantity (Menge)' → 'quantity', 'Unit (ME)' → 'unit'
    """
    result = {}
    for k, v in raw_data.items():
        # Strip parenthetical suffixes first
        cleaned = re.sub(r'\s*\(.*?\)\s*', '', k).strip()
        normalized = cleaned.lower().replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")
        result[normalized] = v
        # Also keep original key for fallback
        result[k] = v
    return result


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
        # Normalize keys so 'Quantity (Menge)' → 'quantity', etc.
        d = _normalize_keys(raw_data)

        # ── Quantity ──────────────────────────────────────────────────────────
        qty_str = d.get("quantity") or d.get("menge") or ""
        unit_str = d.get("unit") or d.get("mengeneinheit") or d.get("me") or "L"

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
        date_str = d.get("posting_date") or d.get("buchungsdatum") or d.get("budat") or ""
        try:
            activity_date, date_log = DateNormalizer.parse(date_str)
            log.append({"step": "date_normalization", "from": date_str, "to": str(activity_date), "note": date_log})
        except NormalizationError as e:
            errors.append(str(e))
            from django.utils import timezone
            activity_date = timezone.now().date()

        # ── Scope assignment ──────────────────────────────────────────────────
        fuel_type = (d.get("fuel_type") or d.get("material") or "").lower()
        mat_group = (d.get("material_group") or d.get("materialgruppe") or "").lower()
        combined = f"{fuel_type} {mat_group}"
        scope = "scope_1" if any(kw in combined for kw in self.SCOPE1_FUEL_KEYWORDS) else "scope_3"
        log.append({"step": "scope_assignment", "to": scope, "note": f"Based on fuel_type={fuel_type!r}"})

        # ── Emission factor + CO2e ────────────────────────────────────────────
        ef, ef_source = get_fuel_factor(fuel_type)
        co2e_kg = (norm_value * ef).quantize(Decimal("0.0001")) if norm_value else None
        log.append({"step": "co2e_calculation", "to": str(co2e_kg), "note": f"EF={ef} ({ef_source})"})

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
            "emission_factor": ef,
            "emission_factor_source": ef_source,
            "co2e_kg": co2e_kg,
            "vendor_name": d.get("vendor_name") or d.get("lieferant") or "",
            "cost_center": d.get("cost_center") or d.get("kostenstelle") or "",
            "document_reference": d.get("document_number") or d.get("belegnummer") or "",
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
        d = _normalize_keys(raw_data)

        kwh_str = d.get("kwh_usage") or d.get("kwh") or d.get("consumption_kwh") or d.get("usage") or ""
        try:
            kwh = _safe_decimal(kwh_str)
            norm_value, norm_unit, unit_log = UnitConverter.convert_energy(kwh, "kWh")
            log.append({"step": "parse_kwh", "from": kwh_str, "to": str(norm_value), "note": unit_log})
        except NormalizationError as e:
            errors.append(str(e))
            norm_value, norm_unit = Decimal("0"), "kWh"

        start_str = d.get("billing_start") or d.get("billing_start_date") or d.get("start_date") or d.get("period_start") or ""
        end_str = d.get("billing_end") or d.get("billing_end_date") or d.get("end_date") or d.get("period_end") or ""
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

        # ── Emission factor + CO2e ────────────────────────────────────────────
        ef, ef_source = get_electricity_factor()
        co2e_kg = (norm_value * ef).quantize(Decimal("0.0001")) if norm_value else None
        log.append({"step": "co2e_calculation", "to": str(co2e_kg), "note": f"EF={ef} ({ef_source})"})

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
            "emission_factor": ef,
            "emission_factor_source": ef_source,
            "co2e_kg": co2e_kg,
            "vendor_name": d.get("supplier") or d.get("utility_provider") or "",
            "document_reference": d.get("meter_id") or d.get("account_number") or "",
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
        d = _normalize_keys(raw_data)

        dist_str = d.get("distance_km") or d.get("distance") or ""
        miles_str = d.get("distance_miles") or d.get("miles") or ""
        unit_str = "miles" if miles_str and not dist_str else "km"
        dist_str = dist_str or miles_str

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

        hotel_nights_str = d.get("hotel_nights") or d.get("nights") or "0"
        try:
            hotel_nights = int(hotel_nights_str) if str(hotel_nights_str).strip() else 0
        except (ValueError, TypeError):
            hotel_nights = 0
            errors.append(f"Invalid hotel_nights: {hotel_nights_str!r}")

        date_str = d.get("travel_date") or d.get("date") or d.get("departure_date") or ""
        try:
            activity_date, date_log = DateNormalizer.parse(date_str)
            log.append({"step": "date_normalization", "from": date_str, "to": str(activity_date)})
        except NormalizationError as e:
            errors.append(str(e))
            from django.utils import timezone
            activity_date = timezone.now().date()

        # ── Emission factor + CO2e ────────────────────────────────────────────
        travel_type = d.get("travel_type") or d.get("type") or d.get("mode") or "flight"
        cabin_class = d.get("cabin_class") or d.get("class") or d.get("fare_class") or ""
        ef, ef_source = get_travel_factor(travel_type, cabin_class)
        co2e_kg = (norm_value * ef).quantize(Decimal("0.0001")) if norm_value else None
        log.append({"step": "co2e_calculation", "to": str(co2e_kg), "note": f"EF={ef} ({ef_source})"})

        suspicious_reasons = SuspiciousDataDetector.check("travel", norm_value, norm_unit, activity_date)

        return {
            "scope": "scope_3",
            "source_type": "travel",
            "activity_value": norm_value,
            "activity_unit": norm_unit,
            "activity_date": activity_date,
            "original_value": norm_value,
            "original_unit": unit_str,
            "emission_factor": ef,
            "emission_factor_source": ef_source,
            "co2e_kg": co2e_kg,
            "vendor_name": d.get("employee_name") or d.get("employee") or d.get("traveler") or "",
            "cost_center": d.get("department_code") or d.get("department") or d.get("cost_center") or "",
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
