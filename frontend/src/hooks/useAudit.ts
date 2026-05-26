import { useQuery } from "@tanstack/react-query";
import { auditService } from "@/services/api/audit.service";

export const AUDIT_KEYS = {
  logs: (params?: Record<string, string>) => ["audit", "logs", params] as const,
};

export function useAuditLogs(params?: Record<string, string>) {
  return useQuery({
    queryKey: AUDIT_KEYS.logs(params),
    queryFn: () => auditService.getLogs(params),
    staleTime: 1000 * 60 * 2,
  });
}
