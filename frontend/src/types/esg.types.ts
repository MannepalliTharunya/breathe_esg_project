export type ESGCategory = "E" | "S" | "G";

export type DataStatus =
  | "draft"
  | "submitted"
  | "under_review"
  | "approved"
  | "rejected"
  | "published";

export interface MetricDefinition {
  id: string;
  category: ESGCategory;
  code: string;
  name: string;
  description: string;
  unit: string;
  data_type: "numeric" | "text" | "boolean" | "percentage";
  is_required: boolean;
  calculation_guidance: string;
  framework_mappings: Record<string, string>;
  tags: string[];
}

export interface ReportingPeriod {
  id: string;
  organization: string;
  name: string;
  period_type: "annual" | "quarterly" | "monthly";
  start_date: string;
  end_date: string;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
}

export interface ESGDataPoint {
  id: string;
  metric: MetricDefinition;
  reporting_period: string;
  facility: string | null;
  value: number | string | boolean | null;
  numeric_value: number | null;
  text_value: string;
  boolean_value: boolean | null;
  status: DataStatus;
  data_source: string;
  collection_method: "manual" | "automated" | "estimated" | "calculated";
  confidence_level: number;
  notes: string;
  attachments: string[];
  submitted_by_name: string | null;
  submitted_at: string | null;
  reviewed_by_name: string | null;
  reviewed_at: string | null;
  review_notes: string;
  created_at: string;
  updated_at: string;
}

export interface ESGDataPointCreate {
  metric: string;
  reporting_period: string;
  facility?: string;
  numeric_value?: number;
  text_value?: string;
  boolean_value?: boolean;
  data_source?: string;
  collection_method?: string;
  confidence_level?: number;
  notes?: string;
}

export interface ESGTarget {
  id: string;
  metric: string;
  metric_name: string;
  metric_unit: string;
  name: string;
  description: string;
  target_type: "absolute" | "intensity" | "percentage";
  baseline_year: number;
  baseline_value: number;
  target_year: number;
  target_value: number;
  is_science_based: boolean;
  framework_alignment: string;
  progress_percentage: number | null;
  created_at: string;
}

export interface MaterialityAssessment {
  id: string;
  organization: string;
  reporting_period: string;
  topic: string;
  category: ESGCategory;
  financial_materiality_score: number;
  impact_materiality_score: number;
  is_material: boolean;
  rationale: string;
  stakeholder_groups: string[];
  created_at: string;
  updated_at: string;
}

export interface ESGSummary {
  E: CategorySummary;
  S: CategorySummary;
  G: CategorySummary;
}

export interface CategorySummary {
  total_metrics: number;
  approved: number;
  completion_pct: number;
}

export interface DataPointFilters {
  category?: ESGCategory;
  metric_code?: string;
  period?: string;
  facility?: string;
  status?: DataStatus | DataStatus[];
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  pagination: {
    count: number;
    total_pages: number;
    current_page: number;
    next: string | null;
    previous: string | null;
  };
  results: T[];
}
