import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiClient } from "../services/api";

export default function Profile() {
  const { user, setUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    phone: "",
    country: "",
    timezone: "",
  });

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        phone: user.phone || "",
        country: user.country || "",
        timezone: user.timezone || "",
      });
    }
  }, [user]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const updatedUser = await apiClient.updateProfile({
        first_name: formData.first_name || null,
        last_name: formData.last_name || null,
        phone: formData.phone || null,
        country: formData.country || null,
        timezone: formData.timezone || null,
      });

      setUser(updatedUser);
      setIsEditing(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to update profile",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="panel">
        <div
          className="form-actions"
          style={{ justifyContent: "space-between", alignItems: "center" }}
        >
          <div>
            <p className="eyebrow">Profile</p>
            <h2>Account details</h2>
          </div>
          {!isEditing && (
            <button
              type="button"
              className="card-button"
              onClick={() => setIsEditing(true)}
            >
              Edit Profile
            </button>
          )}
        </div>

        {error ? <div className="error-box">{error}</div> : null}

        {isEditing ? (
          <form onSubmit={handleSubmit} className="form" style={{ marginTop: "1.5rem" }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "1rem",
              }}
            >
              <div>
                <label htmlFor="first_name" className="form-label">
                  First Name
                </label>
                <input
                  id="first_name"
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  placeholder="Enter first name"
                />
              </div>

              <div>
                <label htmlFor="last_name" className="form-label">
                  Last Name
                </label>
                <input
                  id="last_name"
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  placeholder="Enter last name"
                />
              </div>

              <div>
                <label htmlFor="phone" className="form-label">
                  Phone
                </label>
                <input
                  id="phone"
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="Enter phone number"
                />
              </div>

              <div>
                <label htmlFor="country" className="form-label">
                  Country
                </label>
                <input
                  id="country"
                  type="text"
                  name="country"
                  value={formData.country}
                  onChange={handleInputChange}
                  placeholder="Enter country"
                />
              </div>

              <div>
                <label htmlFor="timezone" className="form-label">
                  Timezone
                </label>
                <select
                  id="timezone"
                  name="timezone"
                  value={formData.timezone}
                  onChange={handleInputChange}
                >
                  <option value="">Select timezone</option>
                  <option value="UTC">UTC</option>
                  <option value="EST">EST (UTC-5)</option>
                  <option value="CST">CST (UTC-6)</option>
                  <option value="MST">MST (UTC-7)</option>
                  <option value="PST">PST (UTC-8)</option>
                  <option value="GMT">GMT (UTC+0)</option>
                  <option value="IST">IST (UTC+5:30)</option>
                  <option value="JST">JST (UTC+9)</option>
                  <option value="AEST">AEST (UTC+10)</option>
                </select>
              </div>
            </div>

            <div
              className="form-actions"
              style={{ marginTop: "1.5rem", gap: "1rem" }}
            >
              <button
                type="submit"
                className="card-button"
                disabled={submitting}
              >
                {submitting ? "Saving..." : "Save Changes"}
              </button>
              <button
                type="button"
                className="secondary-button"
                onClick={() => setIsEditing(false)}
                disabled={submitting}
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div style={{ marginTop: "1.5rem" }}>
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
                {user.phone && (
                  <div>
                    <p className="muted">Phone</p>
                    <p>{user.phone}</p>
                  </div>
                )}
                {user.country && (
                  <div>
                    <p className="muted">Country</p>
                    <p>{user.country}</p>
                  </div>
                )}
                {user.timezone && (
                  <div>
                    <p className="muted">Timezone</p>
                    <p>{user.timezone}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="warning-box">You are not signed in.</div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
