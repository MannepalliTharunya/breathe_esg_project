import { AxiosError } from "axios";

/** Extract a human-readable message from a DRF / Axios error response. */
export function getApiErrorMessage(error: unknown, fallback = "Request failed"): string {
  if (!error || typeof error !== "object") return fallback;

  const axiosErr = error as AxiosError<{
    error?: { message?: string };
    detail?: string;
    message?: string;
  }>;

  const data = axiosErr.response?.data;
  if (data && typeof data === "object") {
    if (data.error?.message) return data.error.message;
    if (typeof data.detail === "string") return data.detail;
    if (typeof data.message === "string") return data.message;
  }

  if (axiosErr.message) return axiosErr.message;
  return fallback;
}
