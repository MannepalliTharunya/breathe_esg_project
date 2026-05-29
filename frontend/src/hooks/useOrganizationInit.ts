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
  const { activeOrganizationId, setActiveOrganization, clearOrganization } = useOrganizationStore();

  useEffect(() => {
    if (!isAuthenticated || isLoading) return;

    if (!data?.results.length) {
      clearOrganization();
      return;
    }

    const existing = activeOrganizationId
      ? data.results.find((o: { id: string }) => o.id === activeOrganizationId)
      : undefined;

    if (existing) {
      setActiveOrganization(existing);
      return;
    }

    // Prefer org with seeded demo data, else first membership
    const preferred =
      data.results.find((o: { name: string }) => o.name === "RGVF Manufacturing") ?? data.results[0];
    setActiveOrganization(preferred);
  }, [isAuthenticated, isLoading, data, activeOrganizationId, setActiveOrganization, clearOrganization]);

  return { isLoading, organizations: data?.results ?? [] };
}
