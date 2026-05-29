import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/api/auth.service";
import { useAuthStore } from "@/store/authStore";
import { toast } from "@/store/uiStore";
import { getApiErrorMessage } from "@/utils/apiError";
import type { LoginRequest, RegisterRequest } from "@/types/auth.types";

export const AUTH_KEYS = {
  me: ["auth", "me"] as const,
  preferences: ["auth", "preferences"] as const,
};

export function useMe() {
  const { isAuthenticated } = useAuthStore();
  return useQuery({
    queryKey: AUTH_KEYS.me,
    queryFn: authService.getMe,
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 10,
  });
}

export function useLogin() {
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (response) => {
      setTokens(response.access, response.refresh);
      setUser(response.user);
      queryClient.setQueryData(AUTH_KEYS.me, response.user);
      toast.success("Welcome back!", `Logged in as ${response.user.email}`);
      navigate("/dashboard");
    },
    onError: (error) => {
      toast.error("Login failed", getApiErrorMessage(error, "Invalid email or password."));
    },
  });
}

export function useRegister() {
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  return useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: (response) => {
      setTokens(response.access, response.refresh);
      setUser(response.user);
      toast.success("Account created", "Welcome to the ESG Platform.");
      navigate("/dashboard");
    },
    onError: (error) => {
      toast.error("Registration failed", getApiErrorMessage(error, "Please check your details and try again."));
    },
  });
}

export function useLogout() {
  const navigate = useNavigate();
  const { refreshToken, logout } = useAuthStore();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authService.logout(refreshToken ?? ""),
    onSettled: () => {
      logout();
      queryClient.clear();
      navigate("/auth/login");
    },
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: ({
      currentPassword,
      newPassword,
      newPasswordConfirm,
    }: {
      currentPassword: string;
      newPassword: string;
      newPasswordConfirm: string;
    }) => authService.changePassword(currentPassword, newPassword, newPasswordConfirm),
    onSuccess: () => toast.success("Password changed", "Your password has been updated."),
    onError: () => toast.error("Failed to change password"),
  });
}
