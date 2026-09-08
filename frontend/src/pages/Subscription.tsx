import { useEffect, useState } from "react";
import {
  apiClient,
  type PaymentRecord,
  type SubscriptionStatus,
} from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Stat from "../components/ui/Stat";
import ErrorBox from "../components/ui/ErrorBox";
import Spinner from "../components/ui/Spinner";

export default function Subscription() {
  const [status, setStatus] = useState<SubscriptionStatus | null>(null);
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const [s, p] = await Promise.all([
        apiClient.getSubscriptionStatus(),
        apiClient.getPaymentHistory(),
      ]);
      setStatus(s);
      setPayments(p.payments);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load subscription.");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpgrade() {
    setError(null);
    try {
      const order = await apiClient.createPaymentOrder(49900);
      // In demo mode the order returns a demo id; simulate a successful verify.
      if (order.provider === "demo") {
        const demoSignature = `${order.order_id}|demo|fakesig`;
        await apiClient.verifyDemoPayment(order.order_id, demoSignature);
        await load();
        return;
      }
      window.alert(
        `Order created: ${order.order_id}. Complete the payment provider checkout flow to finish.`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create order.");
    }
  }

  return (
    <main className="page-shell">
      <PageHeader
        eyebrow="Account"
        title="Subscription"
        subtitle="FREE and PREMIUM plans. Payment secrets stay on the server."
      />

      {error ? <ErrorBox message={error} /> : null}

      {loading ? (
        <Spinner label="Loading subscription…" />
      ) : status ? (
        <>
          <div className="stat-grid">
            <Stat label="Plan" value={status.plan} accent={status.plan === "PREMIUM"} />
            <Stat label="Status" value={status.status} />
            <Stat
              label="Expires"
              value={status.expires_at ? status.expires_at.slice(0, 10) : "—"}
            />
          </div>

          <Card
            title={status.plan === "PREMIUM" ? "You're on PREMIUM" : "Upgrade to PREMIUM"}
            subtitle={
              status.plan === "PREMIUM"
                ? "Premium features are active."
                : "Unlock AI insights, reports, advanced analytics and more."
            }
            actions={
              status.plan !== "PREMIUM" ? (
                <Button onClick={handleUpgrade}>Upgrade · ₹499</Button>
              ) : null
            }
          >
            <ul className="feature-list">
              <li>AI insights</li>
              <li>AI wellness reports</li>
              <li>Advanced analytics</li>
              <li>Wearable sync</li>
            </ul>
          </Card>

          <Card title="Payment history">
            {payments.length === 0 ? (
              <p className="muted">No payments recorded.</p>
            ) : (
              <div className="metric-table">
                <div className="metric-table-head">
                  <span>Amount</span>
                  <span>Status</span>
                  <span>Provider</span>
                  <span>Date</span>
                </div>
                {payments.map((p) => (
                  <div className="metric-table-row" key={p.id}>
                    <strong>
                      {p.currency} {p.amount}
                    </strong>
                    <span>{p.status}</span>
                    <span className="muted">{p.provider ?? "—"}</span>
                    <span className="muted">{p.created_at.slice(0, 10)}</span>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      ) : (
        <Spinner label="No subscription status" />
      )}
    </main>
  );
}