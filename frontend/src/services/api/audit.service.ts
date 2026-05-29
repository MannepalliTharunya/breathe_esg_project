import apiClient from "./client";
import type { AuditLog } from "@/types/audit.types";
import type { PaginatedResponse } from "@/types/esg.types";

export const auditService = {
  getLogs: (params?: Record<string, string>) =>
    apiClient
      .get<PaginatedResponse<AuditLog>>("/audit/logs/", { params })
      .then((r) => r.data),
};
