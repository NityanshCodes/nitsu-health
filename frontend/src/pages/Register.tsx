import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    first_name: "",
    last_name: "",
  });
  const [localError, setLocalError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLocalError("");
    setSuccess("");

    if (!form.email || !form.username || !form.password) {
      setLocalError("Email, username, and password are required.");
      return;
    }

    try {
      await register({
        email: form.email,
        username: form.username,
        password: form.password,
        first_name: form.first_name || undefined,
        last_name: form.last_name || undefined,
      });

      setForm({
        email: "",
        username: "",
        password: "",
        first_name: "",
        last_name: "",
      });
      setSuccess("Registration was successful. You can now sign in.");
      setTimeout(() => navigate("/login"), 500);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Registration failed. Please try again.";
      setLocalError(message);
    }
  };

  const displayError = error || localError;

  return (
    <main className="page-shell">
      <section className="auth-card">
        <p className="eyebrow">Create account</p>
        <h2>Join Nitsu Health</h2>

        <form className="form-grid" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={form.email}
              onChange={(event) =>
                setForm({ ...form, email: event.target.value })
              }
              placeholder="you@example.com"
              disabled={loading}
            />
          </div>

          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={form.username}
              onChange={(event) =>
                setForm({ ...form, username: event.target.value })
              }
              placeholder="janehealth"
              disabled={loading}
            />
          </div>

          <div className="field">
            <label htmlFor="first_name">First name (optional)</label>
            <input
              id="first_name"
              type="text"
              value={form.first_name}
              onChange={(event) =>
                setForm({ ...form, first_name: event.target.value })
              }
              placeholder="Jane"
              disabled={loading}
            />
          </div>

          <div className="field">
            <label htmlFor="last_name">Last name (optional)</label>
            <input
              id="last_name"
              type="text"
              value={form.last_name}
              onChange={(event) =>
                setForm({ ...form, last_name: event.target.value })
              }
              placeholder="Doe"
              disabled={loading}
            />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={(event) =>
                setForm({ ...form, password: event.target.value })
              }
              placeholder="At least 8 characters"
              disabled={loading}
            />
          </div>

          {displayError ? (
            <div className="error-box">{displayError}</div>
          ) : null}
          {success ? <div className="success-box">{success}</div> : null}

          <div className="form-actions">
            <button type="submit" className="primary-button" disabled={loading}>
              {loading ? "Creating account…" : "Create account"}
            </button>
          </div>
        </form>

        <p style={{ marginTop: "1rem" }} className="muted">
          Already have an account?{" "}
          <Link to="/login" className="text-link">
            Sign in
          </Link>
        </p>
      </section>
    </main>
  );
}
