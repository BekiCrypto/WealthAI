"use client";

import Link from "next/link";
import type { TradeSetup } from "@/lib/types";
import { SYMBOL_LABELS } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/format";
import PressureGauge from "./PressureGauge";

/**
 * A dashboard-level view of where the highest-probability entries are right
 * now, across every tracked symbol -- so a reader doesn't have to open each
 * asset page to find out whether there's anything worth looking at.
 */
export default function TradeSetupsSummary({ setups }: { setups: TradeSetup[] }) {
  const active = setups.filter((s) => s.direction !== "none").sort((a, b) => b.probability - a.probability);

  if (active.length === 0) {
    return (
      <div className="panel">
        <h2 style={{ fontSize: 18 }}>Plotted Tracks</h2>
        <div className="text-dim text-sm" style={{ marginTop: 6 }}>
          No high-probability tracks across the tracked universe right now.
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="heading-block">
        <h2>Plotted Tracks</h2>
      </div>
      <div className="grid grid-cols-4">
        {active.map((s) => {
          const isLong = s.direction === "long";
          const color = isLong ? "var(--bullish)" : "var(--bearish)";
          return (
            <Link key={s.symbol} href={`/assets/${encodeURIComponent(s.symbol)}`} className="panel card-link tracked-system-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <h3 style={{ fontSize: 15 }}>{SYMBOL_LABELS[s.symbol] || s.symbol}</h3>
                  <span className={`tag ${isLong ? "tag-bullish" : "tag-bearish"}`} style={{ marginTop: 6 }}>
                    {s.direction.toUpperCase()}
                  </span>
                </div>
                <PressureGauge value={s.probability} color={color} label={s.confidence} size={58} />
              </div>
              {s.risk_reward !== null && (
                <div className="text-sm text-dim" style={{ marginTop: 10 }}>
                  R:R {formatNumber(s.risk_reward, 1)}:1 · entry{" "}
                  {s.entry_pct_from_last !== null ? `${s.entry_pct_from_last > 0 ? "+" : ""}${formatNumber(s.entry_pct_from_last, 1)}%` : "at market"}
                </div>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
