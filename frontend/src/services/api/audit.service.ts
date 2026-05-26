import apiClient from "./client";
import type { AuditLog, PaginatedResponse } from "@/types/audit.types";

export const auditService = {
  getLogs: (params?: Record<string, string>) =>
    apiClient
      .get<PaginatedResponse<AuditLog>>("/audit/logs/", { params })
      .then((r) => r.data),
};
