import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reportsService } from "@/services/api/reports.service";
import { toast } from "@/store/uiStore";
import type { ReportCreate } from "@/types/reports.types";

export const REPORT_KEYS = {
  all: ["reports"] as const,
  detail: (id: string) => ["reports", id] as const,
};

export function useReports(params?: Record<string, string>) {
  return useQuery({
    queryKey: [...REPORT_KEYS.all, params],
    queryFn: () => reportsService.getReports(params),
  });
}

export function useReport(id: string) {
  return useQuery({
    queryKey: REPORT_KEYS.detail(id),
    queryFn: () => reportsService.getReport(id),
    enabled: !!id,
    // Poll while generating
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "generating" ? 5000 : false;
    },
  });
}

export function useCreateReport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ReportCreate) => reportsService.createReport(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: REPORT_KEYS.all });
      toast.success("Report queued", "Your report is being generated.");
    },
    onError: () => toast.error("Failed to create report"),
  });
}

export function useRegenerateReport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => reportsService.regenerateReport(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: REPORT_KEYS.detail(id) });
      toast.info("Regenerating report...");
    },
  });
}
