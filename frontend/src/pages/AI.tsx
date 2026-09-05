import { useEffect, useRef, useState } from "react";
import {
  apiClient,
  type AIChatResponse,
  type AIHealthResponse,
} from "../services/api";

interface Message {
  id: string;
  type: "user" | "ai";
  content: string;
  disclaimer?: string;
  contextUsed?: boolean;
  timestamp: Date;
}

export default function AI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiHealth, setAiHealth] = useState<AIHealthResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check AI health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await apiClient.getAIHealth();
        setAiHealth(health);
      } catch (err) {
        console.error("Failed to check AI health:", err);
      }
    };
    checkHealth();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) {
      return;
    }

    if (!aiHealth?.configured && aiHealth?.provider !== "DevelopmentProvider") {
      setError("AI service is not available");
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const response: AIChatResponse = await apiClient.sendAIQuestion(
        input,
        true,
      );

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: response.answer,
        disclaimer: response.disclaimer,
        contextUsed:
          response.context_used !== null && response.context_used !== undefined,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to get response from AI";
      setError(errorMessage);
      // Add error message to chat
      const errorMessage_obj: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage_obj]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        maxWidth: "800px",
        margin: "0 auto",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "1.5rem",
          borderBottom: "1px solid #e5e7eb",
          backgroundColor: "#f9fafb",
        }}
      >
        <h1
          style={{
            margin: "0 0 0.5rem 0",
            fontSize: "1.875rem",
            fontWeight: "bold",
          }}
        >
          Nitsu AI Assistant
        </h1>
        <p style={{ margin: "0", color: "#6b7280", fontSize: "0.875rem" }}>
          Your personal health information assistant
        </p>
        {aiHealth && (
          <p
            style={{
              margin: "0.5rem 0 0 0",
              fontSize: "0.75rem",
              color: "#9ca3af",
            }}
          >
            Provider: {aiHealth.provider}
            {aiHealth.provider === "DevelopmentProvider" &&
              " (Development Mode)"}
          </p>
        )}
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflow: "auto",
          padding: "1.5rem",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              textAlign: "center",
              color: "#9ca3af",
              paddingTop: "2rem",
            }}
          >
            <p>Ask Nitsu something about your health</p>
            <p style={{ fontSize: "0.875rem", marginTop: "1rem" }}>
              Examples: "What's a healthy sleep schedule?", "How should I
              exercise?"
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            <div
              style={{
                display: "flex",
                justifyContent: msg.type === "user" ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  maxWidth: "70%",
                  padding: "0.75rem 1rem",
                  borderRadius: "0.5rem",
                  backgroundColor: msg.type === "user" ? "#3b82f6" : "#f3f4f6",
                  color: msg.type === "user" ? "white" : "black",
                }}
              >
                <p style={{ margin: "0", wordWrap: "break-word" }}>
                  {msg.content}
                </p>
              </div>
            </div>

            {msg.type === "ai" && msg.disclaimer && (
              <div
                style={{
                  marginTop: "0.5rem",
                  marginLeft: "0",
                  fontSize: "0.75rem",
                  color: "#6b7280",
                  fontStyle: "italic",
                }}
              >
                {msg.contextUsed && (
                  <p style={{ margin: "0.25rem 0" }}>
                    📊 Based on your Nitsu Health data
                  </p>
                )}
                <p style={{ margin: "0.25rem 0" }}>⚠️ {msg.disclaimer}</p>
              </div>
            )}
          </div>
        ))}

        {error && (
          <div
            style={{
              padding: "0.75rem 1rem",
              backgroundColor: "#fee2e2",
              color: "#991b1b",
              borderRadius: "0.5rem",
              fontSize: "0.875rem",
            }}
          >
            <p style={{ margin: 0 }}>Error: {error}</p>
          </div>
        )}

        {loading && (
          <div style={{ display: "flex", gap: "0.5rem", padding: "1rem" }}>
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                backgroundColor: "#9ca3af",
                animation: "pulse 1.5s ease-in-out infinite",
              }}
            />
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                backgroundColor: "#9ca3af",
                animation: "pulse 1.5s ease-in-out infinite 0.3s",
              }}
            />
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                backgroundColor: "#9ca3af",
                animation: "pulse 1.5s ease-in-out infinite 0.6s",
              }}
            />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSendMessage}
        style={{
          padding: "1.5rem",
          borderTop: "1px solid #e5e7eb",
          display: "flex",
          gap: "0.75rem",
          backgroundColor: "#f9fafb",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Nitsu something..."
          disabled={loading || !aiHealth}
          style={{
            flex: 1,
            padding: "0.75rem 1rem",
            border: "1px solid #d1d5db",
            borderRadius: "0.5rem",
            fontSize: "1rem",
            fontFamily: "inherit",
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim() || !aiHealth}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: loading || !input.trim() ? "#d1d5db" : "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: "0.5rem",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            fontSize: "1rem",
            fontWeight: "500",
            transition: "background-color 0.2s",
          }}
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
