import { useEffect, useState } from "react";
import {
  apiClient,
  type ActivityResponse,
  type ActivityCreatePayload,
} from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Modal from "../components/ui/Modal";
import Button from "../components/ui/Button";
import Select from "../components/ui/Select";
import Input from "../components/ui/Input";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

const ACTIVITY_TYPES = [
  { value: "walking", label: "Walking" },
  { value: "running", label: "Running" },
  { value: "cycling", label: "Cycling" },
  { value: "swimming", label: "Swimming" },
  { value: "gym", label: "Gym workout" },
  { value: "yoga", label: "Yoga" },
  { value: "other", label: "Other" },
];

export default function Activity() {
  const [items, setItems] = useState<ActivityResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    activity_type: "walking",
    steps: 0,
    active_minutes: 0,
    distance_km: 0,
    calories_burned: 0,
  });

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const result = await apiClient.getActivity();
      setItems(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load activity.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload: ActivityCreatePayload = {
        activity_type: form.activity_type,
        steps: form.steps || null,
        active_minutes: form.active_minutes || null,
        distance_km: form.distance_km || null,
        calories_burned: form.calories_burned || null,
      };
      await apiClient.createActivityEntry(payload);
      setModalOpen(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save activity.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this activity entry?")) return;
    try {
      await apiClient.deleteActivityEntry(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete activity.");
    }
  }

  return (
    <main className="page-shell">
      <PageHeader
        eyebrow="Activity"
        title="Activity log"
        subtitle="Calorie figures are estimates, not precise measurements."
        actions={<Button onClick={() => setModalOpen(true)}>Log activity</Button>}
      />

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading activity…" />
      ) : items.length === 0 ? (
        <EmptyState
          title="No activity logged"
          message="Log your first activity to start tracking."
        />
      ) : (
        <div className="metric-table">
          <div className="metric-table-head">
            <span>Activity</span>
            <span>Steps</span>
            <span>Active min</span>
            <span>Distance</span>
            <span>Calories</span>
            <span>Date</span>
            <span />
          </div>
          {items.map((a) => (
            <div className="metric-table-row" key={a.id}>
              <span>{a.activity_type}</span>
              <strong>{a.steps ?? "—"}</strong>
              <span>{a.active_minutes ?? "—"}</span>
              <span>
                {a.distance_km != null ? `${a.distance_km} km` : "—"}
              </span>
              <span>{a.calories_burned ?? "—"}</span>
              <span className="muted">{a.recorded_at.slice(0, 10)}</span>
              <span>
                <button
                  type="button"
                  className="button button-ghost button-sm"
                  onClick={() => handleDelete(a.id)}
                >
                  Delete
                </button>
              </span>
            </div>
          ))}
        </div>
      )}

      <Modal
        open={modalOpen}
        title="Log activity"
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={handleSubmit} className="modal-form">
          <Select
            label="Activity type"
            options={ACTIVITY_TYPES}
            value={form.activity_type}
            onChange={(e) => setForm({ ...form, activity_type: e.target.value })}
          />
          <Input
            label="Steps (optional)"
            type="number"
            min={0}
            value={form.steps}
            onChange={(e) => setForm({ ...form, steps: Number(e.target.value) })}
          />
          <Input
            label="Active minutes"
            type="number"
            min={0}
            value={form.active_minutes}
            onChange={(e) =>
              setForm({ ...form, active_minutes: Number(e.target.value) })
            }
          />
          <Input
            label="Distance (km)"
            type="number"
            step="any"
            min={0}
            value={form.distance_km}
            onChange={(e) =>
              setForm({ ...form, distance_km: Number(e.target.value) })
            }
          />
          <Input
            label="Calories burned (estimate)"
            type="number"
            min={0}
            value={form.calories_burned}
            onChange={(e) =>
              setForm({ ...form, calories_burned: Number(e.target.value) })
            }
          />
          <div className="form-actions">
            <Button type="submit" loading={saving}>
              Save activity
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </main>
  );
}