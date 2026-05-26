/**
 * Organization store — tracks the active org context.
 * The active org ID is sent as X-Organization-Id on every API request.
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { Organization } from "@/types/organization.types";

interface OrganizationState {
  activeOrganizationId: string | null;
  activeOrganization: Organization | null;
  organizations: Organization[];

  setActiveOrganization: (org: Organization) => void;
  setOrganizations: (orgs: Organization[]) => void;
  clearOrganization: () => void;
}

export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set) => ({
      activeOrganizationId: null,
      activeOrganization: null,
      organizations: [],

      setActiveOrganization: (org) =>
        set({ activeOrganizationId: org.id, activeOrganization: org }),

      setOrganizations: (orgs) => set({ organizations: orgs }),

      clearOrganization: () =>
        set({ activeOrganizationId: null, activeOrganization: null }),
    }),
    {
      name: "esg-org",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        activeOrganizationId: state.activeOrganizationId,
        activeOrganization: state.activeOrganization,
      }),
    }
  )
);
