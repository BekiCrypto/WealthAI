"use client";

import type { OutcomeBand as OutcomeBandData } from "@/lib/types";
import { formatNumber } from "@/lib/format";

const DOMAIN = 3; // effective_z clamps to [-DOMAIN, +DOMAIN] across the strip

function pct(z: number): number {
  const clamped = Math.max(-DOMAIN, Math.min(DOMAIN, z));
  return ((clamped + DOMAIN) / (2 * DOMAIN)) * 100;
}

function leanColor(lean: string | null): string {
  if (lean === "hawkish") return "var(--hawkish)";
  if (lean === "dovish") return "var(--dovish)";
  return "var(--neutral)";
}

/**
 * The hero visualization for an event card: a diverging strip from big-miss
 * to big-beat, positioned by *policy-adjusted* z-score (effective_z) so a
 * hawkish surprise always sits right/amber and a dovish one always sits
 * left/teal -- even for an inverted series like the unemployment rate,
 * where a higher print is the dovish outcome. Raw print values are shown as
 * labels underneath; only the horizontal position is policy-adjusted.
 */
export default function OutcomeBand({ band, unit }: { band: OutcomeBandData; unit: string }) {
  const [rangeA, rangeB] = band.effective_range ?? [null, null];
  const hasRange = rangeA !== null && rangeB !== null;
  const rangeLeft = hasRange ? Math.min(pct(rangeA as number), pct(rangeB as number)) : null;
  const rangeRight = hasRange ? Math.max(pct(rangeA as number), pct(rangeB as number)) : null;

  const aiPct = band.ai_estimate_effective_z !== null ? pct(band.ai_estimate_effective_z) : null;
  const actualPct = band.effective_z !== null ? pct(band.effective_z) : null;
  const color = leanColor(band.policy_lean);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }} className="text-sm text-dim">
        <span>Big miss / dovish</span>
        <span>Consensus</span>
        <span>Big beat / hawkish</span>
      </div>

      <div style={{ position: "relative", height: 34 }}>
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: 0,
            right: 0,
            height: 8,
            transform: "translateY(-50%)",
            borderRadius: 999,
            background: "var(--band-track)",
            border: "1px solid var(--border)",
          }}
        />
        {hasRange && (
          <div
            title="AI likely range"
            style={{
              position: "absolute",
              top: "50%",
              left: `${rangeLeft}%`,
              width: `${(rangeRight as number) - (rangeLeft as number)}%`,
              height: 8,
              transform: "translateY(-50%)",
              borderRadius: 999,
              background: "rgba(255,255,255,0.12)",
            }}
          />
        )}
        {/* consensus reference line at z=0 */}
        <div
          style={{
            position: "absolute",
            top: 2,
            bottom: 2,
            left: "50%",
            width: 2,
            background: "var(--text-dim)",
            opacity: 0.6,
          }}
        />
        {aiPct !== null && (
          <div
            title={`AI estimate: ${formatNumber(band.ai_estimate ?? undefined)}${unit}`}
            style={{
              position: "absolute",
              top: "50%",
              left: `${aiPct}%`,
              width: 3,
              height: 16,
              transform: "translate(-50%, -50%)",
              background: "var(--accent)",
              borderRadius: 2,
            }}
          />
        )}
        {actualPct !== null && (
          <div
            title={`Actual: ${formatNumber(band.actual ?? undefined)}${unit} (z=${band.actual_z})`}
            style={{
              position: "absolute",
              top: "50%",
              left: `${actualPct}%`,
              width: 16,
              height: 16,
              transform: "translate(-50%, -50%)",
              borderRadius: "50%",
              background: color,
              border: "2px solid var(--bg-panel)",
              boxShadow: "0 0 0 2px " + color,
            }}
          />
        )}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 14 }} className="text-sm">
        <span className="text-dim">
          Previous <span className="mono">{formatNumber(band.previous ?? undefined)}{unit}</span>
        </span>
        <span className="text-dim">
          Consensus <span className="mono">{formatNumber(band.consensus ?? undefined)}{unit}</span>
        </span>
        <span className="text-dim">
          Likely range{" "}
          <span className="mono">
            {formatNumber(band.low ?? undefined)}–{formatNumber(band.high ?? undefined)}{unit}
          </span>
        </span>
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
