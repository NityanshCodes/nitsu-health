import {
  BrowserRouter,
  NavLink,
  Navigate,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";
import "./App.css";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import ActivityPage from "./pages/Activity";
import AIPage from "./pages/AI";
import AnalyticsPage from "./pages/Analytics";
import DashboardPage from "./pages/Dashboard";
import GoalsPage from "./pages/Goals";
import HealthPage from "./pages/Health";
import InsightsPage from "./pages/Insights";
import LoginPage from "./pages/Login";
import MedicalRecordsPage from "./pages/MedicalRecords";
import NotificationsPage from "./pages/Notifications";
import NutritionPage from "./pages/Nutrition";
import OnboardingPage from "./pages/Onboarding";
import ProfilePage from "./pages/Profile";
import RegisterPage from "./pages/Register";
import ReportsPage from "./pages/Reports";
import SettingsPage from "./pages/Settings";
import SleepPage from "./pages/Sleep";
import SubscriptionPage from "./pages/Subscription";
import WearablesPage from "./pages/Wearables";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/health", label: "Health" },
  { to: "/nutrition", label: "Nutrition" },
  { to: "/activity", label: "Activity" },
  { to: "/sleep", label: "Sleep" },
  { to: "/goals", label: "Goals" },
  { to: "/ai", label: "AI Assistant" },
  { to: "/insights", label: "Insights" },
  { to: "/reports", label: "Reports" },
  { to: "/medical-records", label: "Records" },
  { to: "/notifications", label: "Alerts" },
  { to: "/subscription", label: "Plan" },
  { to: "/settings", label: "Settings" },
];

function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      {user && (
        <header className="topbar">
          <div className="brand-block">
            <span className="brand-mark">N</span>
            <div>
              <p className="eyebrow">NITSU Health</p>
              <h1>Health companion</h1>
            </div>
          </div>

          <nav className="nav" aria-label="Main navigation">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                {item.label}
              </NavLink>
            ))}
            <button
              type="button"
              className="logout-button"
              onClick={handleLogout}
            >
              Logout
            </button>
          </nav>
        </header>
      )}

      <Routes>
        <Route
          path="/login"
          element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />
        <Route
          path="/register"
          element={
            user ? <Navigate to="/dashboard" replace /> : <RegisterPage />
          }
        />

        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <OnboardingPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/health"
          element={
            <ProtectedRoute>
              <HealthPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/nutrition"
          element={
            <ProtectedRoute>
              <NutritionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/activity"
          element={
            <ProtectedRoute>
              <ActivityPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sleep"
          element={
            <ProtectedRoute>
              <SleepPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/goals"
          element={
            <ProtectedRoute>
              <GoalsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai"
          element={
            <ProtectedRoute>
              <AIPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/insights"
          element={
            <ProtectedRoute>
              <InsightsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/medical-records"
          element={
            <ProtectedRoute>
              <MedicalRecordsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/subscription"
          element={
            <ProtectedRoute>
              <SubscriptionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/wearables"
          element={
            <ProtectedRoute>
              <WearablesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/"
          element={<Navigate to={user ? "/dashboard" : "/login"} replace />}
        />
        <Route
          path="*"
          element={<Navigate to={user ? "/dashboard" : "/login"} replace />}
        />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}