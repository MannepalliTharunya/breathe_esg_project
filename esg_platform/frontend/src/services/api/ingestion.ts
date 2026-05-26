import { apiClient } from "./client";

export const ingestionApi = {
  getBatches: (params?: Record<string, string>) =>
    apiClient.get("/ingestion/batches/", { params }).then(r => r.data),

  getBatch: (id: string) =>
    apiClient.get(`/ingestion/batches/${id}/`).then(r => r.data),

  uploadBatch: (formData: FormData) =>
    apiClient.post("/ingestion/batches/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then(r => r.data),

  reprocess: (id: string) =>
    apiClient.post(`/ingestion/batches/${id}/reprocess/`).then(r => r.data),

  preview: (id: string) =>
    apiClient.get(`/ingestion/batches/${id}/preview/`).then(r => r.data),
};
