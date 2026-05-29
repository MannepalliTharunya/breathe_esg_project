export type AuditAction =
  | "create"
  | "update"
  | "delete"
  | "login"
  | "logout"
  | "export"
  | "approve"
  | "reject"
  | "publish"
  | "import";

export interface AuditLog {
  id: string;
  user_id: string | null;
  user_email: string;
  organization_id: string | null;
  action: AuditAction;
  resource_type: string;
  resource_id: string;
  ip_address: string | null;
  request_method: string;
  request_path: string;
  changes: Record<string, unknown>;
  metadata: Record<string, unknown>;
  status_code: number | null;
  created_at: string;
}
