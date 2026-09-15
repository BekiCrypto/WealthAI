"use client";

import { useEffect, useState } from "react";
import type { IndicatorEducation } from "@/lib/types";
import { useGame } from "@/lib/game/GameProvider";

const SECTIONS: { key: keyof IndicatorEducation; label: string }[] = [
  { key: "what_it_is", label: "What it is" },
  { key: "why_it_matters", label: "Why it matters" },
  { key: "market_impact_chain", label: "How it moves markets" },
  { key: "how_to_read", label: "How to read it" },
  { key: "historical_context", label: "Historical context" },
  { key: "watch_for", label: "What to watch for" },
];

/**
 * The educational briefing for one indicator: what it is, why it matters,
 * and how to read it -- meant to teach the reader the mechanism, not just
 * hand them a bullish/bearish call. `collapsible` renders it behind a
 * toggle (used inline on an event's scenario detail, where the outcome
 * band is the primary content); the standalone /learn page renders it
 * open by default.
 */
export default function IndicatorBriefing({
  briefing,
  collapsible = false,
  defaultOpen = false,
}: {
  briefing: IndicatorEducation;
  collapsible?: boolean;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen || !collapsible);
  const { awardBriefingRead } = useGame();

  function toggle() {
    if (!collapsible) return;
    setOpen((v) => {
      if (!v) awardBriefingRead(briefing.name);
      return !v;
    });
  }

  useEffect(() => {
    if (!collapsible) awardBriefingRead(briefing.name);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collapsible, briefing.name]);

  return (
    <div className="panel" style={{ padding: 16 }}>
      <div
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: collapsible ? "pointer" : "default" }}
        onClick={toggle}
      >
        <div>
          <h3 style={{ fontSize: 15 }}>{briefing.name}</h3>
          <span className="text-dim text-sm" style={{ textTransform: "capitalize" }}>
            {briefing.category.replace(/_/g, " ")}
            {briefing.inverted && " · inverted indicator"}
          </span>
        </div>
        {collapsible && (
          <span className="text-sm" style={{ color: "var(--pressure-bright)" }}>
            {open ? "Hide" : "Learn about this indicator"}
          </span>
        )}
      </div>

      {open && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 14 }}>
          {briefing.inverted && (
            <div className="text-sm" style={{ color: "var(--warn)" }}>
              This is an inverted indicator: a higher print is the dovish/weaker-economy outcome,
              not the hawkish one — the opposite of most releases in this calendar.
            </div>
          )}
          {SECTIONS.map(({ key, label }) => (
            <div key={key}>
              <div className="text-dim text-sm" style={{ fontWeight: 600, marginBottom: 4 }}>
                {label}
              </div>
              <p className="text-sm" style={{ margin: 0, lineHeight: 1.6 }}>
                {briefing[key] as string}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
