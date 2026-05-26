"""
Corporate Travel CSV Parser (Phase 8).

Handles travel expense / booking data.
Automatically assigns Scope 3 (Category 6: Business Travel).
Validates airport codes, estimates distances when missing.
"""
from .base import BaseCSVParser

# IATA airport code pattern
IATA_PATTERN = r"^[A-Z]{3}$"

# Rough distance estimates by cabin class multiplier (for emission factors)
CABIN_MULTIPLIERS = {
    "economy": 1.0,
    "economy class": 1.0,
    "coach": 1.0,
    "premium economy": 1.6,
    "business": 2.9,
    "business class": 2.9,
    "first": 4.0,
    "first class": 4.0,
}


class TravelParser(BaseCSVParser):
    SOURCE_TYPE = "travel"

    COLUMN_MAP = {
        "employee_name": "employee_name",
        "employee": "employee_name",
        "traveler": "employee_name",
        "travel_type": "travel_type",
        "type": "travel_type",
        "mode": "travel_type",
        "transport_type": "travel_type",
        "departure_airport": "departure_airport",
        "origin": "departure_airport",
        "from": "departure_airport",
        "departure": "departure_airport",
        "arrival_airport": "arrival_airport",
        "destination": "arrival_airport",
        "to": "arrival_airport",
        "arrival": "arrival_airport",
        "distance": "distance_km",
        "distance_km": "distance_km",
        "miles": "distance_miles",
        "distance_miles": "distance_miles",
        "cabin_class": "cabin_class",
        "class": "cabin_class",
        "fare_class": "cabin_class",
        "hotel_nights": "hotel_nights",
        "nights": "hotel_nights",
        "hotel_stay": "hotel_nights",
        "travel_date": "travel_date",
        "date": "travel_date",
        "departure_date": "travel_date",
        "cost": "cost",
        "amount": "cost",
        "expense": "cost",
        "currency": "currency",
        "department": "department_code",
        "cost_center": "department_code",
    }

    REQUIRED_FIELDS = ["travel_type"]

    def validate_row(self, row: dict) -> list[str]:
        import re
        errors = []
        travel_type = row.get("travel_type", "").lower()
        dep = row.get("departure_airport", "").upper().strip()
        arr = row.get("arrival_airport", "").upper().strip()
        distance = row.get("distance_km", "") or row.get("distance_miles", "")

        if travel_type in ("flight", "air", "airplane", "plane"):
            if dep and not re.match(IATA_PATTERN, dep):
                errors.append(f"Invalid departure airport code: {dep!r}")
            if arr and not re.match(IATA_PATTERN, arr):
                errors.append(f"Invalid arrival airport code: {arr!r}")
            if not dep and not arr and not distance:
                errors.append("Flight record missing both airport codes and distance")

        if distance:
            try:
                val = float(distance.replace(",", ""))
                if val < 0:
                    errors.append(f"Negative distance: {val}")
                if val > 20_000:
                    errors.append(f"Distance {val} km exceeds max possible flight distance")
            except ValueError:
                errors.append(f"Non-numeric distance: {distance!r}")

        hotel_nights = row.get("hotel_nights", "")
        if hotel_nights:
            try:
                n = int(hotel_nights)
                if n < 0:
                    errors.append(f"Negative hotel nights: {n}")
                if n > 365:
                    errors.append(f"Hotel nights {n} exceeds 1 year — verify")
            except ValueError:
                errors.append(f"Non-integer hotel nights: {hotel_nights!r}")

        return errors
