import apiClient from "./client";
import type {
  ESGDataPoint,
  ESGDataPointCreate,
  MetricDefinition,
  ReportingPeriod,
  ESGTarget,
  MaterialityAssessment,
  ESGSummary,
  PaginatedResponse,
  DataPointFilters,
} from "@/types/esg.types";

export const esgService = {
  // ── Metrics ──────────────────────────────────────────────────────────────
  getMetrics: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<MetricDefinition>>("/esg/metrics/", { params }).then((r) => r.data),

  // ── Reporting Periods ─────────────────────────────────────────────────────
  getPeriods: () =>
    apiClient
      .get<PaginatedResponse<ReportingPeriod>>("/esg/periods/", { params: { page_size: "100" } })
      .then((r) => r.data),

  createPeriod: (data: Omit<ReportingPeriod, "id" | "created_at" | "updated_at">) =>
    apiClient.post<ReportingPeriod>("/esg/periods/", data).then((r) => r.data),

  // ── Data Points ───────────────────────────────────────────────────────────
  getDataPoints: (filters?: DataPointFilters) =>
    apiClient
      .get<PaginatedResponse<ESGDataPoint>>("/esg/data-points/", { params: filters })
      .then((r) => r.data),

  getDataPoint: (id: string) =>
    apiClient.get<ESGDataPoint>(`/esg/data-points/${id}/`).then((r) => r.data),

  createDataPoint: (data: ESGDataPointCreate) =>
    apiClient.post<ESGDataPoint>("/esg/data-points/", data).then((r) => r.data),

  updateDataPoint: (id: string, data: Partial<ESGDataPointCreate>) =>
    apiClient.patch<ESGDataPoint>(`/esg/data-points/${id}/`, data).then((r) => r.data),

  deleteDataPoint: (id: string) =>
    apiClient.delete(`/esg/data-points/${id}/`),

  updateDataPointStatus: (id: string, status: string, reviewNotes?: string) =>
    apiClient
      .post<ESGDataPoint>(`/esg/data-points/${id}/status/`, { status, review_notes: reviewNotes })
      .then((r) => r.data),

  bulkImport: (file: File, reportingPeriodId: string, sourceType?: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("reporting_period_id", reportingPeriodId);
    if (sourceType) {
      form.append("source_type", sourceType);
    }
    return apiClient
      .post<{ created: number; updated: number; errors: Array<{ row: number; error: string }> }>(
        "/esg/data-points/bulk-import/",
        form,
        { headers: { "Content-Type": "multipart/form-data" } }
      )
      .then((r) => r.data);
  },

  getSummary: (periodId?: string) =>
    apiClient
      .get<ESGSummary>("/esg/data-points/summary/", { params: periodId ? { period_id: periodId } : {} })
      .then((r) => r.data),

  getDashboardStats: (periodId?: string) =>
    apiClient
      .get<any>("/esg/data-points/dashboard-stats/", { params: periodId ? { period_id: periodId } : {} })
      .then((r) => r.data),

  getUploadHistory: (params?: Record<string, string>) =>
    apiClient
      .get<any>("/esg/data-points/upload-history/", { params })
      .then((r) => r.data),

  getAnalytics: (periodId?: string) =>
    apiClient
      .get<any>("/esg/data-points/analytics/", { params: periodId ? { period_id: periodId } : {} })
      .then((r) => r.data),

  getEmissionsSummary: (periodId?: string) =>
    apiClient
      .get<any>("/esg/data-points/emissions-summary/", { params: periodId ? { period_id: periodId } : {} })
      .then((r) => r.data),

  // ── Targets ───────────────────────────────────────────────────────────────
  getTargets: () =>
    apiClient.get<PaginatedResponse<ESGTarget>>("/esg/targets/").then((r) => r.data),

  createTarget: (data: Omit<ESGTarget, "id" | "created_at" | "progress_percentage">) =>
    apiClient.post<ESGTarget>("/esg/targets/", data).then((r) => r.data),

  updateTarget: (id: string, data: Partial<ESGTarget>) =>
    apiClient.patch<ESGTarget>(`/esg/targets/${id}/`, data).then((r) => r.data),

  deleteTarget: (id: string) =>
    apiClient.delete(`/esg/targets/${id}/`),

  // ── Materiality ───────────────────────────────────────────────────────────
  getMaterialityAssessments: () =>
    apiClient.get<PaginatedResponse<MaterialityAssessment>>("/esg/materiality/").then((r) => r.data),

  createMaterialityAssessment: (data: Omit<MaterialityAssessment, "id" | "created_at" | "updated_at">) =>
    apiClient.post<MaterialityAssessment>("/esg/materiality/", data).then((r) => r.data),

  getEmissionCategories: () =>
    apiClient.get<PaginatedResponse<any>>("/esg/emission-categories/").then((r) => r.data),
};
