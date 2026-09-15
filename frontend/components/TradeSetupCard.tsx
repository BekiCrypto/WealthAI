"use client";

import type { TradeSetup } from "@/lib/types";
import { formatNumber, formatPercent } from "@/lib/format";

function Level({ label, price, pct, color }: { label: string; price: number | null; pct: number | null; color?: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span className="text-dim text-sm">{label}</span>
      <span className="mono" style={{ fontWeight: 600, color }}>
        {price !== null ? formatNumber(price) : pct !== null ? `${pct > 0 ? "+" : ""}${formatNumber(pct, 2)}%` : "—"}
      </span>
      {price !== null && pct !== null && (
        <span className="text-dim text-sm">
          {pct > 0 ? "+" : ""}
          {formatNumber(pct, 2)}%
        </span>
      )}
    </div>
  );
}

/**
 * The highest-probability entry/exit signal for an asset (spec step 9):
 * a concrete entry, stop (invalidation), and target instead of a bare
 * bullish/bearish percentage. Shows absolute prices when the symbol's data
 * is licensed for that (crypto); otherwise shows the same structure as
 * percentage distances and a risk/reward ratio, with a disclosure note.
 */
export default function TradeSetupCard({ setup }: { setup: TradeSetup }) {
  if (setup.direction === "none") {
    return (
      <div className="panel">
        <div className="section-title">Trade Setup</div>
        <div className="text-sm text-dim">
          No high-probability setup right now. {setup.reasoning}
        </div>
      </div>
    );
  }

  const isLong = setup.direction === "long";
  const color = isLong ? "var(--bullish)" : "var(--bearish)";

  return (
    <div className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div className="section-title" style={{ marginBottom: 0 }}>
          Trade Setup
        </div>
        <span className={`tag ${isLong ? "tag-bullish" : "tag-bearish"}`}>
          {setup.direction.toUpperCase()} · {formatPercent(setup.probability, 0)} probability
        </span>
      </div>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", margin: "12px 0" }}>
        <span className="tag">{setup.confidence} confidence</span>
        {setup.setup_type && <span className="tag tag-neutral">{setup.setup_type.replace(/_/g, " ")}</span>}
        {setup.risk_reward !== null && <span className="tag">R:R {formatNumber(setup.risk_reward, 1)}:1</span>}
      </div>

      <div className="grid grid-cols-4" style={{ marginBottom: 16 }}>
        <Level label="Entry" price={setup.entry_price} pct={setup.entry_pct_from_last} />
        <Level label="Stop (invalidation)" price={setup.stop_price} pct={setup.stop_pct_from_entry} color="var(--bearish)" />
        <Level label="Target" price={setup.target_price} pct={setup.target_pct_from_entry} color="var(--bullish)" />
      </div>

      {!setup.redistributable && setup.price_disclosure && (
        <div className="text-dim text-sm" style={{ marginBottom: 14 }}>
          {setup.price_disclosure}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <div>
          <div className="text-dim text-sm" style={{ fontWeight: 600, marginBottom: 4 }}>
            Why this entry
          </div>
          <p className="text-sm" style={{ margin: 0, lineHeight: 1.6 }}>
            {setup.reasoning}
          </p>
        </div>
        <div>
          <div className="text-dim text-sm" style={{ fontWeight: 600, marginBottom: 4 }}>
            What would invalidate this
          </div>
          <p className="text-sm" style={{ margin: 0, lineHeight: 1.6 }}>
            {setup.invalidation}
          </p>
        </div>
        <div>
          <div className="text-dim text-sm" style={{ fontWeight: 600, marginBottom: 4 }}>
            Main risk
          </div>
          <p className="text-sm" style={{ margin: 0, lineHeight: 1.6 }}>
            {setup.main_risk}
          </p>
        </div>
      </div>
    </div>
  );
}
