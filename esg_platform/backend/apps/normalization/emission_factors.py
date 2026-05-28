"""
Emission factors (kg CO2e per unit of activity).
Sources: DEFRA 2023, EPA 2023, IPCC AR6.

These are simplified defaults. In production, factors would be
loaded from a database table with versioning and source tracking.
"""
from decimal import Decimal

# ── Scope 1 — Fuel combustion (kg CO2e per liter or kg) ──────────────────────
FUEL_FACTORS_KG_CO2E = {
    # Per liter
    "diesel":       Decimal("2.6391"),   # DEFRA 2023
    "petrol":       Decimal("2.3122"),
    "gasoline":     Decimal("2.3122"),
    "lpg":          Decimal("1.5551"),   # per liter
    "fuel oil":     Decimal("2.9600"),
    "kerosene":     Decimal("2.5400"),
    "kerosin":      Decimal("2.5400"),
    # Per kg
    "coal":         Decimal("2.4200"),
    "natural gas":  Decimal("2.0400"),   # per m3
    "erdgas":       Decimal("2.0400"),
}

# ── Scope 2 — Electricity (kg CO2e per kWh) ──────────────────────────────────
# India grid average (CEA 2023)
ELECTRICITY_FACTOR = Decimal("0.7160")

# ── Scope 3 — Travel (kg CO2e per km) ────────────────────────────────────────
TRAVEL_FACTORS_KG_CO2E_PER_KM = {
    "flight":    Decimal("0.2550"),   # economy, DEFRA 2023
    "air":       Decimal("0.2550"),
    "airplane":  Decimal("0.2550"),
    "plane":     Decimal("0.2550"),
    "train":     Decimal("0.0410"),
    "car":       Decimal("0.1710"),
    "bus":       Decimal("0.0890"),
    "taxi":      Decimal("0.1490"),
    "default":   Decimal("0.2550"),
}

# Cabin class multipliers
CABIN_MULTIPLIERS = {
    "economy":         Decimal("1.0"),
    "economy class":   Decimal("1.0"),
    "coach":           Decimal("1.0"),
    "premium economy": Decimal("1.6"),
    "business":        Decimal("2.9"),
    "business class":  Decimal("2.9"),
    "first":           Decimal("4.0"),
    "first class":     Decimal("4.0"),
}


def get_fuel_factor(fuel_type: str) -> tuple[Decimal, str]:
    """Returns (factor, source_note)."""
    ft = fuel_type.lower().strip()
    for key, factor in FUEL_FACTORS_KG_CO2E.items():
        if key in ft:
            return factor, f"DEFRA 2023 — {key}"
    # Default to diesel if unknown
    return Decimal("2.6391"), "DEFRA 2023 — diesel (default)"


def get_electricity_factor() -> tuple[Decimal, str]:
    return ELECTRICITY_FACTOR, "CEA India Grid Emission Factor 2023"


def get_travel_factor(travel_type: str, cabin_class: str = "") -> tuple[Decimal, str]:
    tt = travel_type.lower().strip()
    base = TRAVEL_FACTORS_KG_CO2E_PER_KM.get(tt, TRAVEL_FACTORS_KG_CO2E["default"])
    multiplier = CABIN_MULTIPLIERS.get(cabin_class.lower().strip(), Decimal("1.0"))
    factor = base * multiplier
    return factor, f"DEFRA 2023 — {tt} {cabin_class}".strip()
