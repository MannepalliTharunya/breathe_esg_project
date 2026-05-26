// ── Auth ──────────────────────────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: "admin" | "analyst" | "viewer";
  organization: string | null;
  organization_name: string | null;
}

// ── Pagination ────────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count: number;
  total_pages: number;
  current_page: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ── Organizations ─────────────────────────────────────────────────────────────
export interface Organization {
  id: string;
  name: string;
  industry: string;
  country: string;
  reporting_year: number;
}

export interface Facility {
  id: string;
  name: string;
  code: string;
  facility_type: string;
  country: string;
  city: string;
}

// ── Ingestion ─────────────────────────────────────────────────────────────────
export type SourceType = "sap" | "utility" | "travel";
export type BatchStatus = "pending" | "processing" | "completed" | "failed" | "partial";

export interface UploadBatch {
  id: string;
  source_type: SourceType;
  original_filename: string;
  file_size_bytes: number;
  status: BatchStatus;
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
  suspicious_rows: number;
  facility: string | null;
  facility_name: string | null;
  notes: string;
  error_summary: string;
  success_rate: number;
  processing_started_at: string | null;
  processing_completed_at: string | null;
  created_by: string;
  created_by_name: string;
  created_at: string;
}

export interface RawRecord {
  id: string;
  batch: string;
  row_number: number;
  raw_data: Record<string, string>;
  source_type: SourceType;
  status: "pending" | "normalized" | "failed" | "skipped";
  parse_errors: string[];
  created_at: string;
}

// ── Normalization ─────────────────────────────────────────────────────────────
export type RecordStatus = "pending" | "approved" | "rejected" | "locked" | "flagged";
export type Scope = "scope_1" | "scope_2" | "scope_3";

export interface NormalizedRecord {
  id: string;
  batch: string;
  batch_filename: string;
  row_number: number;
  raw_data: Record<string, string>;
  scope: Scope;
  source_type: SourceType;
  emission_category: string | null;
  emission_category_name: string | null;
  activity_value: string;
  activity_unit: string;
  activity_date: string;
  activity_period_start: string | null;
  activity_period_end: string | null;
  emission_factor: string | null;
  emission_factor_source: string;
  co2e_kg: string | null;
  vendor_name: string;
  cost_center: string;
  document_reference: string;
  original_value: string | null;
  original_unit: string;
  facility: string | null;
  facility_name: string | null;
  department: string | null;
  department_name: string | null;
  status: RecordStatus;
  is_suspicious: boolean;
  is_locked: boolean;
  suspicious_reasons: string[];
  validation_errors: string[];
  transformation_log: TransformStep[];
  created_at: string;
  updated_at: string;
}

export interface TransformStep {
  step: string;
  from?: string;
  to?: string;
  note?: string;
}

export interface ApprovalWorkflow {
  id: string;
  normalized_record: string;
  decision: "approved" | "rejected" | "flagged" | "escalated";
  comment: string;
  previous_status: string;
  new_status: string;
  decided_by: string;
  decided_by_email: string;
  created_at: string;
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export interface DashboardSummary {
  records: {
    total: number;
    pending: number;
    flagged: number;
    approved: number;
    rejected: number;
    locked: number;
    suspicious: number;
    failed: number;
  };
  batches: {
    total: number;
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
  emissions: {
    total_co2e_kg: number;
    by_scope: Array<{ scope: Scope; co2e_kg: number; count: number }>;
  };
}

export interface MonthlyTrend {
  month: string;
  scope: Scope;
  co2e_kg: number;
  count: number;
}

export interface IngestionQuality {
  source_type: SourceType;
  total_batches: number;
  total_rows: number;
  failed_rows: number;
  suspicious_rows: number;
  failed_pct: number;
  suspicious_pct: number;
}

// ── Audit ─────────────────────────────────────────────────────────────────────
export interface AuditLog {
  id: string;
  user_email: string;
  user_name: string;
  action: string;
  resource_type: string;
  resource_id: string;
  before_value: Record<string, unknown>;
  after_value: Record<string, unknown>;
  ip_address: string | null;
  source_system: string;
  created_at: string;
}
