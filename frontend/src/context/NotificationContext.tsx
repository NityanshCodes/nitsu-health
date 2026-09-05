import { createContext, type ReactNode } from "react";

interface NotificationContextValue {
  notifications: string[];
}

export const NotificationContext =
  createContext<NotificationContextValue | null>(null);

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
  return (
    <NotificationContext.Provider value={{ notifications: [] }}>
      {children}
    </NotificationContext.Provider>
  );
};
