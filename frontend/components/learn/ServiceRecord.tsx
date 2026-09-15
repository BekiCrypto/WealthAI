"use client";

import { useGame } from "@/lib/game/GameProvider";
import { ACHIEVEMENTS, RANKS, TOTAL_STATIONS, nextRank, rankForXP } from "@/lib/game/config";
import PressureGauge from "@/components/PressureGauge";

export default function ServiceRecord() {
  const { state, hydrated } = useGame();

  if (!hydrated) {
    return <div className="panel text-dim text-sm">Loading service record…</div>;
  }

  const rank = rankForXP(state.xp);
  const next = nextRank(state.xp);
  const certifiedPct = Math.round((state.quizzesCertified.length / TOTAL_STATIONS) * 100);

  return (
    <div className="panel">
      <div style={{ display: "flex", gap: 24, flexWrap: "wrap", alignItems: "flex-start" }}>
        <PressureGauge value={certifiedPct} color="var(--pressure-bright)" label="stations certified" size={96} />

        <div style={{ flex: 1, minWidth: 240 }}>
          <h2 style={{ fontSize: 18 }}>{rank.title}</h2>
          <p className="text-dim text-sm" style={{ margin: "4px 0 10px" }}>
            {next
              ? `${next.minXP - state.xp} XP to ${next.title}`
              : "Maximum rank reached."}{" "}
            · {state.xp} XP logged · {state.streak > 0 ? `${state.streak}-day watch streak` : "no active streak"}
          </p>
          <div className="rank-badge-track" style={{ height: 6, maxWidth: 320 }}>
            <span
              className="rank-badge-fill"
              style={{
                width: next ? `${Math.min(100, Math.round(((state.xp - rank.minXP) / (next.minXP - rank.minXP)) * 100))}%` : "100%",
              }}
            />
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 14 }}>
            {RANKS.map((r) => (
              <span key={r.id} className={`tag ${r.id === rank.id ? "tag-bullish" : "tag-neutral"}`}>
                {r.insignia} {r.title}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="text-dim text-sm" style={{ fontWeight: 600, margin: "20px 0 10px" }}>
        Service ribbons — {state.achievements.length} of {ACHIEVEMENTS.length} earned
      </div>
      <div className="grid grid-cols-4">
        {ACHIEVEMENTS.map((a) => {
          const earned = state.achievements.includes(a.id);
          return (
            <div
              key={a.id}
              className="panel"
              style={{ padding: 12, opacity: earned ? 1 : 0.4, background: "var(--bg-panel-alt)" }}
              title={a.description}
            >
              <div className="text-sm" style={{ fontWeight: 700, color: earned ? "var(--hawkish)" : "var(--text-dim)" }}>
                {a.title}
              </div>
              <div className="text-dim text-sm" style={{ marginTop: 4 }}>
                {a.description}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
