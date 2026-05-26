import { useQuery } from "@tanstack/react-query";
import { masterDataService } from "@/services/api/masterData.service";
import { useOrganizationStore } from "@/store/organizationStore";

export const MASTER_KEYS = {
  categories: ["master", "categories"] as const,
  emissionScopes: ["master", "emission-scopes"] as const,
  collectionMethods: ["master", "collection-methods"] as const,
  dataSources: (sourceType?: string) => ["master", "data-sources", sourceType] as const,
  uploads: (params?: Record<string, string>) => ["master", "uploads", params] as const,
};

function useOrgEnabled() {
  const { activeOrganizationId } = useOrganizationStore();
  return !!activeOrganizationId;
}

export function useESGCategories() {
  const enabled = useOrgEnabled();
  return useQuery({
    queryKey: MASTER_KEYS.categories,
    queryFn: () => masterDataService.getCategories({ page_size: "100" }),
    enabled,
  });
}

export function useEmissionScopes() {
  const enabled = useOrgEnabled();
  return useQuery({
    queryKey: MASTER_KEYS.emissionScopes,
    queryFn: () => masterDataService.getEmissionScopes({ page_size: "100" }),
    enabled,
  });
}

export function useCollectionMethods() {
  const enabled = useOrgEnabled();
  return useQuery({
    queryKey: MASTER_KEYS.collectionMethods,
    queryFn: () => masterDataService.getCollectionMethods({ page_size: "100" }),
    enabled,
  });
}

export function useDataSources(sourceType?: string) {
  const enabled = useOrgEnabled();
  return useQuery({
    queryKey: MASTER_KEYS.dataSources(sourceType),
    queryFn: () =>
      masterDataService.getDataSources({
        page_size: "100",
        ...(sourceType ? { source_type: sourceType } : {}),
      }),
    enabled,
  });
}

export function useDataUploads(params?: Record<string, string>) {
  const enabled = useOrgEnabled();
  return useQuery({
    queryKey: MASTER_KEYS.uploads(params),
    queryFn: () => masterDataService.getUploads(params),
    enabled,
  });
}
