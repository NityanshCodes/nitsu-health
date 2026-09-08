import { useEffect, useState } from "react";
import {
  apiClient,
  type SleepResponse,
  type SleepCreatePayload,
} from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Modal from "../components/ui/Modal";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

export default function Sleep() {
  const [items, setItems] = useState<SleepResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ start_time: "", end_time: "" });

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const result = await apiClient.getSleep();
      setItems(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sleep.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload: SleepCreatePayload = {
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
      };
      await apiClient.createSleepEntry(payload);
      setModalOpen(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save sleep entry.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this sleep entry?")) return;
    try {
      await apiClient.deleteSleepEntry(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete sleep.");
    }
  }

  return (
    <main className="page-shell">
      <PageHeader
        eyebrow="Sleep"
        title="Sleep log"
        subtitle="Log your sleep sessions to track duration patterns."
        actions={<Button onClick={() => setModalOpen(true)}>Log sleep</Button>}
      />

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading sleep…" />
      ) : items.length === 0 ? (
        <EmptyState
          title="No sleep logged"
          message="Log your first sleep session to start tracking."
        />
      ) : (
        <div className="metric-table">
          <div className="metric-table-head">
            <span>Started</span>
            <span>Ended</span>
            <span>Duration</span>
            <span>Source</span>
            <span />
          </div>
          {items.map((s) => (
            <div className="metric-table-row" key={s.id}>
              <span>{s.start_time.slice(0, 16).replace("T", " ")}</span>
              <span>{s.end_time.slice(0, 16).replace("T", " ")}</span>
              <strong>
                {s.duration_minutes
                  ? `${Math.round(s.duration_minutes / 60)}h ${Math.round(
                      s.duration_minutes % 60,
                    )}m`
                  : "—"}
              </strong>
              <span className="muted">{s.source}</span>
              <span>
                <button
                  type="button"
                  className="button button-ghost button-sm"
                  onClick={() => handleDelete(s.id)}
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
        title="Log sleep"
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={handleSubmit} className="modal-form">
          <Input
            label="Start time"
            type="datetime-local"
            value={form.start_time}
            onChange={(e) => setForm({ ...form, start_time: e.target.value })}
          />
          <Input
            label="End time"
            type="datetime-local"
            value={form.end_time}
            onChange={(e) => setForm({ ...form, end_time: e.target.value })}
          />
          <div className="form-actions">
            <Button type="submit" loading={saving}>
              Save sleep
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