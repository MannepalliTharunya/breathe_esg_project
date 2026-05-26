import apiClient from "./client";
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  UserPreferences,
} from "@/types/auth.types";

export const authService = {
  login: (data: LoginRequest) =>
    apiClient.post<AuthResponse>("/auth/login/", data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    apiClient.post<AuthResponse>("/auth/register/", data).then((r) => r.data),

  logout: (refreshToken: string) =>
    apiClient.post("/auth/logout/", { refresh: refreshToken }),

  refreshToken: (refresh: string) =>
    apiClient.post<{ access: string }>("/auth/token/refresh/", { refresh }).then((r) => r.data),

  requestPasswordReset: (email: string) =>
    apiClient.post("/auth/password/reset/", { email }),

  confirmPasswordReset: (token: string, newPassword: string, newPasswordConfirm: string) =>
    apiClient.post("/auth/password/reset/confirm/", {
      token,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    }),

  getMe: () => apiClient.get<User>("/users/me/").then((r) => r.data),

  updateMe: (data: Partial<User>) =>
    apiClient.patch<User>("/users/me/", data).then((r) => r.data),

  changePassword: (currentPassword: string, newPassword: string, newPasswordConfirm: string) =>
    apiClient.post("/users/me/password/", {
      current_password: currentPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    }),

  getPreferences: () =>
    apiClient.get<UserPreferences>("/users/me/preferences/").then((r) => r.data),

  updatePreferences: (data: Partial<UserPreferences>) =>
    apiClient.patch<UserPreferences>("/users/me/preferences/", data).then((r) => r.data),
};
