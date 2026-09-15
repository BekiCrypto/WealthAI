"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { EconomicEvent } from "@/lib/types";
import EventTable from "@/components/EventTable";
import SyntheticDataBanner from "@/components/SyntheticDataBanner";

export default function EventsPage() {
  const [events, setEvents] = useState<EconomicEvent[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .calendar()
      .then(setEvents)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load calendar"));
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div>
        <h1 style={{ fontSize: 22 }}>Economic Calendar</h1>
        <p className="text-dim text-sm">
          Click a row to see the AI&apos;s pre-release scenario analysis: likely range, surprise probabilities, and
          expected asset reaction under each outcome.
        </p>
      </div>
      {error && <div style={{ color: "var(--bearish)" }}>{error}</div>}
      {!events && !error && <div className="text-dim">Loading…</div>}
      {events && events.some((e) => e.source === "seed") && (
        <SyntheticDataBanner>
          This calendar is a demo dataset (no licensed economic-calendar provider is wired up
          yet) — consensus/previous figures and scheduling are illustrative, not real forecasts.
        </SyntheticDataBanner>
      )}
      {events && (
        <div className="panel" style={{ padding: 0 }}>
          <EventTable events={events} />
        </div>
      )}
    </div>
  );
}
