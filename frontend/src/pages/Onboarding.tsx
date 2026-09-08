import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import ErrorBox from "../components/ui/ErrorBox";
import { apiClient } from "../services/api";

/** Lightweight onboarding: health profile basics. Skippable. */
export default function Onboarding() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    height_cm: 0,
    weight_kg: 0,
    blood_type: "",
    medical_conditions: "",
    lifestyle: "",
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await apiClient.updateProfileHealth({
        height_cm: form.height_cm || null,
        weight_kg: form.weight_kg || null,
        blood_type: form.blood_type || null,
        medical_conditions: form.medical_conditions || null,
        lifestyle: form.lifestyle || null,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="page-shell" style={{ maxWidth: "640px", margin: "0 auto" }}>
      <div className="page-header">
        <div>
          <p className="eyebrow">Almost there</p>
          <h2>Tell us a bit about yourself</h2>
          <p className="muted">
            This helps personalize your experience. You can change it anytime or
            skip for now.
          </p>
        </div>
      </div>

      {error ? <ErrorBox message={error} /> : null}

      <form onSubmit={handleSubmit} className="panel form">
        <Input
          label="Height (cm)"
          type="number"
          step="any"
          value={form.height_cm || ""}
          onChange={(e) => setForm({ ...form, height_cm: Number(e.target.value) })}
        />
        <Input
          label="Weight (kg)"
          type="number"
          step="any"
          value={form.weight_kg || ""}
          onChange={(e) => setForm({ ...form, weight_kg: Number(e.target.value) })}
        />
        <Input
          label="Blood type"
          placeholder="e.g. O+"
          value={form.blood_type}
          onChange={(e) => setForm({ ...form, blood_type: e.target.value })}
        />
        <Input
          label="Medical conditions"
          placeholder="Comma-separated conditions, if any"
          value={form.medical_conditions}
          onChange={(e) =>
            setForm({ ...form, medical_conditions: e.target.value })
          }
        />
        <Input
          label="Lifestyle"
          placeholder="Activity, diet, sleep habits"
          value={form.lifestyle}
          onChange={(e) => setForm({ ...form, lifestyle: e.target.value })}
        />

        <div className="form-actions">
          <Button type="submit" loading={saving}>
            Save and continue
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate("/dashboard")}
          >
            Skip for now
          </Button>
        </div>
      </form>
    </main>
  );
}