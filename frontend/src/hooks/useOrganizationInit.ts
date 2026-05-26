/**
 * Bootstraps the active organization on app load.
 * If the user has only one org, auto-selects it.
 * If they have multiple, they need to pick one.
 */
import { useEffect } from "react";
import { useOrganizations } from "./useOrganization";
import { useOrganizationStore } from "@/store/organizationStore";
import { useAuthStore } from "@/store/authStore";

export function useOrganizationInit() {
  const { isAuthenticated } = useAuthStore();
  const { data, isLoading } = useOrganizations();
  const { activeOrganizationId, setActiveOrganization } = useOrganizationStore();

  useEffect(() => {
    if (!isAuthenticated || isLoading || !data?.results.length) return;

    // Already have an active org that exists in the list — keep it
    if (activeOrganizationId) {
      const existing = data.results.find((o) => o.id === activeOrganizationId);
      if (existing) return;
    }

    // Auto-select the first org
    setActiveOrganization(data.results[0]);
  }, [isAuthenticated, isLoading, data, activeOrganizationId, setActiveOrganization]);

  return { isLoading, organizations: data?.results ?? [] };
}
