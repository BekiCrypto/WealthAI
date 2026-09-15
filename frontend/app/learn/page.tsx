"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { IndicatorEducation } from "@/lib/types";
import { STATIONS } from "@/lib/learn/stations";
import { useGame } from "@/lib/game/GameProvider";
import IndicatorBriefing from "@/components/IndicatorBriefing";
import ServiceRecord from "@/components/learn/ServiceRecord";
import StationCard, { stationMastery } from "@/components/learn/StationCard";
import Quiz from "@/components/learn/Quiz";

export default function LearnPage() {
  const [briefings, setBriefings] = useState<IndicatorEducation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [showQuiz, setShowQuiz] = useState(false);
  const { state, hydrated } = useGame();

  useEffect(() => {
    api
      .educationList()
      .then((list) => {
        setBriefings(list);
        setSelected((prev) => prev ?? list[0]?.name ?? null);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load the handbook"));
  }, []);

  const selectedBriefing = briefings?.find((b) => b.name === selected) ?? null;
  const selectedStation = STATIONS.find((s) => s.name === selected) ?? null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1 style={{ fontSize: 26 }}>The Forecaster&apos;s Handbook</h1>
        <p className="text-dim text-sm" style={{ maxWidth: "68ch" }}>
          What each release measures, why the desk watches it, and the exact mechanism by which a
          surprise moves through rates and currency to reach a tracked system like Gold or the S&amp;P
          500 — plus the gotchas, like inverted indicators, that trip up retail tools. Read a station,
          then sit its certification exam to log it in your service record.
        </p>
      </div>

      {hydrated && <ServiceRecord />}

      {error && <div style={{ color: "var(--bearish)" }}>{error}</div>}
      {!briefings && !error && <div className="text-dim">Loading handbook…</div>}

      {briefings && (
        <div>
          <div className="heading-block">
            <h2>Stations</h2>
          </div>
          <div className="grid grid-cols-4">
            {briefings.map((b) => {
              const certified = state.quizzesCertified.includes(b.name);
              const read = state.briefingsRead.includes(b.name);
              const bestScore = state.quizBestScores[b.name] ?? null;
              return (
                <StationCard
                  key={b.name}
                  name={b.name}
                  category={b.category}
                  mastery={stationMastery(read, certified)}
                  bestScore={bestScore}
                  active={selected === b.name}
                  onSelect={() => {
                    setSelected(b.name);
                    setShowQuiz(false);
                  }}
                />
              );
            })}
          </div>
        </div>
      )}

      {selectedBriefing && (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <IndicatorBriefing briefing={selectedBriefing} />

          {selectedStation && !showQuiz && (
            <div className="panel" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
              <div>
                <div style={{ fontWeight: 700 }}>Certification exam</div>
                <div className="text-dim text-sm">
                  {selectedStation.quiz.length} questions · pass at 70% or higher to certify this station
                </div>
              </div>
              <button className="btn" onClick={() => setShowQuiz(true)}>
                Start exam
              </button>
            </div>
          )}

          {selectedStation && showQuiz && (
            <Quiz station={selectedStation.name} questions={selectedStation.quiz} onClose={() => setShowQuiz(false)} />
          )}
        </div>
      )}
    </div>
  );
}
