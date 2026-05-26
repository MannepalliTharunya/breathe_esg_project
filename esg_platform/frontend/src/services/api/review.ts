import { apiClient } from "./client";

export const reviewApi = {
  getRecords: (params?: Record<string, string | boolean | number>) =>
    apiClient.get("/normalization/records/", { params }).then(r => r.data),

  getRecord: (id: string) =>
    apiClient.get(`/normalization/records/${id}/`).then(r => r.data),

  approve: (id: string, comment = "") =>
    apiClient.post(`/normalization/records/${id}/approve/`, { comment }).then(r => r.data),

  reject: (id: string, comment = "") =>
    apiClient.post(`/normalization/records/${id}/reject/`, { comment }).then(r => r.data),

  flag: (id: string, comment = "") =>
    apiClient.post(`/normalization/records/${id}/flag/`, { comment }).then(r => r.data),

  getHistory: (id: string) =>
    apiClient.get(`/normalization/records/${id}/history/`).then(r => r.data),

  bulkAction: (record_ids: string[], decision: string, comment = "") =>
    apiClient.post("/normalization/records/bulk-action/", { record_ids, decision, comment }).then(r => r.data),
};
