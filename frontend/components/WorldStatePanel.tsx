"use client";

import type { WorldStateRegime } from "@/lib/types";
import { directionClass } from "@/lib/format";

const FIELDS: { key: keyof WorldStateRegime; label: string }[] = [
  { key: "inflation", label: "Inflation" },
  { key: "usd", label: "USD" },
  { key: "yields", label: "Yields" },
  { key: "oil", label: "Oil" },
  { key: "gold", label: "Gold" },
  { key: "equities", label: "Equities" },
  { key: "crypto", label: "Crypto" },
  { key: "geopolitical_risk", label: "Geopolitical Risk" },
];

function regimeColor(regime: string): string {
  if (regime === "Risk-Off") return "var(--bearish)";
  if (regime === "Risk-On") return "var(--bullish)";
  return "var(--hawkish)";
}

export default function WorldStatePanel({
  regime,
  reasoning,
}: {
  regime: WorldStateRegime;
  reasoning: Record<string, string>;
}) {
  const color = regimeColor(regime.risk_regime);

  return (
    <div className="panel situation-headline" style={{ borderColor: `color-mix(in srgb, ${color} 30%, var(--border))` }}>
      <h2 style={{ fontSize: 24, color }}>
        {regime.risk_regime.toUpperCase()} ADVISORY IN EFFECT
      </h2>
      <p className="text-dim text-sm" style={{ margin: "4px 0 20px", maxWidth: "65ch" }}>
        {reasoning.risk_regime}
      </p>

      <div className="grid grid-cols-4">
        {FIELDS.map(({ key, label }) => {
          const value = String(regime[key] ?? "unknown");
          const reason = reasoning[key];
          return (
            <div key={key} title={reason || undefined} style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span className="text-dim text-sm">{label}</span>
              <span className={`tag ${directionClass(value)}`} style={{ width: "fit-content" }}>
                <span className="dot" />
                {value.replace(/_/g, " ")}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
