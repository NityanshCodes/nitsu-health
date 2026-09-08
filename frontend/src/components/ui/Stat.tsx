import type { ReactNode } from "react";

interface StatProps {
  label: ReactNode;
  value: ReactNode;
  hint?: ReactNode;
  accent?: boolean;
}

export default function Stat({ label, value, hint, accent = false }: StatProps) {
  return (
    <div className={`stat ${accent ? "stat-accent" : ""}`.trim()}>
      <span className="muted">{label}</span>
      <strong>{value}</strong>
      {hint && <p className="stat-hint">{hint}</p>}
    </div>
  );
}