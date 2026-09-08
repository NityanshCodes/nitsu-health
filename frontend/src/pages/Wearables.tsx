import { useEffect, useState } from "react";
import { apiClient, type WearableStatusResponse } from "../services/api";
import Card from "../components/ui/Card";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

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
          err instanceof Error ? err.message : "Wearable status is unavailable.",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadWearables();
  }, []);

  async function handleConnect() {
    try {
      const { auth_url } = await apiClient.getWearableConnectUrl();
      window.location.href = auth_url;
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to start Fitbit connection.",
      );
    }
  }

  return (
    <main className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Wearables</p>
          <h2>Integration status</h2>
          <p className="muted">Connect Fitbit to sync your activity and sleep.</p>
        </div>
      </div>

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Checking wearable connections…" />
      ) : data ? (
        <Card
          title="Fitbit"
          subtitle={
            data.configured
              ? "Configuration detected"
              : data.config_note ?? "Not configured"
          }
          actions={
            <button type="button" className="card-button" onClick={handleConnect}>
              Connect
            </button>
          }
        >
          {data.connections.length === 0 ? (
            <EmptyState
              title="No connections yet"
              message="Connect a Fitbit account to start syncing data."
            />
          ) : (
            <ul className="metric-list">
              {data.connections.map((c) => (
                <li key={c.provider} className="metric-item">
                  <span>{c.provider}</span>
                  <strong className="muted">
                    {c.status}
                    {c.last_synced_at
                      ? ` · last synced ${c.last_synced_at.slice(0, 10)}`
                      : ""}
                  </strong>
                </li>
              ))}
            </ul>
          )}
          {!data.configured && (
            <p className="warning-box">
              Fitbit credentials are not configured on the server. Set
              FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET to enable real syncing.
            </p>
          )}
        </Card>
      ) : (
        <EmptyState title="No wearable status" />
      )}
    </main>
  );
}