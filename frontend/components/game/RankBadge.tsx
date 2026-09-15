"use client";

import Link from "next/link";
import { useGame } from "@/lib/game/GameProvider";
import { nextRank, rankForXP } from "@/lib/game/config";

export default function RankBadge() {
  const { state, hydrated } = useGame();

  if (!hydrated) return <div className="rank-badge rank-badge-loading" aria-hidden="true" />;

  const rank = rankForXP(state.xp);
  const next = nextRank(state.xp);
  const span = next ? next.minXP - rank.minXP : 1;
  const progressed = next ? state.xp - rank.minXP : span;
  const pct = Math.min(100, Math.round((progressed / span) * 100));

  return (
    <Link href="/learn" className="rank-badge" title={next ? `${next.minXP - state.xp} XP to ${next.title}` : "Maximum rank"}>
      <span className="rank-badge-insignia">{rank.insignia}</span>
      <span className="rank-badge-text">
        <span className="rank-badge-title">{rank.title}</span>
        <span className="rank-badge-track">
          <span className="rank-badge-fill" style={{ width: `${pct}%` }} />
        </span>
      </span>
      {state.streak > 0 && <span className="rank-badge-streak">{state.streak}d watch</span>}
    </Link>
  );
}
