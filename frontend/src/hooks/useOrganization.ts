import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationsService } from "@/services/api/organizations.service";
import { useOrganizationStore } from "@/store/organizationStore";
import { toast } from "@/store/uiStore";

export const ORG_KEYS = {
  all: ["organizations"] as const,
  detail: (id: string) => ["organizations", id] as const,
  facilities: (orgId: string) => ["organizations", orgId, "facilities"] as const,
  members: (orgId: string) => ["organizations", orgId, "members"] as const,
};

export function useOrganizations() {
  const { setOrganizations } = useOrganizationStore();
  return useQuery({
    queryKey: ORG_KEYS.all,
    queryFn: async () => {
      const data = await organizationsService.getOrganizations();
      setOrganizations(data.results);
      return data;
    },
  });
}

export function useFacilities(orgId: string) {
  return useQuery({
    queryKey: ORG_KEYS.facilities(orgId),
    queryFn: () => organizationsService.getFacilities(orgId),
    enabled: !!orgId,
  });
}

export function useDepartments(orgId: string) {
  return useQuery({
    queryKey: ["organizations", orgId, "departments"],
    queryFn: () => organizationsService.getDepartments(orgId),
    enabled: !!orgId,
  });
}

export function useMembers(orgId: string) {
  return useQuery({
    queryKey: ORG_KEYS.members(orgId),
    queryFn: () => organizationsService.getMembers(orgId),
    enabled: !!orgId,
  });
}

export function useInviteMember(orgId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      organizationsService.inviteMember(orgId, userId, role),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ORG_KEYS.members(orgId) });
      toast.success("Member invited");
    },
    onError: () => toast.error("Failed to invite member"),
  });
}
