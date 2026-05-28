# Sources — Research Behind Each Data Source

---

## 1. SAP Fuel & Procurement Data

### What I researched

SAP exposes procurement and goods movement data through several mechanisms:
- **Transaction MB51** (Material Document List) — shows goods movements including fuel receipts. Exports to CSV/Excel via the standard SAP list export.
- **Transaction ME2M** (Purchase Orders by Material) — shows purchase orders with quantities, units, vendors, and cost centers.
- **OData service** `MM_PUR_PO_MAINT_V2_SRV` — REST API for purchase order data, requires SAP Gateway configuration.
- **IDoc MATMAS/ORDERS** — EDI format used for system-to-system integration, not human-readable.

### What I learned

Real SAP exports have several quirks:
1. **German column headers** — SAP's default language is German. A client running SAP in German will get `Menge` (quantity), `Mengeneinheit` (unit of measure), `Buchungsdatum` (posting date), `Kostenstelle` (cost center), `Lieferant` (vendor). Some clients configure bilingual exports: `"Quantity (Menge)"`.
2. **Inconsistent units** — SAP stores quantities in the base unit of measure configured per material. Diesel might be in liters (L), gallons (GAL), or barrels (BBL) depending on the plant's configuration. Coal might be in metric tons (MT) or short tons (ST).
3. **Plant codes** — `Plant Code` is a 4-character SAP code (e.g., `PL001`, `DE01`) that means nothing without a plant master lookup table. In a real deployment, we'd need a plant-to-facility mapping.
4. **Date formats** — German SAP installations use `DD.MM.YYYY`. US installations use `MM/DD/YYYY`. Some exports use ISO `YYYY-MM-DD`.
5. **Reversal entries** — SAP records reversals as negative quantities. These should be flagged as suspicious, not silently dropped.

### What my sample data looks like and why

The sample template (`sap_fuel_procurement_template.csv`) uses:
- Mixed fuel types: Diesel, Natural Gas, Petrol, LPG, Coal — realistic for a manufacturing client
- Compound column names: `"Quantity (Menge)"`, `"Unit (ME)"` — reflects bilingual SAP export
- ISO date format: `2024-01-15` — simplest to parse, but the parser handles 10+ formats
- Indian plant codes and vendors (Shell India, GAIL India, Indian Oil) — realistic for an Indian manufacturing client
- Units: Liters, m3, kg — realistic mix

### What would break in real deployment

1. **Plant code lookup** — without a plant master, we can't map `PL001` to a facility. Currently we use the batch's facility assignment.
2. **Material group taxonomy** — SAP material groups (e.g., `MG101`) are client-specific. Our scope assignment uses fuel type keywords, not material group codes.
3. **Currency conversion** — cost amounts are in local currency. We store them but don't convert.
4. **Reversal handling** — negative quantities are flagged as suspicious but not automatically matched to their original entry.
5. **Partial period exports** — if a client exports mid-month, we get incomplete data for that period.

---

## 2. Utility Electricity Data

### What I researched

Utility data is available through:
- **Portal CSV export** — every utility portal (BESCOM, TATA Power, MSEDCL in India; National Grid, EDF in UK) has a "download usage history" button that exports billing data as CSV.
- **Green Button** — US standard (ESPI protocol) for utility data sharing. Supported by most US utilities. Returns XML with interval meter data.
- **PDF bills** — the most common format but hardest to parse programmatically.
- **Smart meter APIs** — available from some utilities for interval data (15-minute readings).

### What I learned

1. **Billing periods don't align with calendar months** — a billing period might be 28-35 days depending on the meter reading schedule. This means you can't simply sum by month without pro-rating.
2. **Multiple meters per facility** — a large facility might have 10+ meters (HVAC, lighting, production lines). Each has its own meter ID and billing account.
3. **Tariff structures** — commercial/industrial tariffs have peak and off-peak rates. The CSV typically includes both total kWh and peak/off-peak breakdown.
4. **Units** — most portal exports are in kWh, but some industrial meters report in MWh or even GWh. Our parser handles all three.
5. **Supplier name** — important for market-based Scope 2 accounting (if the supplier provides renewable energy certificates).

