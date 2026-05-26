import { apiClient } from "./client";

export const auditApi = {
  getLogs: (params?: Record<string, string>) =>
    apiClient.get("/audit/logs/", { params }).then(r => r.data),
};
