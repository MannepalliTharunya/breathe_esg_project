import { useMetrics, usePeriods, useEmissionCategories } from "./useESGData";
import { useFacilities, useDepartments, useOrganizations } from "./useOrganization";
import { useCollectionMethods, useDataSources, useESGCategories } from "./useMasterData";
import { useQuery } from "@tanstack/react-query";
import apiClient from "@/services/api/client";

// ESGFrameworks hook
export function useESGFrameworks() {
  return useQuery({
    queryKey: ["frameworks"],
    queryFn: () => apiClient.get("/frameworks/").then((r) => r.data),
  });
}

/**
 * Consolidated dropdown loading hook to simplify forms.
 * Returns queries for metrics, periods, facilities, and departments.
 */
export function useEsgDropdowns(orgId: string) {
  const metrics = useMetrics();
  const periods = usePeriods();
  const facilities = useFacilities(orgId);
  const departments = useDepartments(orgId);
  const emissionCategories = useEmissionCategories();
  const organizations = useOrganizations();
  const frameworks = useESGFrameworks();
  const collectionMethods = useCollectionMethods();
  const dataSources = useDataSources();
  const esgCategories = useESGCategories();

  return {
    metrics: {
      data: metrics.data?.results ?? [],
      isLoading: metrics.isLoading,
      isError: metrics.isError,
    },
    periods: {
      data: periods.data?.results ?? [],
      isLoading: periods.isLoading,
      isError: periods.isError,
    },
    facilities: {
      data: facilities.data?.results ?? [],
      isLoading: facilities.isLoading,
      isError: facilities.isError,
    },
    departments: {
      data: departments.data?.results ?? [],
      isLoading: departments.isLoading,
      isError: departments.isError,
    },
    emissionCategories: {
      data: emissionCategories.data?.results ?? [],
      isLoading: emissionCategories.isLoading,
      isError: emissionCategories.isError,
    },
    organizations: {
      data: organizations.data?.results ?? [],
      isLoading: organizations.isLoading,
      isError: organizations.isError,
    },
    frameworks: {
      data: frameworks.data?.results ?? [],
      isLoading: frameworks.isLoading,
      isError: frameworks.isError,
    },
    collectionMethods: {
      data: collectionMethods.data?.results ?? [],
      isLoading: collectionMethods.isLoading,
      isError: collectionMethods.isError,
    },
    dataSources: {
      data: dataSources.data?.results ?? [],
      isLoading: dataSources.isLoading,
      isError: dataSources.isError,
    },
    esgCategories: {
      data: esgCategories.data?.results ?? [],
      isLoading: esgCategories.isLoading,
      isError: esgCategories.isError,
    },
  };
}
