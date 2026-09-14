import { useEffect, useState } from "react";
import {
  apiClient,
  type InsightResponse,
} from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

export default function Insights() {
  const [items, setItems] = useState<InsightResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const result = await apiClient.getInsights();
      setItems(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load insights.");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    setError(null);
    try {
      await apiClient.generateInsights();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate insights.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <main className="page-shell">
      <PageHeader
        eyebrow="AI"
        title="Insights"
        subtitle="Observations derived from your recorded data — not medical diagnoses."
        actions={
          <Button onClick={handleGenerate} loading={generating}>
            Generate insights
          </Button>
        }
      />

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading insights…" />
      ) : items.length === 0 ? (
        <EmptyState
          title="No insights yet"
          message="Generate insights from your recorded data to see observations and trends."
        />
      ) : (
        <div className="goal-grid">
          {items.map((insight) => (
            <Card
              key={insight.id}
              title={insight.title}
              subtitle={insight.type}
            >
              <p>{insight.body}</p>
              {insight.confidence != null && (
                <p className="muted" style={{ marginTop: "0.5rem" }}>
                  Confidence: {Math.round(insight.confidence * 100)}%
                </p>
              )}
              {insight.next_step && (
                <p className="muted" style={{ marginTop: "0.5rem" }}>
                  Next step: {insight.next_step}
                </p>
              )}
            </Card>
          ))}
        </div>
      )}
    </main>
  );
}