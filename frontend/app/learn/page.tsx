"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { IndicatorEducation } from "@/lib/types";
import IndicatorBriefing from "@/components/IndicatorBriefing";

export default function LearnPage() {
  const [briefings, setBriefings] = useState<IndicatorEducation[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .educationList()
      .then(setBriefings)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load the glossary"));
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div>
        <h1 style={{ fontSize: 22 }}>Learn the Indicators</h1>
        <p className="text-dim text-sm">
          What each release measures, why markets watch it, how a surprise typically transmits
          through rates and currencies to reach an asset like Gold or the S&amp;P 500, and the
          gotchas (like inverted indicators) that trip up retail tools. This is the same
          knowledge behind every score and scenario on this site — read here once, and the
          calendar and scenario pages will make a lot more sense.
        </p>
      </div>
      {error && <div style={{ color: "var(--bearish)" }}>{error}</div>}
      {!briefings && !error && <div className="text-dim">Loading…</div>}
      {briefings && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {briefings.map((b) => (
            <IndicatorBriefing key={b.name} briefing={b} />
          ))}
        </div>
      )}
    </div>
  );
}
