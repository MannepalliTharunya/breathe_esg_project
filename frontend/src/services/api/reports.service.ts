import apiClient from "./client";
import type { Report, ReportCreate } from "@/types/reports.types";
import type { PaginatedResponse } from "@/types/esg.types";

export const reportsService = {
  getReports: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Report>>("/reports/", { params }).then((r) => r.data),

  getReport: (id: string) =>
    apiClient.get<Report>(`/reports/${id}/`).then((r) => r.data),

  createReport: (data: ReportCreate) =>
    apiClient.post<Report>("/reports/", data).then((r) => r.data),

  regenerateReport: (id: string) =>
    apiClient.post<{ detail: string }>(`/reports/${id}/regenerate/`).then((r) => r.data),

  deleteReport: (id: string) =>
    apiClient.delete(`/reports/${id}/`),
};
