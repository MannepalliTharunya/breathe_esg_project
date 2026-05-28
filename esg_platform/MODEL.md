# Data Model

## Design Principles

1. **Immutability of raw data** — `RawRecord` stores the original CSV row verbatim as JSON and is never modified. This is the source of truth for audit purposes.
2. **Separation of ingestion and normalization** — `RawRecord` (what came in) is separate from `NormalizedRecord` (what we computed). Analysts review normalized records; auditors can always trace back to the raw row.
3. **Multi-tenancy via organization FK** — Every tenant-scoped model inherits from `TenantModel` which enforces an `organization` foreign key. The middleware resolves the active org from the `X-Organization-Id` header or the user's own org field.
4. **Append-only audit trail** — `AuditLog` has no update or delete permissions. Every mutation is a new row.
5. **Immutable approved records** — `NormalizedRecord.is_locked = True` is set on approval. The API returns 409 if a locked record is submitted for review again.

---

## Entity Relationship

```
Organization
  ├── Facility (many)
  ├── Department (many, optional FK to Facility)
  ├── CustomUser (many, via organization FK)
  ├── UploadBatch (many)
  │     └── RawRecord (many)
  │           └── NormalizedRecord (1:1)
  │                 ├── ApprovalWorkflow (many, append-only)
  │                 ├── EmissionCategory (FK)
  │                 ├── Facility (FK, nullable)
  │                 └── Department (FK, nullable)
  └── AuditLog (many, append-only)
```

---

## Core Models

### `Organization`
Top-level tenant. Every piece of data belongs to exactly one organization.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| name | CharField | |
| industry | CharField | |
| country | CharField | ISO 3166-1 alpha-2 |
| reporting_year | SmallInt | Active reporting year |

### `CustomUser`
Extends `AbstractBaseUser`. Email is the unique identifier.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| email | EmailField | Unique |
| role | CharField | admin / analyst / viewer |
| organization | FK → Organization | Nullable (superusers have none) |

**Roles:**
- `admin` — full access, can manage users and org settings
- `analyst` — can upload, review, approve/reject records
- `viewer` — read-only access to dashboard and records

### `UploadBatch`
One batch = one file upload event. Tracks the full lifecycle.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| organization | FK | Tenant isolation |
| source_type | CharField | sap / utility / travel |
| original_filename | CharField | Preserved for audit |
| file | FileField | Stored in media/uploads/ |
| status | CharField | pending → processing → completed / failed / partial |
| total_rows | Int | Set after parsing |
| failed_rows | Int | Rows that failed validation |
| suspicious_rows | Int | Rows flagged by anomaly detection |
| error_summary | TextField | Human-readable failure reason |
| created_by | FK → User | Who uploaded |
| created_at | DateTime | |

### `RawRecord`
**Immutable.** Stores the original CSV row exactly as uploaded.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| organization | FK | Tenant isolation |
| batch | FK → UploadBatch | |
| row_number | Int | 1-based row in source file |
| raw_data | JSONField | Original key-value dict from CSV |
| source_type | CharField | Copied from batch |
| status | CharField | pending → normalized / failed / skipped |
| parse_errors | JSONField | List of error strings from parser |

### `NormalizedRecord`
The analyst-reviewable, transformed version of a raw row.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| organization | FK | Tenant isolation |
| raw_record | OneToOne → RawRecord | Full lineage |
| batch | FK → UploadBatch | |
| scope | CharField | scope_1 / scope_2 / scope_3 |
| source_type | CharField | sap / utility / travel |
| activity_value | Decimal(20,6) | Normalized quantity |
| activity_unit | CharField | L / kWh / km |
| activity_date | Date | Normalized to ISO 8601 |
| emission_factor | Decimal(20,8) | kg CO2e per unit |
| emission_factor_source | CharField | e.g. "DEFRA 2023 — diesel" |
| co2e_kg | Decimal(20,4) | Calculated: activity_value × emission_factor |
| vendor_name | CharField | Supplier / employee name |
| cost_center | CharField | SAP cost center / department |
| original_value | Decimal | Before unit conversion |
| original_unit | CharField | Before unit conversion |
| status | CharField | pending / flagged / approved / rejected / locked |
| is_suspicious | Boolean | Set by anomaly detector |
| is_locked | Boolean | True after approval — immutable |
| suspicious_reasons | JSONField | List of human-readable flag reasons |
| validation_errors | JSONField | List of normalization errors |
| transformation_log | JSONField | Ordered list of {step, from, to, note} |
| facility | FK → Facility | Nullable |
| department | FK → Department | Nullable |

