import apiClient from "./client";
import type { PaginatedResponse } from "@/types/esg.types";

export interface MasterRecord {
  id: string;
  code: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DataSourceRecord extends MasterRecord {
  source_type: string;
}

export interface DataUploadRecord {
  id: string;
  file_name: string;
  source_type: string;
  status: string;
  rows_created: number;
  rows_updated: number;
  rows_failed: number;
  uploaded_by_email: string;
  reporting_period_name: string;
  created_at: string;
}

export const masterDataService = {
  getCategories: (params?: Record<string, string>) =>
    apiClient
      .get<PaginatedResponse<MasterRecord>>("/esg/categories/", { params })
      .then((r) => r.data),

  getEmissionScopes: (params?: Record<string, string>) =>
    apiClient
      .get<PaginatedResponse<MasterRecord>>("/esg/emission-scopes/", { params })
      .then((r) => r.data),

  getCollectionMethods: (params?: Record<string, string>) =>
    apiClient
      .get<PaginatedResponse<MasterRecord>>("/esg/collection-methods/", { params })
      .then((r) => r.data),

  getDataSources: (params?: Record<string, string>) =>
    apiClient
      .get<PaginatedResponse<DataSourceRecord>>("/esg/data-sources/", { params })
      .then((r) => r.data),

  getUploads: (params?: Record<string, string>) =>
    apiClient
      .get<PaginatedResponse<DataUploadRecord>>("/esg/uploads/", { params })
      .then((r) => r.data),

  downloadImportTemplate: () =>
    apiClient.get("/esg/data-points/import-template/", { responseType: "blob" }),

  previewBulkImport: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return apiClient
      .post<{
        preview: Array<Record<string, unknown>>;
        row_count: number;
        errors: Array<{ row: number; error: string }>;
        detected_columns?: string[];
      }>(
        "/esg/data-points/bulk-import/preview/",
        form,
        { headers: { "Content-Type": "multipart/form-data" } }
      )
      .then((r) => r.data);
  },
};
