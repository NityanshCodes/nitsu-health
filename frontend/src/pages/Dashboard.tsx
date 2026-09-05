import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiClient, type DashboardSummaryResponse } from "../services/api";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] =
    useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const data = await apiClient.getDashboard();
        setDashboardData(data);
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

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <main className="page-shell">
      <section className="panel">
        <div
          className="form-actions"
          style={{ justifyContent: "space-between", alignItems: "center" }}
        >
          <div>
            <p className="eyebrow">Welcome</p>
            <h2>
              {user
                ? `Hello, ${user.first_name || user.username}`
                : "Your health overview"}
            </h2>
          </div>
          <button
            type="button"
            className="secondary-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </section>

      {error ? (
        <div className="error-box" style={{ marginTop: "1rem" }}>
          {error}
        </div>
      ) : null}

      <div className="stat-grid" style={{ marginTop: "1rem" }}>
        <div className="stat">
          <span className="muted">Status</span>
          <strong>{dashboardData?.status ?? "Loading"}</strong>
        </div>
        <div className="stat">
          <span className="muted">Profile</span>
          <strong>{user?.role ?? "User"}</strong>
        </div>
        <div className="stat">
          <span className="muted">AI</span>
          <strong>Ready</strong>
        </div>
        <div className="stat">
          <span className="muted">Account</span>
          <strong>{user?.email ? "Active" : "Guest"}</strong>
        </div>
      </div>

      <div className="dashboard-grid" style={{ marginTop: "1rem" }}>
        <div className="card">
          <h2>Health overview</h2>
          {loading ? (
            <p className="muted">Loading dashboard summary…</p>
          ) : dashboardData ? (
            <div className="info-grid">
              <div>
                <p className="muted">Summary</p>
                <p>{dashboardData.summary}</p>
              </div>
              <div>
                <p className="muted">Insights</p>
                <ul>
                  {dashboardData.insights.map((insight) => (
                    <li key={insight}>{insight}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <p className="muted">No dashboard summary is available.</p>
          )}
        </div>

        <div className="card">
          <h2>Quick access</h2>
          <div
            className="form-actions"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            }}
          >
            <button
              type="button"
              className="card-button"
              onClick={() => navigate("/ai")}
            >
              AI Assistant
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => navigate("/nutrition")}
            >
              Nutrition
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => navigate("/wearables")}
            >
              Wearables
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => navigate("/reports")}
            >
              Reports
            </button>
          </div>
        </div>

        <div className="card">
          <h2>Profile</h2>
          {user ? (
            <div className="info-grid">
              <div>
                <p className="muted">Email</p>
                <p>{user.email}</p>
              </div>
              <div>
                <p className="muted">Username</p>
                <p>{user.username}</p>
              </div>
              <div>
                <p className="muted">Role</p>
                <p>{user.role}</p>
              </div>
              <div>
                <p className="muted">Name</p>
                <p>
                  {user.first_name || user.last_name
                    ? `${user.first_name ?? ""} ${user.last_name ?? ""}`.trim()
                    : "Not provided"}
                </p>
              </div>
            </div>
          ) : (
            <p className="muted">Profile information is unavailable.</p>
          )}
        </div>
      </div>
    </main>
  );
}
