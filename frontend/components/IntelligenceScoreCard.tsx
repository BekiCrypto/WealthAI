"use client";

import Link from "next/link";
import type { ScoreBreakdown } from "@/lib/types";
import { SYMBOL_LABELS } from "@/lib/api";
import { directionClass } from "@/lib/format";

export default function IntelligenceScoreCard({ score }: { score: ScoreBreakdown }) {
  const isBullish = score.bullish_pct >= 50;
  const barColor = isBullish ? "var(--bullish)" : "var(--bearish)";

  return (
    <Link href={`/assets/${encodeURIComponent(score.symbol)}`} className="panel card-link">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 style={{ fontSize: 16 }}>{SYMBOL_LABELS[score.symbol] || score.symbol}</h3>
        <span className="text-dim text-sm mono">{score.symbol}</span>
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: 10, margin: "10px 0" }}>
        <span className="mono" style={{ fontSize: 28, fontWeight: 700, color: barColor }}>
          {score.bullish_pct}%
        </span>
        <span className="text-dim text-sm">{isBullish ? "bullish" : "bearish"}</span>
        <span className={`tag ${score.confidence === "High" ? "tag-bullish" : score.confidence === "Low" ? "tag-neutral" : "tag-warn"}`}>
          {score.confidence} confidence
        </span>
      </div>

      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${score.bullish_pct}%`, background: barColor }} />
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
        <span className={`tag ${directionClass(score.macro)}`}>Macro: {score.macro}</span>
        <span className={`tag ${directionClass(score.technical)}`}>Technical: {score.technical}</span>
        <span className={`tag ${directionClass(score.sentiment)}`}>Sentiment: {score.sentiment}</span>
        <span className={`tag ${directionClass(score.geopolitical)}`}>Geopolitical: {score.geopolitical}</span>
      </div>
    </Link>
  );
}
