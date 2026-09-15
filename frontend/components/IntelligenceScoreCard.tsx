"use client";

import Link from "next/link";
import type { ScoreBreakdown } from "@/lib/types";
import { SYMBOL_LABELS } from "@/lib/api";
import { convictionTier, directionClass } from "@/lib/format";
import PressureGauge from "./PressureGauge";
import MiniTrajectory from "./MiniTrajectory";

export default function IntelligenceScoreCard({ score, trajectory }: { score: ScoreBreakdown; trajectory?: number[] }) {
  const isBullish = score.bullish_pct >= 50;
  const color = isBullish ? "var(--bullish)" : "var(--bearish)";
  const tier = convictionTier(score.bullish_pct, score.confidence);

  return (
    <Link href={`/assets/${encodeURIComponent(score.symbol)}`} className="panel card-link tracked-system-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h3 style={{ fontSize: 16 }}>{SYMBOL_LABELS[score.symbol] || score.symbol}</h3>
          <span className="text-dim text-sm mono">{score.symbol}</span>
        </div>
        <span className={`tag ${tier.tagClass}`}>{tier.label}</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 16, margin: "14px 0" }}>
        <PressureGauge value={score.bullish_pct} color={color} label={isBullish ? "bullish" : "bearish"} size={76} />
        <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1 }}>
          <span className="tag" style={{ width: "fit-content" }}>{score.confidence} confidence</span>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span className={`tag ${directionClass(score.macro)}`}>Macro</span>
            <span className={`tag ${directionClass(score.technical)}`}>Technical</span>
            <span className={`tag ${directionClass(score.sentiment)}`}>Sentiment</span>
            <span className={`tag ${directionClass(score.geopolitical)}`}>Geo</span>
          </div>
        </div>
      </div>

      {trajectory && trajectory.length >= 2 && (
        <div>
          <div className="text-dim text-sm" style={{ marginBottom: 2 }}>
            Conviction trajectory
          </div>
          <MiniTrajectory series={trajectory} color={color} />
        </div>
      )}
    </Link>
  );
}
