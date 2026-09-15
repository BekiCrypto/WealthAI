"use client";

import { formatNumber } from "@/lib/format";

/**
 * A labeled readout of a tracked system's bullish_pct over recent World
 * State snapshots -- real conviction history, not a decorative flourish,
 * and not a raw price series (which the licensing gate withholds for
 * non-redistributable symbols; the Intelligence Score is our own derived
 * output regardless of the underlying data source). The line is paired
 * with its own numeric delta and range so it reads as a data readout even
 * when the trend is visually near-flat, not a bare sparkline standing in
 * for content.
 */
export default function MiniTrajectory({ series, color }: { series: number[]; color: string }) {
  if (series.length < 2) {
    return <div style={{ height: 28 }} />;
  }

  const w = 100;
  const h = 22;
  const min = Math.min(...series);
  const max = Math.max(...series);
  const span = max - min || 1;
  const delta = series[series.length - 1] - series[0];

  const points = series.map((v, i) => {
    const x = (i / (series.length - 1)) * w;
    const y = h - ((v - min) / span) * (h - 4) - 2;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <svg viewBox={`0 0 ${w} ${h}`} width="60" height={h} preserveAspectRatio="none" aria-hidden="true" style={{ flexShrink: 0 }}>
        <polyline points={points.join(" ")} fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" opacity="0.85" />
      </svg>
      <span className="mono text-sm" style={{ color: Math.abs(delta) < 0.5 ? "var(--text-dim)" : color }}>
        {delta > 0 ? "+" : ""}
        {formatNumber(delta, 1)}pp · range {formatNumber(min, 0)}–{formatNumber(max, 0)}%
      </span>
    </div>
  );
}
