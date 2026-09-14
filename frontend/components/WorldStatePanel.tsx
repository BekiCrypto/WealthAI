"use client";

import type { WorldStateRegime } from "@/lib/types";
import { directionClass } from "@/lib/format";

const FIELDS: { key: keyof WorldStateRegime; label: string }[] = [
  { key: "risk_regime", label: "Risk Regime" },
  { key: "inflation", label: "Inflation" },
  { key: "usd", label: "USD" },
  { key: "yields", label: "Yields" },
  { key: "oil", label: "Oil" },
  { key: "gold", label: "Gold" },
  { key: "equities", label: "Equities" },
  { key: "crypto", label: "Crypto" },
  { key: "geopolitical_risk", label: "Geopolitical Risk" },
];

export default function WorldStatePanel({
  regime,
  reasoning,
}: {
  regime: WorldStateRegime;
  reasoning: Record<string, string>;
}) {
  return (
    <div className="panel">
      <div className="section-title">Live World State</div>
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
