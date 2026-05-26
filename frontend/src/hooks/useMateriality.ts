import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { esgService } from "@/services/api/esg.service";
import { toast } from "@/store/uiStore";
import type { MaterialityAssessment } from "@/types/esg.types";

export const MATERIALITY_KEYS = {
  all: ["materiality"] as const,
};

export function useMaterialityAssessments() {
  return useQuery({
    queryKey: MATERIALITY_KEYS.all,
    queryFn: esgService.getMaterialityAssessments,
  });
}

export function useCreateMaterialityAssessment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Omit<MaterialityAssessment, "id" | "created_at" | "updated_at">) =>
      esgService.createMaterialityAssessment(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: MATERIALITY_KEYS.all });
      toast.success("Materiality assessment saved");
    },
    onError: () => toast.error("Failed to save materiality assessment"),
  });
}
