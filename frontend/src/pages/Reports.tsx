import { useEffect, useState } from "react";
import { apiClient, type ReportListItem } from "../services/api";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

export default function Reports() {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadReports();
  }, []);

  async function loadReports() {
    try {
      const result = await apiClient.getReports();
      setReports(result.items);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Reports are temporarily unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    setError(null);
    try {
      await apiClient.generateReport();
      await loadReports();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate report.",
      );
    } finally {
      setGenerating(false);
    }
  }

  return (
    <main className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Reports</p>
          <h2>Wellness reports</h2>
          <p className="muted">
            Reports summarize your recorded data over the past 30 days. They are
            observations, not medical diagnoses.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={handleGenerate}
          loading={generating}
        >
          Generate report
        </Button>
      </div>

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading reports…" />
      ) : reports.length === 0 ? (
        <EmptyState
          title="No reports yet"
          message="Generate your first wellness report from your recorded data."
        />
      ) : (
        <div className="report-grid">
          {reports.map((r) => (
            <Card key={r.id} title={r.title} subtitle={`${r.report_type} · ${r.created_at.slice(0, 10)}`}>
              <p>{r.summary}</p>
              <p className="muted" style={{ marginTop: "0.5rem" }}>
                Status: {r.status}
              </p>
            </Card>
          ))}
        </div>
      )}
    </main>
  );
}