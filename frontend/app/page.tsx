"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { EconomicEvent, TradeSetup, WorldState } from "@/lib/types";
import WorldStatePanel from "@/components/WorldStatePanel";
import IntelligenceScoreCard from "@/components/IntelligenceScoreCard";
import EventCountdown from "@/components/EventCountdown";
import TradeSetupsSummary from "@/components/TradeSetupsSummary";

const REFRESH_MS = 60_000;

export default function DashboardPage() {
  const [worldState, setWorldState] = useState<WorldState | null>(null);
  const [events, setEvents] = useState<EconomicEvent[]>([]);
  const [setups, setSetups] = useState<TradeSetup[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [ws, cal, ts] = await Promise.all([api.worldState(), api.calendar(), api.assetSetups()]);
        if (cancelled) return;
        setWorldState(ws);
        setEvents(cal.slice(0, 5));
        setSetups(ts);
        setError(null);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load live data");
      }
    }

    load();
    const id = setInterval(load, REFRESH_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (error) {
    return (
      <div className="panel" style={{ color: "var(--bearish)" }}>
        {error}. Is the backend running at the configured NEXT_PUBLIC_API_BASE?
      </div>
    );
  }

  if (!worldState) {
    return <div className="text-dim">Loading live market intelligence…</div>;
  }

  const scores = Object.values(worldState.scores);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <WorldStatePanel regime={worldState.regime} reasoning={worldState.reasoning} />

      <div>
        <div className="section-title">Intelligence Scores</div>
        <div className="grid grid-cols-4">
          {scores.map((score) => (
            <IntelligenceScoreCard key={score.symbol} score={score} />
          ))}
          {scores.length === 0 && (
            <div className="text-dim text-sm">No price data yet — the ingestion scheduler is still warming up.</div>
          )}
        </div>
      </div>

      <TradeSetupsSummary setups={setups} />

      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <div className="section-title">Upcoming Events</div>
          <Link href="/events" className="text-sm" style={{ color: "var(--accent)" }}>
            Full calendar →
          </Link>
        </div>
        <div className="panel" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Event</th>
                <th>Country</th>
                <th>When</th>
                <th>Consensus</th>
                <th>AI Estimate</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id}>
                  <td>{e.name}</td>
                  <td className="text-dim">{e.country}</td>
                  <td>
                    <EventCountdown targetIso={e.scheduled_at} />
                  </td>
                  <td className="mono">
                    {e.consensus ?? "—"}
                    {e.unit}
                  </td>
                  <td className="mono">
                    {e.ai_estimate ?? "—"}
                    {e.unit}
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-dim text-sm">
                    No upcoming events in the calendar.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
