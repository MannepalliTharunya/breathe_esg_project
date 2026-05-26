import { useMutation, useQuery, useQueryClient, keepPreviousData } from "@tanstack/react-query";
import { esgService } from "@/services/api/esg.service";
import { toast } from "@/store/uiStore";
import type { DataPointFilters, ESGDataPointCreate } from "@/types/esg.types";

export const ESG_KEYS = {
  metrics: (params?: Record<string, string>) => ["esg", "metrics", params] as const,
  periods: () => ["esg", "periods"] as const,
  dataPoints: (filters?: DataPointFilters) => ["esg", "data-points", filters] as const,
  dataPoint: (id: string) => ["esg", "data-points", id] as const,
  summary: (periodId?: string) => ["esg", "summary", periodId] as const,
  targets: () => ["esg", "targets"] as const,
  materiality: () => ["esg", "materiality"] as const,
};

export function useMetrics(params?: Record<string, string>) {
  return useQuery({
    queryKey: ESG_KEYS.metrics(params),
    queryFn: () => esgService.getMetrics(params),
  });
}

export function usePeriods() {
  return useQuery({
    queryKey: ESG_KEYS.periods(),
    queryFn: esgService.getPeriods,
  });
}

export function useDataPoints(filters?: DataPointFilters) {
  return useQuery({
    queryKey: ESG_KEYS.dataPoints(filters),
    queryFn: () => esgService.getDataPoints(filters),
    placeholderData: keepPreviousData,
  });
}

export function useDataPoint(id: string) {
  return useQuery({
    queryKey: ESG_KEYS.dataPoint(id),
    queryFn: () => esgService.getDataPoint(id),
    enabled: !!id,
  });
}

export function useESGSummary(periodId?: string) {
  return useQuery({
    queryKey: ESG_KEYS.summary(periodId),
    queryFn: () => esgService.getSummary(periodId),
  });
}

export function useDashboardStats(periodId?: string) {
  return useQuery({
    queryKey: ["esg", "dashboard-stats", periodId],
    queryFn: () => esgService.getDashboardStats(periodId),
  });
}

export function useUploadHistory(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["esg", "upload-history", params],
    queryFn: () => esgService.getUploadHistory(params),
  });
}

export function useAnalytics(periodId?: string) {
  return useQuery({
    queryKey: ["esg", "analytics", periodId],
    queryFn: () => esgService.getAnalytics(periodId),
  });
}

export function useEmissionsSummary(periodId?: string) {
  return useQuery({
    queryKey: ["esg", "emissions-summary", periodId],
    queryFn: () => esgService.getEmissionsSummary(periodId),
  });
}

export function useCreateDataPoint() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ESGDataPointCreate) => esgService.createDataPoint(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["esg", "data-points"] });
      qc.invalidateQueries({ queryKey: ["esg", "summary"] });
      toast.success("Data point submitted");
    },
    onError: () => toast.error("Failed to submit data point"),
  });
}

export function useUpdateDataPointStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      esgService.updateDataPointStatus(id, status, notes),
    onSuccess: (_, { status }) => {
      qc.invalidateQueries({ queryKey: ["esg", "data-points"] });
      toast.success(`Data point ${status}`);
    },
    onError: () => toast.error("Status update failed"),
  });
}

export function useBulkImport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ file, periodId }: { file: File; periodId: string }) =>
      esgService.bulkImport(file, periodId),
    onSuccess: (result) => {
      qc.invalidateQueries({ queryKey: ["esg", "data-points"] });
      toast.success(
        "Import complete",
        `Created: ${result.created}, Updated: ${result.updated}, Errors: ${result.errors.length}`
      );
    },
    onError: () => toast.error("Bulk import failed"),
  });
}

export function useTargets() {
  return useQuery({
    queryKey: ESG_KEYS.targets(),
    queryFn: esgService.getTargets,
  });
}

export function useEmissionCategories() {
  return useQuery({
    queryKey: ["esg", "emission-categories"],
    queryFn: esgService.getEmissionCategories,
  });
}
