import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notificationsService } from "@/services/api/notifications.service";
import { toast } from "@/store/uiStore";

export const NOTIFICATION_KEYS = {
  all: ["notifications"] as const,
  unread: ["notifications", "unread"] as const,
};

export function useNotifications(unreadOnly = false) {
  return useQuery({
    queryKey: unreadOnly ? NOTIFICATION_KEYS.unread : NOTIFICATION_KEYS.all,
    queryFn: () => notificationsService.getNotifications(unreadOnly),
    // Poll every 30s for new notifications
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
}

export function useUnreadCount() {
  const { data } = useNotifications(true);
  return data?.unread_count ?? 0;
}

export function useMarkRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationsService.markRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: NOTIFICATION_KEYS.all });
    },
  });
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => notificationsService.markAllRead(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: NOTIFICATION_KEYS.all });
      toast.success("All notifications marked as read");
    },
  });
}
