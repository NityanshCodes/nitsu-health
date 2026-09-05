import { useEffect, useState } from "react";
import { apiClient, type LatestReportResponse } from "../services/api";

export default function Reports() {
  const [data, setData] = useState<LatestReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadReports = async () => {
      try {
        const result = await apiClient.getLatestReport();
        setData(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Reports are temporarily unavailable.",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadReports();
  }, []);

  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">Reports</p>
        <h2>Latest report</h2>
        {error ? <div className="error-box">{error}</div> : null}

        {loading ? (
          <p className="muted">Loading report…</p>
        ) : data ? (
          <div className="info-grid">
            <div>
              <p className="muted">Title</p>
              <p>{data.title}</p>
            </div>
            <div>
              <p className="muted">Status</p>
              <p>{data.status}</p>
            </div>
            <div style={{ gridColumn: "1 / -1" }}>
              <p className="muted">Summary</p>
              <p>{data.summary}</p>
            </div>
          </div>
        ) : (
          <div className="warning-box">No report available yet.</div>
        )}
      </section>
    </main>
  );
}
