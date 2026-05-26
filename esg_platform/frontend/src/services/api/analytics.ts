import { apiClient } from "./client";

export const analyticsApi = {
  dashboard: () =>
    apiClient.get("/analytics/dashboard/").then(r => r.data),

  emissionsBySource: () =>
    apiClient.get("/analytics/emissions/by-source/").then(r => r.data),

  monthlyTrend: (scope?: string) =>
    apiClient.get("/analytics/emissions/monthly/", { params: scope ? { scope } : {} }).then(r => r.data),

  facilityEmissions: () =>
    apiClient.get("/analytics/emissions/by-facility/").then(r => r.data),

  ingestionQuality: () =>
    apiClient.get("/analytics/ingestion-quality/").then(r => r.data),

  suspicious: () =>
    apiClient.get("/analytics/suspicious/").then(r => r.data),
};
