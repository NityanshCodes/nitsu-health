import { useEffect, useState } from "react";
import {
  apiClient,
  type HealthMetricResponse,
  type HealthMetricCreatePayload,
} from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Modal from "../components/ui/Modal";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

const METRIC_TYPES = [
  { value: "weight", label: "Weight (kg)" },
  { value: "blood_pressure_systolic", label: "Blood pressure - systolic" },
  { value: "blood_pressure_diastolic", label: "Blood pressure - diastolic" },
  { value: "heart_rate", label: "Heart rate (bpm)" },
  { value: "blood_glucose", label: "Blood glucose (mg/dL)" },
  { value: "bmi", label: "BMI" },
  { value: "waist_circumference", label: "Waist circumference (cm)" },
];

function unitFor(type: string): string {
  const map: Record<string, string> = {
    weight: "kg",
    heart_rate: "bpm",
    blood_glucose: "mg/dL",
    bmi: "",
    waist_circumference: "cm",
  };
  return map[type] ?? "";
}

export default function Health() {
  const [metrics, setMetrics] = useState<HealthMetricResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    metric_type: "weight",
    value: 0,
  });

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const result = await apiClient.getHealthMetrics();
      setMetrics(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load metrics.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload: HealthMetricCreatePayload = {
        metric_type: form.metric_type,
        value: form.value,
        unit: unitFor(form.metric_type),
      };
      await apiClient.createHealthMetric(payload);
      setModalOpen(false);
      setForm({ metric_type: "weight", value: 0 });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save metric.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this metric?")) return;
    try {
      await apiClient.deleteHealthMetric(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete metric.");
    }
  }

  return (
    <main className="page-shell">
      <PageHeader
        eyebrow="Health"
        title="Health metrics"
        subtitle="Track measurements over time. Consistent tracking reveals trends."
        actions={
          <Button onClick={() => setModalOpen(true)}>Add metric</Button>
        }
      />

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading metrics…" />
      ) : metrics.length === 0 ? (
        <EmptyState
          title="No metrics recorded"
          message="Add your first health metric to start a longitudinal record."
        />
      ) : (
        <div className="metric-table">
          <div className="metric-table-head">
            <span>Metric</span>
            <span>Value</span>
            <span>Recorded</span>
            <span>Source</span>
            <span />
          </div>
          {metrics.map((m) => (
            <div className="metric-table-row" key={m.id}>
              <span>{m.metric_type}</span>
              <strong>
                {m.value} {m.unit}
              </strong>
              <span className="muted">{m.recorded_at.slice(0, 10)}</span>
              <span className="muted">{m.source}</span>
              <span>
                <button
                  type="button"
                  className="button button-ghost button-sm"
                  onClick={() => handleDelete(m.id)}
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
        title="Add health metric"
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={handleSubmit} className="modal-form">
          <Select
            label="Metric type"
            options={METRIC_TYPES}
            value={form.metric_type}
            onChange={(e) => setForm({ ...form, metric_type: e.target.value })}
          />
          <Input
            label={`Value (${unitFor(form.metric_type) || "unit"})`}
            type="number"
            step="any"
            required
            value={form.value}
            onChange={(e) => setForm({ ...form, value: Number(e.target.value) })}
          />
          <div className="form-actions">
            <Button type="submit" loading={saving}>
              Save metric
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