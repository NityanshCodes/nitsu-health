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
import AIPage from "./pages/AI";
import DashboardPage from "./pages/Dashboard";
import LoginPage from "./pages/Login";
import NutritionPage from "./pages/Nutrition";
import ProfilePage from "./pages/Profile";
import RegisterPage from "./pages/Register";
import ReportsPage from "./pages/Reports";
import WearablesPage from "./pages/Wearables";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/ai", label: "AI Assistant" },
  { to: "/nutrition", label: "Nutrition" },
  { to: "/wearables", label: "Wearables" },
  { to: "/reports", label: "Reports" },
  { to: "/profile", label: "Profile" },
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
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
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
          path="/nutrition"
          element={
            <ProtectedRoute>
              <NutritionPage />
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
          path="/reports"
          element={
            <ProtectedRoute>
              <ReportsPage />
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
