import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "../services/api/analytics";
import type { DashboardSummary, MonthlyTrend, IngestionQuality } from "../types";

export const ANALYTICS_KEYS = {
  dashboard: ["analytics", "dashboard"] as const,
  bySource: ["analytics", "by-source"] as const,
  monthly: (scope?: string) => ["analytics", "monthly", scope] as const,
  byFacility: ["analytics", "by-facility"] as const,
  quality: ["analytics", "quality"] as const,
  suspicious: ["analytics", "suspicious"] as const,
};

export function useDashboard() {
  return useQuery<DashboardSummary>({
    queryKey: ANALYTICS_KEYS.dashboard,
    queryFn: analyticsApi.dashboard,
    refetchInterval: 30_000,
  });
}

export function useEmissionsBySource() {
  return useQuery({
    queryKey: ANALYTICS_KEYS.bySource,
    queryFn: analyticsApi.emissionsBySource,
  });
}

export function useMonthlyTrend(scope?: string) {
  return useQuery<MonthlyTrend[]>({
    queryKey: ANALYTICS_KEYS.monthly(scope),
    queryFn: () => analyticsApi.monthlyTrend(scope),
  });
}

export function useFacilityEmissions() {
  return useQuery({
    queryKey: ANALYTICS_KEYS.byFacility,
    queryFn: analyticsApi.facilityEmissions,
  });
}

export function useIngestionQuality() {
  return useQuery<IngestionQuality[]>({
    queryKey: ANALYTICS_KEYS.quality,
    queryFn: analyticsApi.ingestionQuality,
  });
}

export function useSuspiciousRecords() {
  return useQuery({
    queryKey: ANALYTICS_KEYS.suspicious,
    queryFn: analyticsApi.suspicious,
  });
}
