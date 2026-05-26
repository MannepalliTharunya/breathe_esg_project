export type NotificationType =
  | "data_submitted"
  | "data_approved"
  | "data_rejected"
  | "report_ready"
  | "target_alert"
  | "system";

export interface Notification {
  id: string;
  notification_type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  read_at: string | null;
  action_url: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface NotificationsResponse {
  pagination: {
    count: number;
    total_pages: number;
    current_page: number;
    next: string | null;
    previous: string | null;
  };
  results: Notification[];
  unread_count: number;
}
