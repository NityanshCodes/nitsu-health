import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiClient, type DashboardSummaryResponse } from "../services/api";
import Card from "../components/ui/Card";
import Stat from "../components/ui/Stat";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const result = await apiClient.getDashboard();
        setData(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Dashboard data is unavailable right now.",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadDashboard();
  }, []);

  return (
    <main className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Welcome</p>
          <h2>Your health overview</h2>
          <p className="muted">
            {user
              ? `Hello, ${user.first_name || user.username}`
              : "Sign in to see your overview"}
          </p>
        </div>
      </div>

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading your dashboard…" />
      ) : data ? (
        <>
          <div className="stat-grid">
            <Stat
              label="Calories today"
              value={`${data.nutrition_today.calories} kcal`}
              hint={`${data.nutrition_today.entries} entries`}
              accent
            />
            <Stat
              label="Steps today"
              value={data.activity_today.total_steps.toLocaleString()}
              hint={`${data.activity_today.total_active_minutes} active minutes`}
            />
            <Stat
              label="Sleep"
              value={
                data.sleep.last_entry?.duration_minutes
                  ? `${Math.round(data.sleep.last_entry.duration_minutes / 60)}h`
                  : "No entry"
              }
              hint="Last recorded night"
            />
            <Stat
              label="Notifications"
              value={data.unread_notifications}
              hint="Unread"
            />
          </div>

          <div className="dashboard-grid" style={{ marginTop: "1rem" }}>
            <Card title="Active goals" subtitle="Track progress towards your targets">
              {data.active_goals.length === 0 ? (
                <EmptyState
                  title="No active goals"
                  message="Create a goal to start tracking progress."
                />
              ) : (
                <ul className="goal-list">
                  {data.active_goals.map((g) => (
                    <li key={g.id} className="goal-item">
                      <div className="goal-row">
                        <span>{g.title}</span>
                        <span className="muted">
                          {g.progress_value}/{g.target_value} {g.unit}
                        </span>
                      </div>
                      <div className="progress-track">
                        <div
                          className="progress-fill"
                          style={{ width: `${g.progress_pct}%` }}
                        />
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card title="Latest metrics" subtitle="Most recent measurements">
              {data.latest_metrics.length === 0 ? (
                <EmptyState
                  title="No metrics yet"
                  message="Add a health metric to begin tracking."
                />
              ) : (
                <ul className="metric-list">
                  {data.latest_metrics.map((m, i) => (
                    <li key={i} className="metric-item">
                      <span>{m.metric_type}</span>
                      <strong>
                        {m.value} {m.unit}
                      </strong>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card title="Recent reports">
              {data.recent_reports.length === 0 ? (
                <EmptyState
                  title="No reports yet"
                  message="Generate your first wellness report."
                />
              ) : (
                <ul className="report-list">
                  {data.recent_reports.map((r) => (
                    <li key={r.id}>
                      <span>{r.title}</span>
                      <span className="muted">{r.created_at.slice(0, 10)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </>
      ) : (
        <EmptyState title="No dashboard data" message="Your overview will appear here." />
      )}
    </main>
  );
}