### What my sample data looks like and why

The sample template (`utility_electricity_template.csv`) uses:
- Multiple meter IDs (`MTR-001`, `MTR-002`) — realistic for a multi-facility client
- Billing periods that don't align with calendar months (e.g., Jan 1–31, Feb 1–29) — realistic
- Peak/off-peak breakdown — reflects commercial tariff structure
- Indian utility providers (BESCOM, TATA Power, MSEDCL) — realistic for Indian client
- kWh values in the 18,000–62,000 range — realistic for a medium-sized commercial facility

### What would break in real deployment

1. **Pro-rating across months** — if a billing period spans two months, we currently use the start date as the activity date. A proper implementation would pro-rate the kWh across months.
2. **Market-based vs location-based** — we use the India grid average (0.716 kg CO2e/kWh). A client with renewable energy contracts needs a market-based factor (potentially 0).
3. **Reactive power / power factor** — some industrial bills include reactive power charges. We ignore these.
4. **Estimated vs actual readings** — utilities sometimes estimate readings when the meter can't be read. We don't distinguish estimated from actual.

---

## 3. Corporate Travel Data

### What I researched

Travel data is available through:
- **Concur Travel** — SAP's travel management platform. Exports expense reports as CSV. API available via OAuth 2.0.
- **Navan (formerly TripActions)** — modern travel platform. CSV export and REST API.
- **Expense management systems** — Expensify, Zoho Expense, etc. All have CSV exports.
- **Manual spreadsheets** — many companies still track travel in Excel maintained by the sustainability team.

### What I learned

1. **Distance is often not provided** — Concur and Navan record origin/destination airports (IATA codes) but not distance. Distance must be estimated from airport coordinates using the haversine formula.
2. **Cabin class matters significantly** — DEFRA 2023 multipliers: economy = 1.0×, business = 2.9×, first = 4.0×. A business class flight emits nearly 3× more than economy for the same route.
3. **Travel categories** — flights, hotels, ground transport (taxi, rental car, train) have different emission factors. Hotels are Scope 3 Category 1 (purchased services), flights are Category 6 (business travel).
4. **Employee privacy** — travel data contains employee names and travel patterns. In a real system, this would need GDPR/privacy controls.
5. **Connecting flights** — a trip from Hyderabad to London via Dubai is two flights, not one. Concur records each segment separately.

### What my sample data looks like and why

The sample template (`corporate_travel_template.csv`) uses:
- Mix of travel types: Flight, Train, Car — realistic for a corporate travel program
- IATA airport codes: DEL, BOM, LHR, SIN, DXB, JFK — realistic international routes
- Distance in km — some platforms provide this, some don't
- Cabin class mix: Economy and Business — realistic for a company with both junior and senior travelers
- Hotel nights — included for completeness (Scope 3 Cat 1)
- Indian employee names and departments — consistent with the demo organization

### What would break in real deployment

1. **Missing distances** — when distance is not provided and only airport codes are given, we set distance to 0 and flag as suspicious. A real implementation would use the haversine formula with an airport coordinates database.
2. **Connecting flights** — we treat each row as one trip segment. Multi-segment trips need to be aggregated by booking reference.
3. **Hotel emission factors** — we don't currently calculate CO2e for hotel nights (no factor in emission_factors.py). This is a gap.
4. **Ground transport** — taxi and rental car emissions depend on vehicle type and fuel. We use a generic car factor.
5. **Employee privacy** — employee names are stored in `vendor_name`. In production, this field should be pseudonymized or access-controlled.

---

## Emission Factor Sources

| Source | URL | Used for |
|--------|-----|---------|
| DEFRA 2023 Conversion Factors | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2023 | Fuel combustion, travel |
| CEA India Grid Emission Factor 2023 | https://cea.nic.in/wp-content/uploads/baseline/2023/CEF_2023.pdf | Electricity (India) |
| IPCC AR6 | https://www.ipcc.ch/report/ar6/wg1/ | GWP values for GHG Protocol |
| GHG Protocol Corporate Standard | https://ghgprotocol.org/corporate-standard | Scope 1/2/3 definitions |
