import { useEffect, useState } from "react";
import {
  apiClient,
  type GoalResponse,
  type GoalCreatePayload,
} from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Card from "../components/ui/Card";
import Modal from "../components/ui/Modal";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

const GOAL_TYPES = [
  { value: "steps", label: "Steps per day" },
  { value: "weight", label: "Weight" },
  { value: "nutrition", label: "Nutrition" },
  { value: "water", label: "Water intake" },
  { value: "sleep", label: "Sleep duration" },
  { value: "exercise", label: "Exercise" },
  { value: "other", label: "Other" },
];

export default function Goals() {
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    goal_type: "steps",
    title: "",
    target_value: 0,
    unit: "steps",
    start_date: new Date().toISOString().slice(0, 10),
    target_date: "",
  });

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const result = await apiClient.getGoals();
      setGoals(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load goals.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload: GoalCreatePayload = {
        goal_type: form.goal_type,
        title: form.title,
        target_value: form.target_value,
        unit: form.unit,
        start_date: form.start_date,
        target_date: form.target_date,
      };
      await apiClient.createGoal(payload);
      setModalOpen(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save goal.");
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdateProgress(goal: GoalResponse, next: number) {
    try {
      await apiClient.updateGoalProgress(goal.id, next);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update progress.");
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this goal?")) return;
    try {
      await apiClient.deleteGoal(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete goal.");
    }
  }

  return (
    <main className="page-shell">
      <PageHeader
        eyebrow="Goals"
        title="Health goals"
        subtitle="Set realistic targets and track progress. Slow, steady progress beats none."
        actions={<Button onClick={() => setModalOpen(true)}>New goal</Button>}
      />

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading goals…" />
      ) : goals.length === 0 ? (
        <EmptyState
          title="No goals yet"
          message="Create a goal to give your tracking a direction."
        />
      ) : (
        <div className="goal-grid">
          {goals.map((g) => {
            const pct =
              g.target_value > 0
                ? Math.min(100, Math.round((g.progress_value / g.target_value) * 100))
                : 0;
            return (
              <Card
                key={g.id}
                title={g.title}
                subtitle={`${g.goal_type} · ${g.start_date} → ${g.target_date}`}
                actions={
                  <button
                    type="button"
                    className="button button-ghost button-sm"
                    onClick={() => handleDelete(g.id)}
                  >
                    Delete
                  </button>
                }
              >
                <div className="goal-row">
                  <span className="muted">
                    {g.progress_value}/{g.target_value} {g.unit}
                  </span>
                  <strong>{pct}%</strong>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${pct}%` }} />
                </div>
                {g.status === "active" && (
                  <button
                    type="button"
                    className="button button-secondary button-sm"
                    style={{ marginTop: "0.75rem" }}
                    onClick={() =>
                      handleUpdateProgress(g, g.progress_value + 1)
                    }
                  >
                    Bump progress +1
                  </button>
                )}
                {g.status === "completed" && (
                  <p className="muted" style={{ marginTop: "0.75rem" }}>
                    ✓ Completed
                  </p>
                )}
              </Card>
            );
          })}
        </div>
      )}

      <Modal
        open={modalOpen}
        title="Create goal"
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={handleSubmit} className="modal-form">
          <Select
            label="Goal type"
            options={GOAL_TYPES}
            value={form.goal_type}
            onChange={(e) => setForm({ ...form, goal_type: e.target.value })}
          />
          <Input
            label="Title"
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
          <Input
            label="Target value"
            type="number"
            step="any"
            min={1}
            required
            value={form.target_value}
            onChange={(e) =>
              setForm({ ...form, target_value: Number(e.target.value) })
            }
          />
          <Input
            label="Unit"
            value={form.unit}
            onChange={(e) => setForm({ ...form, unit: e.target.value })}
          />
          <Input
            label="Start date"
            type="date"
            required
            value={form.start_date}
            onChange={(e) => setForm({ ...form, start_date: e.target.value })}
          />
          <Input
            label="Target date"
            type="date"
            required
            value={form.target_date}
            onChange={(e) => setForm({ ...form, target_date: e.target.value })}
          />
          <div className="form-actions">
            <Button type="submit" loading={saving}>
              Create goal
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