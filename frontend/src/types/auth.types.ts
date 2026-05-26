export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: UserRole;
  avatar: string | null;
  phone: string;
  job_title: string;
  department: string;
  timezone: string;
  locale: string;
  is_verified: boolean;
  mfa_enabled: boolean;
  created_at: string;
  preferences: UserPreferences;
}

export type UserRole =
  | "super_admin"
  | "org_admin"
  | "esg_manager"
  | "analyst"
  | "viewer"
  | "auditor";

export interface UserPreferences {
  email_notifications: boolean;
  report_ready_notifications: boolean;
  data_alert_notifications: boolean;
  dashboard_layout: Record<string, unknown>;
  default_framework: string;
  default_reporting_period: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  job_title?: string;
  department?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}
