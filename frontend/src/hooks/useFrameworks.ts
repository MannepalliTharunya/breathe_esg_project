import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/services/api/client";
import { toast } from "@/store/uiStore";

export const FRAMEWORK_KEYS = {
  all: ["frameworks"] as const,
  requirements: (frameworkId?: string) => ["frameworks", "requirements", frameworkId] as const,
  orgFrameworks: () => ["frameworks", "organization"] as const,
};

export function useFrameworks() {
  return useQuery({
    queryKey: FRAMEWORK_KEYS.all,
    queryFn: () => apiClient.get("/frameworks/").then((r) => r.data),
    staleTime: 1000 * 60 * 30, // frameworks rarely change
  });
}

export function useFrameworkRequirements(frameworkId?: string) {
  return useQuery({
    queryKey: FRAMEWORK_KEYS.requirements(frameworkId),
    queryFn: () =>
      apiClient
        .get("/frameworks/requirements/", { params: frameworkId ? { framework_id: frameworkId } : {} })
        .then((r) => r.data),
    enabled: !!frameworkId,
  });
}

export function useOrganizationFrameworks() {
  return useQuery({
    queryKey: FRAMEWORK_KEYS.orgFrameworks(),
    queryFn: () => apiClient.get("/frameworks/organization/").then((r) => r.data),
  });
}

export function useAdoptFramework() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { framework_id: string; adopted_at: string; is_primary: boolean }) =>
      apiClient.post("/frameworks/organization/", data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: FRAMEWORK_KEYS.orgFrameworks() });
      toast.success("Framework adopted");
    },
    onError: () => toast.error("Failed to adopt framework"),
  });
}
