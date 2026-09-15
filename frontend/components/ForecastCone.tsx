"use client";

import { useId } from "react";
import type { OutcomeBand } from "@/lib/types";
import { formatNumber } from "@/lib/format";

const DOMAIN = 3; // effective_z clamps to [-DOMAIN, +DOMAIN] across the chart
const VB_W = 100;
const VB_H = 40;
const BASELINE = 34;

function pct(z: number): number {
  const clamped = Math.max(-DOMAIN, Math.min(DOMAIN, z));
  return ((clamped + DOMAIN) / (2 * DOMAIN)) * VB_W;
}

function leanColor(lean: string | null): string {
  if (lean === "hawkish") return "var(--hawkish)";
  if (lean === "dovish") return "var(--dovish)";
  return "var(--neutral)";
}

/** Samples a Gaussian bump into an SVG path, baseline to baseline, so
 * nested contours at different sigma/amplitude read as isobar-style
 * probability bands -- widest and most likely at consensus, thinning into
 * the tails. Correctly represents that outcomes near consensus are more
 * probable than extreme surprises, unlike a flat bar. */
function contourPath(sigma: number, amplitude: number): string {
  const points: string[] = [];
  const steps = 60;
  for (let i = 0; i <= steps; i++) {
    const x = (i / steps) * VB_W;
    const zNorm = (x - VB_W / 2) / (VB_W / 2);
    const z = zNorm * DOMAIN;
    const g = Math.exp(-(z * z) / (2 * sigma * sigma));
    const y = BASELINE - g * amplitude * (BASELINE - 6);
    points.push(`${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`);
  }
  return points.join(" ");
}

function curveYAt(x: number, sigma: number, amplitude: number): number {
  const zNorm = (x - VB_W / 2) / (VB_W / 2);
  const z = zNorm * DOMAIN;
  const g = Math.exp(-(z * z) / (2 * sigma * sigma));
  return BASELINE - g * amplitude * (BASELINE - 6);
}

/**
 * The hero visualization for an event's scenario: a pressure-contour field
 * (nested isobar-style bands) centered on consensus, positioned by
 * policy-adjusted z-score (effective_z) so a hawkish surprise always sits
 * right/amber and a dovish one always sits left/teal -- even for an
 * inverted series like the unemployment rate. Raw print values are shown
 * as labels underneath; only the horizontal position is policy-adjusted.
 */
export default function ForecastCone({ band, unit }: { band: OutcomeBand; unit: string }) {
  const gradientId = useId();
  const [rangeA, rangeB] = band.effective_range ?? [null, null];
  const hasRange = rangeA !== null && rangeB !== null;

  const aiPct = band.ai_estimate_effective_z !== null ? pct(band.ai_estimate_effective_z) : null;
  const actualPct = band.effective_z !== null ? pct(band.effective_z) : null;
  const color = leanColor(band.policy_lean);
  const actualY = actualPct !== null ? curveYAt(actualPct, 1, 0.92) : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }} className="text-sm text-dim mono">
        <span>DOVISH / MISS</span>
        <span>CONSENSUS</span>
        <span>HAWKISH / BEAT</span>
      </div>

      <svg viewBox={`0 0 ${VB_W} ${VB_H}`} className="forecast-cone" preserveAspectRatio="none" role="img" aria-label="Forecast probability contour">
        <defs>
          <linearGradient id={gradientId} x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="var(--dovish)" stopOpacity="0.55" />
            <stop offset="48%" stopColor="var(--neutral)" stopOpacity="0.3" />
            <stop offset="52%" stopColor="var(--neutral)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="var(--hawkish)" stopOpacity="0.55" />
          </linearGradient>
        </defs>

        <line x1={0} y1={BASELINE} x2={VB_W} y2={BASELINE} stroke="var(--border)" strokeWidth="0.4" />

        {/* nested contour bands, outermost (widest sigma) drawn first */}
        <path d={contourPath(2.4, 0.32)} fill="none" stroke="var(--border-strong)" strokeWidth="0.5" />
        <path d={contourPath(1.6, 0.6)} fill="none" stroke="var(--border-strong)" strokeWidth="0.5" />
        <path
          d={`${contourPath(1, 0.92)} L${VB_W},${BASELINE} L0,${BASELINE} Z`}
          fill={`url(#${gradientId})`}
          stroke={`url(#${gradientId})`}
          strokeWidth="0.8"
        />

        {/* consensus reference line */}
        <line x1={VB_W / 2} y1={4} x2={VB_W / 2} y2={BASELINE} stroke="var(--text-dim)" strokeOpacity="0.5" strokeWidth="0.35" strokeDasharray="1.2,1" />

        {aiPct !== null && (
          <line x1={aiPct} y1={BASELINE - 6} x2={aiPct} y2={BASELINE + 2} stroke="var(--pressure-bright)" strokeWidth="0.9" strokeLinecap="round">
            <title>{`AI estimate: ${formatNumber(band.ai_estimate ?? undefined)}${unit}`}</title>
          </line>
        )}

        {actualPct !== null && actualY !== null && (
          <g>
            <line x1={actualPct} y1={actualY} x2={actualPct} y2={BASELINE + 2} stroke={color} strokeWidth="0.6" />
            <circle cx={actualPct} cy={actualY} r="2.1" fill={color} stroke="var(--bg-panel)" strokeWidth="0.8">
              <title>{`Actual: ${formatNumber(band.actual ?? undefined)}${unit} (z=${band.actual_z})`}</title>
            </circle>
          </g>
        )}
      </svg>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 14 }} className="text-sm">
        <span className="text-dim">
          Previous <span className="mono">{formatNumber(band.previous ?? undefined)}{unit}</span>
        </span>
        <span className="text-dim">
          Consensus <span className="mono">{formatNumber(band.consensus ?? undefined)}{unit}</span>
        </span>
        {hasRange && (
          <span className="text-dim">
            Likely range{" "}
            <span className="mono">
              {formatNumber(band.low ?? undefined)}–{formatNumber(band.high ?? undefined)}{unit}
            </span>
          </span>
        )}
        {band.actual !== null && (
          <span>
            Actual <span className="mono" style={{ color, fontWeight: 700 }}>{formatNumber(band.actual ?? undefined)}{unit}</span>
          </span>
        )}
      </div>

      {band.actual !== null && band.policy_lean && (
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span className="tag" style={{ color, borderColor: color }}>
            {band.magnitude} {band.policy_lean === "neutral" ? "in line" : band.policy_lean}
          </span>
          {band.inverted && <span className="text-dim text-sm">(inverted series: a higher print is the dovish outcome)</span>}
        </div>
      )}
    </div>
  );
}
