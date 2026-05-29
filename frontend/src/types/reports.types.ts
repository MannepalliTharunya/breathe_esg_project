export type ReportType = "gri" | "tcfd" | "sasb" | "cdp" | "csrd" | "custom";
export type ReportStatus = "draft" | "generating" | "ready" | "published" | "failed";

export interface Report {
  id: string;
  name: string;
  report_type: ReportType;
  status: ReportStatus;
  file_url: string;
  file_size_bytes: number | null;
  generation_config: Record<string, unknown>;
  error_message: string;
  generated_at: string | null;
  published_at: string | null;
  created_by_name: string;
  created_at: string;
}

export interface ReportCreate {
  name: string;
  report_type: ReportType;
  reporting_period: string;
  generation_config?: Record<string, unknown>;
}
