import apiClient from "./client";
import type { NotificationsResponse } from "@/types/notifications.types";

export const notificationsService = {
  getNotifications: (unreadOnly = false) =>
    apiClient
      .get<NotificationsResponse>("/notifications/", {
        params: unreadOnly ? { unread: "true" } : {},
      })
      .then((r) => r.data),

  markRead: (id: string) =>
    apiClient.patch(`/notifications/${id}/read/`),

  markAllRead: () =>
    apiClient.post("/notifications/read-all/"),
};
