# Tradeoffs — Three Things Deliberately Not Built

---

## 1. Automated SAP OData / API connector

**What it would be:** A scheduled Celery task that authenticates to the client's SAP system via OData (e.g., `/sap/opu/odata/sap/MM_PUR_PO_MAINT_V2_SRV/`) or a BAPI RFC call, pulls new procurement and fuel records on a schedule, and ingests them without manual file uploads.

**Why not built:**
- Requires SAP Basis configuration (OAuth 2.0 or basic auth, firewall rules, RFC destination setup) that is client-specific and takes weeks to arrange
- The realistic starting point for a new client is always a flat-file export — the API connector is a sprint 2 feature once the client's IT team is engaged
- Building a mock OData connector would be toy code that doesn't reflect real SAP integration complexity

**What would be needed to build it:**
- SAP system URL, client number, and credentials
- Decision on auth method (OAuth 2.0 preferred, basic auth as fallback)
- Agreement on which SAP transaction/report to pull from (MB51 for goods movements, ME2M for purchase orders, or a custom Z-report)
- Incremental sync strategy (delta token, last-modified timestamp, or document number range)

---

## 2. Emission factor management UI

**What it would be:** A database-driven emission factor table with a UI for admins to add, version, and override factors. Factors would be versioned (DEFRA 2022 vs DEFRA 2023) and could be client-specific (e.g., a client with a renewable energy contract might have a market-based electricity factor of 0 kg CO2e/kWh instead of the grid average).

**Why not built:**
- Adds significant complexity: factor versioning, effective date ranges, scope/activity type mapping, UI for non-technical users
- For a prototype, hardcoded DEFRA 2023 factors are sufficient to demonstrate the normalization pipeline
- The factors are clearly documented in MODEL.md and emission_factors.py so they can be audited and challenged

**What would be needed to build it:**
- `EmissionFactor` model with: scope, activity_type, unit, factor_value, source, effective_from, effective_to, organization (nullable for global defaults)
- Admin UI for factor management
- Factor selection logic in the transformer (pick the most recent factor effective on the activity_date)
- Recalculation job when factors are updated (re-normalize affected records)

---

## 3. PDF bill parsing for utility data

**What it would be:** A parser that extracts kWh usage, billing period, and meter ID from utility bill PDFs using OCR or structured PDF parsing (pdfplumber, camelot).

**Why not built:**
- PDF formats vary by utility provider — a parser for BESCOM bills would not work for TATA Power bills
- OCR-based extraction is unreliable and requires significant post-processing validation
- Portal CSV exports are available from every utility provider and are the correct tool for this job
- Building a PDF parser that works on one provider's format would give a false impression of generality

**What would be needed to build it:**
- A library of sample PDFs from each target utility provider
- Provider-specific extraction rules (coordinates, regex patterns, or ML-based extraction)
- Confidence scoring on extracted values
- Human review queue for low-confidence extractions
- This is a significant engineering effort (2-3 sprints) and should only be built if the client cannot access portal CSV exports

---

## Honorable Mentions (also not built)

- **SSO / SAML integration** — enterprise clients expect SSO. Not built because it requires client IdP configuration.
- **Role-based field visibility** — viewers should not see cost center codes or vendor names in some compliance frameworks. Not built due to time.
- **Bulk re-normalization** — when emission factors are updated, all historical records should be re-normalized. The infrastructure (Celery, NormalizationService) supports it but the trigger UI is not built.
- **Export to GHG Protocol template** — analysts need to export approved records to the standard GHG Protocol Excel template for submission. Not built.
