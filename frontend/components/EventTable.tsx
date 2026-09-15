"use client";

import { Fragment, useState } from "react";
import type { EconomicEvent, EventScenario } from "@/lib/types";
import { api } from "@/lib/api";
import { directionClass, formatNumber } from "@/lib/format";
import EventCountdown from "./EventCountdown";
import OutcomeBand from "./OutcomeBand";
import SyntheticDataBanner from "./SyntheticDataBanner";

function importanceClass(importance: string): string {
  if (importance === "high") return "tag-warn";
  if (importance === "medium") return "tag-neutral";
  return "tag-unknown";
}

function ScenarioDetail({ scenario, eventUnit }: { scenario: EventScenario; eventUnit: string }) {
  const released = scenario.outcome_band.actual !== null;
  const activeScenarioKey = released
    ? scenario.outcome_band.policy_lean === "hawkish"
      ? "hot"
      : scenario.outcome_band.policy_lean === "dovish"
        ? "cool"
        : "base"
    : null;

  return (
    <tr>
      <td colSpan={8} style={{ background: "var(--bg-panel-alt)" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16, padding: "14px 4px" }}>
          <OutcomeBand band={scenario.outcome_band} unit={eventUnit} />

          <div className="text-sm text-dim">
            Hot {formatNumber((scenario.probabilities.hot ?? 0) * 100, 0)}% · Cool{" "}
            {formatNumber((scenario.probabilities.cool ?? 0) * 100, 0)}% · In-line{" "}
            {formatNumber((scenario.probabilities.in_line ?? 0) * 100, 0)}%
          </div>

          <div className="grid grid-cols-2">
            {Object.entries(scenario.scenarios).map(([key, s]) => (
              <div
                key={key}
                className="panel"
                style={{ padding: 12, opacity: activeScenarioKey && activeScenarioKey !== key ? 0.45 : 1 }}
              >
                <div className="text-sm" style={{ fontWeight: 600, marginBottom: 8, textTransform: "capitalize" }}>
                  {key} scenario {activeScenarioKey === key && "— what happened"}
                </div>
                <div className="text-dim text-sm" style={{ marginBottom: 8 }}>
                  {s.description}
                </div>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {Object.entries(s.asset_impact).map(([symbol, dir]) => (
                    <span key={symbol} className={`tag ${directionClass(dir)}`}>
                      {symbol}: {dir}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <SyntheticDataBanner>{scenario.disclosure}</SyntheticDataBanner>
        </div>
      </td>
    </tr>
  );
}

export default function EventTable({ events }: { events: EconomicEvent[] }) {
  const [expanded, setExpanded] = useState<number | null>(null);
  const [scenarios, setScenarios] = useState<Record<number, EventScenario>>({});
  const [loadingId, setLoadingId] = useState<number | null>(null);

  async function toggle(event: EconomicEvent) {
    if (expanded === event.id) {
      setExpanded(null);
      return;
    }
    setExpanded(event.id);
    if (!scenarios[event.id]) {
      setLoadingId(event.id);
      try {
        const scenario = await api.eventScenario(event.id);
        setScenarios((prev) => ({ ...prev, [event.id]: scenario }));
      } catch {
        // leave collapsed content empty; row stays expanded with no detail
      } finally {
        setLoadingId(null);
      }
    }
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Event</th>
          <th>Country</th>
          <th>Importance</th>
          <th>When</th>
          <th>Previous</th>
          <th>Consensus</th>
          <th>Actual</th>
          <th>Surprise</th>
        </tr>
      </thead>
      <tbody>
        {events.map((event) => (
          <Fragment key={event.id}>
            <tr onClick={() => toggle(event)} style={{ cursor: "pointer" }}>
              <td>{event.name}</td>
              <td className="text-dim">{event.country}</td>
              <td>
                <span className={`tag ${importanceClass(event.importance)}`}>{event.importance}</span>
              </td>
              <td>
                <EventCountdown targetIso={event.scheduled_at} />
              </td>
              <td className="mono">
                {formatNumber(event.previous)}
                {event.unit}
              </td>
              <td className="mono">
                {formatNumber(event.consensus)}
                {event.unit}
              </td>
              <td className="mono">{event.actual !== null ? `${formatNumber(event.actual)}${event.unit}` : "—"}</td>
              <td className="mono">
                {event.surprise !== null ? (
                  <span className={event.surprise > 0 ? "tag-bullish" : event.surprise < 0 ? "tag-bearish" : ""}>
                    {event.surprise > 0 ? "+" : ""}
                    {formatNumber(event.surprise)}
                  </span>
                ) : (
                  "—"
                )}
              </td>
            </tr>
            {expanded === event.id && scenarios[event.id] && (
              <ScenarioDetail scenario={scenarios[event.id]} eventUnit={event.unit} />
            )}
            {expanded === event.id && loadingId === event.id && (
              <tr>
                <td colSpan={8} className="text-dim text-sm">
                  Loading scenario…
                </td>
              </tr>
            )}
          </Fragment>
        ))}
      </tbody>
    </table>
  );
}
