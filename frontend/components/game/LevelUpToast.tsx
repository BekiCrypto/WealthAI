"use client";

import { useEffect, useState } from "react";
import { useGame } from "@/lib/game/GameProvider";

/**
 * A single authored motion moment for the whole app: an advisory bulletin
 * slides in from the instrument rail when XP is logged, a rank advances, or
 * a service ribbon is earned. Auto-dismisses; never blocks interaction.
 */
export default function LevelUpToast() {
  const { lastAward, clearLastAward } = useGame();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!lastAward) return;
    setVisible(true);
    const dismiss = setTimeout(() => setVisible(false), 4200);
    const clear = setTimeout(() => clearLastAward(), 4600);
    return () => {
      clearTimeout(dismiss);
      clearTimeout(clear);
    };
  }, [lastAward, clearLastAward]);

  if (!lastAward) return null;

  const headline = lastAward.leveledUp
    ? `ADVISORY — RANK ADVANCED: ${lastAward.newRank?.title.toUpperCase()}`
    : lastAward.newAchievements.length > 0
      ? `ADVISORY — RIBBON EARNED: ${lastAward.newAchievements[0].title.toUpperCase()}`
      : `ADVISORY — +${lastAward.xpGained} XP LOGGED`;

  return (
    <div className={`bulletin-toast ${visible ? "bulletin-toast-visible" : ""}`} role="status" aria-live="polite">
      <div>
        <div className="bulletin-toast-headline">{headline}</div>
        {lastAward.newAchievements.length > 1 && (
          <div className="bulletin-toast-sub">
            +{lastAward.newAchievements.length - 1} more ribbon{lastAward.newAchievements.length > 2 ? "s" : ""} earned
          </div>
        )}
      </div>
    </div>
  );
}
