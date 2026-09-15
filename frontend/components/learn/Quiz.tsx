"use client";

import { useState } from "react";
import type { QuizQuestion } from "@/lib/learn/stations";
import { useGame } from "@/lib/game/GameProvider";
import { QUIZ_PASS_THRESHOLD } from "@/lib/game/config";

type Phase = "question" | "answered" | "result";

export default function Quiz({ station, questions, onClose }: { station: string; questions: QuizQuestion[]; onClose: () => void }) {
  const { awardQuizResult } = useGame();
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [phase, setPhase] = useState<Phase>("question");

  const question = questions[index];
  const isLast = index === questions.length - 1;

  function choose(choiceIndex: number) {
    if (phase !== "question") return;
    setSelected(choiceIndex);
    setPhase("answered");
    if (choiceIndex === question.correctIndex) setCorrectCount((c) => c + 1);
  }

  function next() {
    if (isLast) {
      const finalCorrect = correctCount;
      const scorePct = finalCorrect / questions.length;
      awardQuizResult(station, scorePct);
      setPhase("result");
      return;
    }
    setIndex((i) => i + 1);
    setSelected(null);
    setPhase("question");
  }

  function retake() {
    setIndex(0);
    setSelected(null);
    setCorrectCount(0);
    setPhase("question");
  }

  if (phase === "result") {
    const scorePct = correctCount / questions.length;
    const passed = scorePct >= QUIZ_PASS_THRESHOLD;
    return (
      <div className="panel" style={{ background: "var(--bg-panel-alt)" }}>
        <h3 style={{ fontSize: 16, color: passed ? "var(--bullish)" : "var(--bearish)" }}>
          {passed ? "Certification Passed" : "Certification Not Yet Passed"}
        </h3>
        <p className="text-sm text-dim" style={{ margin: "6px 0 14px" }}>
          Scored {correctCount} of {questions.length} ({Math.round(scorePct * 100)}%). {passed ? "This station is now certified in your service record." : `A score of ${Math.round(QUIZ_PASS_THRESHOLD * 100)}% or higher certifies this station.`}
        </p>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn" onClick={retake}>
            {passed ? "Retake exam" : "Try again"}
          </button>
          <button
            className="tag"
            style={{ cursor: "pointer", border: "1px solid var(--border)" }}
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="panel" style={{ background: "var(--bg-panel-alt)" }}>
      <div className="text-dim text-sm mono" style={{ marginBottom: 10 }}>
        CERTIFICATION EXAM — QUESTION {index + 1} OF {questions.length}
      </div>
      <p style={{ fontSize: 15, fontWeight: 600, margin: "0 0 14px" }}>{question.question}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {question.choices.map((choice, i) => {
          const isCorrect = i === question.correctIndex;
          const isSelected = i === selected;
          let borderColor = "var(--border)";
          let bg = "var(--bg-panel)";
          if (phase === "answered") {
            if (isCorrect) {
              borderColor = "var(--bullish)";
              bg = "color-mix(in srgb, var(--bullish) 10%, var(--bg-panel))";
            } else if (isSelected) {
              borderColor = "var(--bearish)";
              bg = "color-mix(in srgb, var(--bearish) 10%, var(--bg-panel))";
            }
          }
          return (
            <button
              key={i}
              onClick={() => choose(i)}
              disabled={phase === "answered"}
              style={{
                textAlign: "left",
                padding: "10px 14px",
                borderRadius: "var(--radius-sm)",
                border: `1px solid ${borderColor}`,
                background: bg,
                color: "var(--text)",
                fontSize: 14,
                cursor: phase === "answered" ? "default" : "pointer",
              }}
            >
              {choice}
            </button>
          );
        })}
      </div>
      {phase === "answered" && (
        <div style={{ marginTop: 14, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span className="text-sm" style={{ color: selected === question.correctIndex ? "var(--bullish)" : "var(--bearish)" }}>
            {selected === question.correctIndex ? "Correct." : "Not quite."}
          </span>
          <button className="btn" onClick={next}>
            {isLast ? "See results" : "Next question"}
          </button>
        </div>
      )}
    </div>
  );
}
