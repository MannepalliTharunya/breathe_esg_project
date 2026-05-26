import { apiClient } from "./client";

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post("/auth/login/", { email, password }).then(r => r.data),

  register: (data: { email: string; first_name: string; last_name: string; password: string; password_confirm: string; role?: string }) =>
    apiClient.post("/auth/register/", data).then(r => r.data),

  logout: (refresh: string) =>
    apiClient.post("/auth/logout/", { refresh }),

  me: () =>
    apiClient.get("/auth/me/").then(r => r.data),
};
