import { create } from "zustand";

export type NotificationType = "success" | "warning" | "error" | "info";

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

interface NotificationStore {
  notifications: NotificationItem[];
  addNotification: (type: NotificationType, title: str, message: str) => void;
  markAsRead: (id: string) => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [
    {
      id: "not_1",
      type: "info",
      title: "System Seeding",
      message: "AgentSphere database seeded with support workflows.",
      timestamp: new Date().toLocaleTimeString(),
      read: false,
    },
  ],
  addNotification: (type, title, message) =>
    set((state) => ({
      notifications: [
        {
          id: `not_${Date.now()}`,
          type,
          title,
          message,
          timestamp: new Date().toLocaleTimeString(),
          read: false,
        },
        ...state.notifications,
      ],
    })),
  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
    })),
  clearAll: () => set({ notifications: [] }),
}));