**Why store transformation_log?** Auditors need to understand exactly what changed between the raw row and the normalized value. A list of steps (unit conversion, date parsing, scope assignment, CO2e calculation) makes this transparent.

### `ApprovalWorkflow`
Append-only decision log. Every approve/reject/flag creates a new row.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| organization | FK | Tenant isolation |
| normalized_record | FK → NormalizedRecord | |
| decision | CharField | approved / rejected / flagged / escalated |
| comment | TextField | Analyst's note |
| previous_status | CharField | Before this decision |
| new_status | CharField | After this decision |
| created_by | FK → User | Who decided |
| created_at | DateTime | |

### `EmissionCategory`
Master catalogue of GHG Protocol categories.

| Field | Type | Notes |
|-------|------|-------|
| scope | CharField | scope_1 / scope_2 / scope_3 |
| code | CharField | e.g. S1-STATIONARY, S3-CAT6 |
| name | CharField | e.g. "Business Travel" |
| ghg_protocol_category | CharField | e.g. "GHG Protocol Scope 3 Cat 6" |
| source_types | JSONField | Which source types map here |

### `AuditLog`
Append-only. No update or delete permissions in admin or API.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| organization | FK | Nullable (system actions) |
| user | FK → User | Who acted |
| user_email | EmailField | Denormalized for immutability |
| action | CharField | create / update / delete / record_approved / etc. |
| resource_type | CharField | e.g. "normalization" |
| resource_id | CharField | UUID of affected record |
| before_value | JSONField | State before change |
| after_value | JSONField | State after change |
| ip_address | GenericIPAddress | |
| created_at | DateTime | |

---

## Scope Assignment Logic

| Source | Fuel/Activity | Scope |
|--------|--------------|-------|
| SAP | Diesel, petrol, natural gas, coal, LPG | Scope 1 |
| SAP | Procurement, raw materials, packaging | Scope 3 |
| Utility | Electricity | Scope 2 |
| Travel | All modes | Scope 3 (Cat 6) |

---

## Emission Factors Used

| Activity | Factor | Source |
|----------|--------|--------|
| Diesel | 2.6391 kg CO2e/L | DEFRA 2023 |
| Petrol/Gasoline | 2.3122 kg CO2e/L | DEFRA 2023 |
| Natural Gas | 2.0400 kg CO2e/m³ | DEFRA 2023 |
| Coal | 2.4200 kg CO2e/kg | DEFRA 2023 |
| Electricity (India) | 0.7160 kg CO2e/kWh | CEA 2023 |
| Flight (economy) | 0.2550 kg CO2e/km | DEFRA 2023 |
| Flight (business) | 0.7395 kg CO2e/km | DEFRA 2023 × 2.9 |
| Train | 0.0410 kg CO2e/km | DEFRA 2023 |
| Car | 0.1710 kg CO2e/km | DEFRA 2023 |

---

## Indexes

Key indexes for query performance:
- `NormalizedRecord`: (organization, scope, status), (organization, source_type, activity_date), (batch, status), (is_suspicious, status)
- `UploadBatch`: (organization, source_type, status), (organization, created_at)
- `RawRecord`: (batch, status), (organization, source_type, status)
- `AuditLog`: (organization, action, created_at), (resource_type, resource_id), (user, created_at)
