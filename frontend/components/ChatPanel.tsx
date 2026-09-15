"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useGame } from "@/lib/game/GameProvider";

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
  const { awardChatQuestion } = useGame();

  async function send(query: string) {
    if (!query.trim() || loading) return;
    setError(null);
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chat(query);
      setMessages((prev) => [...prev, { role: "assistant", text: res.answer }]);
      awardChatQuestion();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reach the AI assistant.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel" style={{ display: "flex", flexDirection: "column", gap: 16, minHeight: 480 }}>
      <div>
        <h1 style={{ fontSize: 22 }}>Ask the Forecaster</h1>
        <p className="text-dim text-sm">
          Answers are grounded in the live world state, tracked systems, advisory schedule and recent
          headlines — not general knowledge alone.
        </p>
      </div>

      {messages.length === 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              className="tag"
              style={{ cursor: "pointer", whiteSpace: "normal", textAlign: "left", maxWidth: "100%" }}
              onClick={() => send(s)}
            >
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
            <div className="text-dim text-sm mono" style={{ marginBottom: 6, fontWeight: 700 }}>
              {m.role === "user" ? "YOU" : "FORECASTER"}
            </div>
            {m.text}
          </div>
        ))}
        {loading && <div className="text-dim text-sm">Reading the instruments…</div>}
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
          placeholder="Ask about Gold, USD, stocks, crypto, or an upcoming advisory…"
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
