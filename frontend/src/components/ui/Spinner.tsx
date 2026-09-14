export default function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="spinner" role="status">
      <span className="spinner-dot" />
      <span className="muted">{label}</span>
    </div>
  );
}