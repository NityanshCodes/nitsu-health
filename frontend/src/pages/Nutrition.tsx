import { useEffect, useState } from "react";
import { apiClient, type NutritionTodayResponse } from "../services/api";

export default function Nutrition() {
  const [data, setData] = useState<NutritionTodayResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    meal_type: "lunch",
    calories: 600,
    protein_g: 25,
    carbs_g: 75,
    fats_g: 20,
    water_ml: 500,
    notes: "",
  });

  useEffect(() => {
    const loadNutrition = async () => {
      try {
        const result = await apiClient.getNutritionToday();
        setData(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Nutrition information is currently unavailable.",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadNutrition();
  }, []);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await apiClient.createNutritionEntry({
        meal_type: formData.meal_type,
        calories: formData.calories,
        protein_g: formData.protein_g,
        carbs_g: formData.carbs_g,
        fats_g: formData.fats_g,
        water_ml: formData.water_ml,
        notes: formData.notes || null,
      });

      const result = await apiClient.getNutritionToday();
      setData(result);
      setShowForm(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to save nutrition entry",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="panel">
        <div
          className="form-actions"
          style={{ justifyContent: "space-between", alignItems: "center" }}
        >
          <div>
            <p className="eyebrow">Nutrition</p>
            <h2>Today's nutrition</h2>
          </div>
          {!showForm && (
            <button
              type="button"
              className="card-button"
              onClick={() => setShowForm(true)}
            >
              Add Entry
            </button>
          )}
        </div>

        {error ? <div className="error-box">{error}</div> : null}

        {showForm ? (
          <form
            onSubmit={handleSubmit}
            className="form"
            style={{ marginTop: "1.5rem" }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "1rem",
              }}
            >
              <div>
                <label htmlFor="meal_type" className="form-label">
                  Meal Type
                </label>
                <select
                  id="meal_type"
                  name="meal_type"
                  value={formData.meal_type}
                  onChange={handleInputChange}
                  required
                >
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                </select>
              </div>

              <div>
                <label htmlFor="calories" className="form-label">
                  Calories
                </label>
                <input
                  id="calories"
                  type="number"
                  name="calories"
                  min="0"
                  max="10000"
                  value={formData.calories}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div>
                <label htmlFor="protein_g" className="form-label">
                  Protein (g)
                </label>
                <input
                  id="protein_g"
                  type="number"
                  name="protein_g"
                  min="0"
                  step="0.1"
                  value={formData.protein_g}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div>
                <label htmlFor="carbs_g" className="form-label">
                  Carbs (g)
                </label>
                <input
                  id="carbs_g"
                  type="number"
                  name="carbs_g"
                  min="0"
                  step="0.1"
                  value={formData.carbs_g}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div>
                <label htmlFor="fats_g" className="form-label">
                  Fats (g)
                </label>
                <input
                  id="fats_g"
                  type="number"
                  name="fats_g"
                  min="0"
                  step="0.1"
                  value={formData.fats_g}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div>
                <label htmlFor="water_ml" className="form-label">
                  Water (ml)
                </label>
                <input
                  id="water_ml"
                  type="number"
                  name="water_ml"
                  min="0"
                  max="20000"
                  value={formData.water_ml}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div style={{ gridColumn: "1 / -1" }}>
                <label htmlFor="notes" className="form-label">
                  Notes (optional)
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  placeholder="Any notes about this meal..."
                  rows={3}
                />
              </div>
            </div>

            <div
              className="form-actions"
              style={{ marginTop: "1.5rem", gap: "1rem" }}
            >
              <button
                type="submit"
                className="card-button"
                disabled={submitting}
              >
                {submitting ? "Saving..." : "Save Entry"}
              </button>
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowForm(false)}
                disabled={submitting}
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div style={{ marginTop: "1.5rem" }}>
            {loading ? (
              <p className="muted">Loading nutrition data…</p>
            ) : data ? (
              <div className="stat-grid">
                <div className="stat">
                  <span className="muted">Calories</span>
                  <strong>{data.calories}</strong>
                </div>
                <div className="stat">
                  <span className="muted">Water</span>
                  <strong>{data.water_ml} ml</strong>
                </div>
                <div className="stat" style={{ gridColumn: "1 / -1" }}>
                  <span className="muted">Recommendation</span>
                  <strong style={{ fontSize: "1.1rem" }}>
                    {data.recommendation}
                  </strong>
                </div>
              </div>
            ) : (
              <p className="muted">No nutrition data is available yet.</p>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
