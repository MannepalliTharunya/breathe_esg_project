import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { ingestionApi } from "../services/api/ingestion";
import type { UploadBatch, PaginatedResponse } from "../types";

export const INGESTION_KEYS = {
  list: (params?: Record<string, string>) => ["ingestion", "batches", params] as const,
  detail: (id: string) => ["ingestion", "batches", id] as const,
  preview: (id: string) => ["ingestion", "preview", id] as const,
};

export function useBatches(params?: Record<string, string>) {
  return useQuery<PaginatedResponse<UploadBatch>>({
    queryKey: INGESTION_KEYS.list(params),
    queryFn: () => ingestionApi.getBatches(params),
    refetchInterval: 10_000, // poll while batches are processing
  });
}

export function useBatch(id: string) {
  return useQuery<UploadBatch>({
    queryKey: INGESTION_KEYS.detail(id),
    queryFn: () => ingestionApi.getBatch(id),
    enabled: !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "processing" || status === "pending" ? 3000 : false;
    },
  });
}

export function useUpload() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => ingestionApi.uploadBatch(formData),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ingestion"] });
      qc.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("File uploaded — processing started");
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { error?: { message?: string } } } })
        ?.response?.data?.error?.message ?? "Upload failed";
      toast.error(msg);
    },
  });
}

export function useReprocess() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ingestionApi.reprocess(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ingestion"] });
      toast.success("Reprocessing started");
    },
    onError: () => toast.error("Reprocess failed"),
  });
}
