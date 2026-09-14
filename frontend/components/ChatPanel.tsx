"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

const SUGGESTIONS = [
  "What will move Gold today?",
  "What happens if CPI is lower than expected?",
  "Why is Bitcoin falling?",
  "What are the biggest risks for stocks this week?",
  "Give me the highest-probability Gold setup.",
];

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send(query: string) {
    if (!query.trim() || loading) return;
    setError(null);
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chat(query);
      setMessages((prev) => [...prev, { role: "assistant", text: res.answer }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reach the AI assistant.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel" style={{ display: "flex", flexDirection: "column", gap: 16, minHeight: 480 }}>
      <div>
        <h2 style={{ fontSize: 18 }}>Ask the Market Intelligence AI</h2>
        <p className="text-dim text-sm">
          Answers are grounded in the live world state, intelligence scores, calendar and recent headlines —
          not general knowledge alone.
        </p>
      </div>

      {messages.length === 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {SUGGESTIONS.map((s) => (
            <button key={s} className="tag" style={{ cursor: "pointer" }} onClick={() => send(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 12, flex: 1 }}>
        {messages.map((m, i) => (
          <div
            key={i}
            className="panel"
            style={{
              background: m.role === "user" ? "var(--bg-panel-alt)" : "var(--bg)",
              whiteSpace: "pre-wrap",
              fontSize: 14,
            }}
          >
            <div className="text-dim text-sm" style={{ marginBottom: 6, fontWeight: 600 }}>
              {m.role === "user" ? "You" : "WealthAI"}
            </div>
            {m.text}
          </div>
        ))}
        {loading && <div className="text-dim text-sm">Thinking…</div>}
        {error && <div style={{ color: "var(--bearish)" }}>{error}</div>}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        style={{ display: "flex", gap: 10 }}
      >
        <input
          className="input"
          style={{ flex: 1 }}
          placeholder="Ask about Gold, USD, stocks, crypto, or an upcoming event…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="btn" type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
