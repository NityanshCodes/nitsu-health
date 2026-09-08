import type { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  message?: string;
  action?: ReactNode;
}

export default function EmptyState({ title, message, action }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <p className="empty-state-title">{title}</p>
      {message && <p className="muted">{message}</p>}
      {action && <div className="empty-state-action">{action}</div>}
    </div>
  );
}