import { useEffect, useState } from "react";
import {
  apiClient,
  type NotificationResponse,
} from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Button from "../components/ui/Button";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

export default function Notifications() {
  const [items, setItems] = useState<NotificationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const result = await apiClient.getNotifications();
      setItems(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load notifications.");
    } finally {
      setLoading(false);
    }
  }

  async function markRead(id: number) {
    try {
      await apiClient.markNotificationRead(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update notification.");
    }
  }

  async function markAllRead() {
    try {
      await apiClient.markAllNotificationsRead();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update notifications.");
    }
  }

  return (
    <main className="page-shell">
      <PageHeader
        eyebrow="Inbox"
        title="Notifications"
        actions={
          <Button variant="secondary" onClick={markAllRead}>
            Mark all read
          </Button>
        }
      />

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading notifications…" />
      ) : items.length === 0 ? (
        <EmptyState
          title="No notifications"
          message="Notifications about goals, reports, and data reminders will appear here."
        />
      ) : (
        <ul className="notification-list">
          {items.map((n) => (
            <li
              key={n.id}
              className={`notification-item ${n.is_read ? "read" : "unread"}`}
              onClick={() => !n.is_read && markRead(n.id)}
            >
              <div>
                <strong>{n.title}</strong>
                {n.body && <p className="muted">{n.body}</p>}
                <p className="muted" style={{ fontSize: "0.8rem" }}>
                  {n.created_at.slice(0, 16).replace("T", " ")}
                </p>
              </div>
              {!n.is_read && <span className="unread-dot" />}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}