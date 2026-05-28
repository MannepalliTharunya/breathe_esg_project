# Design Decisions

Every significant ambiguity resolved during development, with reasoning.

---

## 1. SAP ingestion format: flat-file CSV, not IDoc or OData

**Options considered:** IDoc (EDI), OData service, BAPI RFC call, flat-file CSV export.

**Decision:** Flat-file CSV/Excel export.

**Why:** The assignment says "onboarding a new enterprise client." In practice, getting direct SAP system access (OData, BAPI) requires IT involvement, firewall rules, and SAP Basis configuration that takes weeks. Flat-file exports are what sustainability teams actually have on day one — they run a transaction (MB51, ME2M, or a custom report) and get a CSV. This is the realistic starting point for a new client.

**What I'd ask the PM:** "Does the client have an SAP Basis team willing to expose an OData service? If yes, we can build a connector. If not, flat-file is the right call for now."

**Tradeoff:** Flat-file is manual and error-prone. A real production system would eventually move to scheduled OData pulls. See TRADEOFFS.md.

---

## 2. German column names handled via normalization, not a fixed mapping

**Decision:** The parser strips parenthetical suffixes and lowercases all headers before matching. `"Quantity (Menge)"` → `"quantity"`, `"Posting Date (Buchungsdatum)"` → `"posting_date"`.

**Why:** SAP exports vary by client configuration. Some have English headers, some German, some both (e.g., `"Quantity (Menge)"`). A fixed mapping would break on any variation. The normalization approach handles all three cases with one code path.

---

## 3. Utility data: portal CSV export, not PDF or API

**Options considered:** PDF bill parsing, utility API (if available), portal CSV export.

**Decision:** Portal CSV export.

**Why:** PDF parsing is fragile and format-specific to each utility provider. Utility APIs exist (Green Button, some ESPI implementations) but are not universally available and require OAuth setup per provider. Portal CSV exports are the universal fallback — every utility portal has a "download usage data" button. This is what facilities teams actually use.

**What I'd ask the PM:** "Which utility providers does this client use? If they're all on a platform that supports Green Button, we can automate. Otherwise, CSV is the right call."

---

## 4. Travel data: CSV export from travel platform, not Concur/Navan API

**Decision:** CSV export.

**Why:** Concur's API requires OAuth 2.0 setup, client credentials, and often IT approval. Navan's API is similar. For a prototype, CSV export from either platform is the realistic starting point. The column mapping handles both Concur and Navan export formats since they use similar field names.

**What I'd ask the PM:** "Does the client use Concur or Navan? Are they willing to set up API credentials? If yes, we can build a connector in sprint 2."

---

## 5. RawRecord stores original data as JSON, never modified

**Decision:** `raw_data` is a JSONField containing the original CSV row dict. It is never updated after creation.

**Why:** Auditors need to see exactly what was uploaded. If we only stored normalized values, we'd lose the ability to explain why a record looks the way it does. The transformation_log on NormalizedRecord explains every step from raw → normalized.

---

## 6. Approved records are immediately locked (is_locked = True)

**Decision:** Approval sets `is_locked = True` and the API returns 409 on any subsequent decision attempt.

**Why:** The assignment says "approve rows before they're locked for audit." Once approved, the data should be immutable — this is what auditors expect. If an analyst approves a record and then realizes it's wrong, they need to create a corrected record (new upload), not modify the approved one.

**What I'd ask the PM:** "What's the correction workflow? Can an admin unlock a record, or does a correction require a new upload batch?"

---

## 7. Scope assignment is rule-based, not ML

**Decision:** Scope is assigned by keyword matching on fuel_type and material_group fields.

**Why:** Rule-based is transparent and auditable. An analyst can look at the transformation_log and see exactly why a record was assigned Scope 1 vs Scope 3. ML-based classification would be a black box and harder to defend to auditors.

**Limitation:** The keyword list is not exhaustive. Unknown fuel types default to Scope 3 (procurement). This is conservative — it's better to over-report Scope 3 than to miss Scope 1 emissions.

---

## 8. Multi-tenancy via organization FK, not separate schemas

**Decision:** All tenant data lives in shared tables with an `organization` FK. The middleware resolves the active org and all queries filter by it.

**Why:** Separate schemas (PostgreSQL) or separate databases add operational complexity. For a prototype with a small number of clients, shared tables with row-level isolation is simpler and sufficient. The `TenantModel` base class enforces the FK on every model.

**Risk:** A bug in the middleware could expose one tenant's data to another. Mitigated by: (1) the middleware is tested, (2) all querysets explicitly filter by `request.organization`.

---

## 9. Celery tasks run synchronously in local dev

**Decision:** `CELERY_TASK_ALWAYS_EAGER = True` in `settings_local.py`.

**Why:** Running Redis + Celery worker locally adds friction for development. Synchronous execution means the ingestion and normalization pipeline runs in the same request/response cycle during local testing, making it easier to debug.

**Production:** Celery runs as a separate worker container with Redis as the broker.

---

## 10. Emission factors are hardcoded, not database-driven

**Decision:** Emission factors live in `emission_factors.py` as Python constants.

**Why:** For a prototype, hardcoded factors are simpler and faster to implement. The factors are sourced from DEFRA 2023 and CEA 2023 — well-known, publicly available sources.

**What I'd ask the PM:** "Does the client need to use their own emission factors (e.g., supplier-specific factors, location-based vs market-based for electricity)? If yes, we need a factor management UI in sprint 2."

---

## 11. No real-time notifications

**Decision:** The dashboard polls every 30 seconds for batch status updates.

**Why:** WebSockets add complexity (Django Channels, separate ASGI server). Polling is simpler and sufficient for a prototype where uploads complete in seconds to minutes.

---

## 12. Register defaults all users to analyst role

**Decision:** The registration form does not expose a role selector. All self-registered users get `analyst` role. Admins can change roles via the Django admin.

**Why:** Allowing users to self-assign `admin` role would be a security hole. In a real system, user provisioning would be done by an admin or via SSO/SCIM.
