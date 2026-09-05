import { useEffect, useState } from "react";
import { apiClient, type WearableStatusResponse } from "../services/api";

export default function Wearables() {
  const [data, setData] = useState<WearableStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadWearables = async () => {
      try {
        const result = await apiClient.getWearableStatus();
        setData(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Wearable status is unavailable.",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadWearables();
  }, []);

  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">Wearables</p>
        <h2>Integration status</h2>
        {error ? <div className="error-box">{error}</div> : null}

        {loading ? (
          <p className="muted">Checking wearable connections…</p>
        ) : data ? (
          <div className="info-grid">
            <div>
              <p className="muted">Status</p>
              <p>{data.status}</p>
            </div>
            <div>
              <p className="muted">Provider</p>
              <p>{data.provider}</p>
            </div>
            <div style={{ gridColumn: "1 / -1" }}>
              <p className="muted">Message</p>
              <p>{data.message}</p>
            </div>
          </div>
        ) : (
          <div className="warning-box">Integration not connected.</div>
        )}
      </section>
    </main>
  );
}
