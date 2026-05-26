import { useQuery, useMutation, useQueryClient, keepPreviousData } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { reviewApi } from "../services/api/review";
import type { NormalizedRecord, PaginatedResponse } from "../types";

export const REVIEW_KEYS = {
  list: (params: Record<string, unknown>) => ["review", "records", params] as const,
  detail: (id: string) => ["review", "records", id] as const,
  history: (id: string) => ["review", "history", id] as const,
};

export function useRecords(params: Record<string, string | boolean | number> = {}) {
  return useQuery<PaginatedResponse<NormalizedRecord>>({
    queryKey: REVIEW_KEYS.list(params),
    queryFn: () => reviewApi.getRecords(params),
    placeholderData: keepPreviousData,
  });
}

export function useRecord(id: string) {
  return useQuery<NormalizedRecord>({
    queryKey: REVIEW_KEYS.detail(id),
    queryFn: () => reviewApi.getRecord(id),
    enabled: !!id,
  });
}

export function useRecordHistory(id: string) {
  return useQuery({
    queryKey: REVIEW_KEYS.history(id),
    queryFn: () => reviewApi.getHistory(id),
    enabled: !!id,
  });
}

export function useApprove() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      reviewApi.approve(id, comment),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["review"] });
      qc.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Record approved and locked");
    },
    onError: () => toast.error("Failed to approve record"),
  });
}

export function useReject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      reviewApi.reject(id, comment),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["review"] });
      qc.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Record rejected");
    },
    onError: () => toast.error("Failed to reject record"),
  });
}

export function useFlag() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      reviewApi.flag(id, comment),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["review"] });
      toast.success("Record flagged for review");
    },
    onError: () => toast.error("Failed to flag record"),
  });
}

export function useBulkAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ ids, decision, comment }: { ids: string[]; decision: string; comment?: string }) =>
      reviewApi.bulkAction(ids, decision, comment),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["review"] });
      qc.invalidateQueries({ queryKey: ["analytics"] });
      toast.success(`${data.updated} records ${data.decision}`);
    },
    onError: () => toast.error("Bulk action failed"),
  });
}
