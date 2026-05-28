import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

const BASE_URL = (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ?? "/api";

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

// Inject auth token on every request
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const raw = localStorage.getItem("esg_auth");
  if (raw) {
    try {
      const parsed = JSON.parse(raw) as {
        accessToken?: string;
        user?: { organization?: string };
      };
      if (parsed.accessToken) {
        config.headers.Authorization = `Bearer ${parsed.accessToken}`;
      }
      // Always send org header if available — backend also falls back to user.organization
      if (parsed.user?.organization) {
        config.headers["X-Organization-Id"] = parsed.user.organization;
      }
    } catch {}
  }
  return config;
});

// Auto-refresh on 401
let isRefreshing = false;
let queue: Array<{ resolve: (t: string) => void; reject: (e: unknown) => void }> = [];

function processQueue(err: unknown, token: string | null) {
  queue.forEach(p => err ? p.reject(err) : p.resolve(token!));
  queue = [];
}

apiClient.interceptors.response.use(
  r => r,
  async error => {
    const orig = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !orig._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ resolve, reject });
        }).then(token => {
          orig.headers.Authorization = `Bearer ${token}`;
          return apiClient(orig);
        });
      }
      orig._retry = true;
      isRefreshing = true;
      const raw = localStorage.getItem("esg_auth");
      const { refreshToken } = (raw ? JSON.parse(raw) : {}) as { refreshToken?: string };
      if (!refreshToken) {
        localStorage.removeItem("esg_auth");
        window.location.href = "/login";
        return Promise.reject(error);
      }
      try {
        const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh: refreshToken });
        const stored = JSON.parse(localStorage.getItem("esg_auth") || "{}") as { accessToken?: string };
        stored.accessToken = data.access;
        localStorage.setItem("esg_auth", JSON.stringify(stored));
        processQueue(null, data.access);
        orig.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(orig);
      } catch (e) {
        processQueue(e, null);
        localStorage.removeItem("esg_auth");
        window.location.href = "/login";
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);
