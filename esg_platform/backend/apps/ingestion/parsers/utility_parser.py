"""
Utility Electricity CSV Parser (Phase 7).

Handles electricity billing data from utility providers.
Automatically assigns Scope 2 (market-based or location-based).
Detects billing anomalies: zero usage, extreme spikes, overlapping periods.
"""
from .base import BaseCSVParser


class UtilityParser(BaseCSVParser):
    SOURCE_TYPE = "utility"

    COLUMN_MAP = {
        "meter_id": "meter_id",
        "meter": "meter_id",
        "account_number": "meter_id",
        "billing_start_date": "billing_start",
        "start_date": "billing_start",
        "period_start": "billing_start",
        "billing_end_date": "billing_end",
        "end_date": "billing_end",
        "period_end": "billing_end",
        "kwh_usage": "kwh_usage",
        "kwh": "kwh_usage",
        "consumption_kwh": "kwh_usage",
        "energy_kwh": "kwh_usage",
        "usage": "kwh_usage",
        "tariff_type": "tariff_type",
        "tariff": "tariff_type",
        "rate_type": "tariff_type",
        "peak_usage": "peak_kwh",
        "peak_kwh": "peak_kwh",
        "off_peak_usage": "off_peak_kwh",
        "off_peak_kwh": "off_peak_kwh",
        "facility": "facility_name",
        "facility_name": "facility_name",
        "site": "facility_name",
        "amount": "amount",
        "total_amount": "amount",
        "bill_amount": "amount",
        "currency": "currency",
        "supplier": "supplier",
        "utility_provider": "supplier",
    }

    REQUIRED_FIELDS = ["meter_id", "billing_start", "billing_end", "kwh_usage"]

    def validate_row(self, row: dict) -> list[str]:
        errors = []
        kwh = row.get("kwh_usage", "")
        start = row.get("billing_start", "")
        end = row.get("billing_end", "")

        if not kwh:
            errors.append("Missing kWh usage")
        else:
            try:
                val = float(kwh.replace(",", ""))
                if val < 0:
                    errors.append(f"Negative kWh: {val}")
                if val == 0:
                    errors.append("Zero kWh — verify meter reading")
                if val > 10_000_000:
                    errors.append(f"Extremely high kWh ({val:,.0f}) — verify data")
            except ValueError:
                errors.append(f"Non-numeric kWh: {kwh!r}")

        if not start:
            errors.append("Missing billing start date")
        if not end:
            errors.append("Missing billing end date")

        return errors
