"use client";

import type { TradeSetup, TradeTarget } from "@/lib/types";
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

function TargetCard({ t, color }: { t: TradeTarget; color: string }) {
  return (
    <div className="panel" style={{ padding: 12 }} title={t.note}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span className="text-dim text-sm" style={{ fontWeight: 600 }}>
          {t.label}
        </span>
        {t.r_multiple !== null && (
          <span className="tag" style={{ fontSize: 11 }}>
            {formatNumber(t.r_multiple, 1)}R
          </span>
        )}
      </div>
      <div className="mono" style={{ fontWeight: 600, color, marginTop: 6 }}>
        {t.price !== null ? formatNumber(t.price) : t.pct_from_entry !== null ? `${t.pct_from_entry > 0 ? "+" : ""}${formatNumber(t.pct_from_entry, 2)}%` : "—"}
      </div>
      {t.price !== null && t.pct_from_entry !== null && (
        <div className="text-dim text-sm">
          {t.pct_from_entry > 0 ? "+" : ""}
          {formatNumber(t.pct_from_entry, 2)}%
        </div>
      )}
    </div>
  );
}

/**
 * The highest-probability entry/exit signal for an asset (spec step 9):
 * bias, entry, stop (invalidation), staged targets (TP1/TP2/TP3) and the
 * timeframe they're all sized for -- instead of a bare bullish/bearish
 * percentage. Shows absolute prices when the symbol's data is licensed for
 * that (crypto); otherwise shows the same structure as percentage
 * distances and R-multiples, with a disclosure note.
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
        <span className={`tag ${isLong ? "tag-bullish" : "tag-bearish"}`}>Bias: {isLong ? "Bullish" : "Bearish"}</span>
        <span className="tag">{setup.confidence} confidence</span>
        {setup.setup_type && <span className="tag tag-neutral">{setup.setup_type.replace(/_/g, " ")}</span>}
        <span className="tag" title={setup.timeframe_note}>
          {setup.timeframe}
        </span>
        {setup.risk_reward !== null && <span className="tag">R:R {formatNumber(setup.risk_reward, 1)}:1 (TP2)</span>}
      </div>

      <div className="grid grid-cols-4" style={{ marginBottom: 12 }}>
        <Level label="Entry" price={setup.entry_price} pct={setup.entry_pct_from_last} />
        <Level label="Stop (SL / invalidation)" price={setup.stop_price} pct={setup.stop_pct_from_entry} color="var(--bearish)" />
      </div>

      <div className="text-dim text-sm" style={{ marginBottom: 8 }}>
        Targets (scale out: take partial profit at each level)
      </div>
      <div className="grid grid-cols-4" style={{ marginBottom: 16 }}>
        {setup.targets.map((t) => (
          <TargetCard key={t.label} t={t} color={color} />
        ))}
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
        <div>
          <div className="text-dim text-sm" style={{ fontWeight: 600, marginBottom: 4 }}>
            Timeframe
          </div>
          <p className="text-sm" style={{ margin: 0, lineHeight: 1.6 }}>
            {setup.timeframe_note}
          </p>
        </div>
      </div>
    </div>
  );
}
