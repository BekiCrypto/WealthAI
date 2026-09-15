"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { AchievementDefinition, AwardResult, GameState } from "./types";
import {
  ACHIEVEMENTS,
  DAILY_CHAT_XP_CAP,
  EMPTY_STATE,
  QUIZ_PASS_THRESHOLD,
  STORAGE_KEY,
  TOTAL_STATIONS,
  XP_VALUES,
  rankForXP,
} from "./config";

function todayKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function yesterdayKey(): string {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function loadState(): GameState {
  if (typeof window === "undefined") return EMPTY_STATE;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return EMPTY_STATE;
    return { ...EMPTY_STATE, ...JSON.parse(raw) };
  } catch {
    return EMPTY_STATE;
  }
}

function saveState(state: GameState) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // private-browsing / quota errors: gamification degrades to session-only, silently
  }
}

/** A mutation returns the fields to change plus how much XP that change earns
 * (0 when the action was a no-op, e.g. a station already read today). */
type Mutation = (prev: GameState) => { patch: Partial<GameState>; xpGained: number };

interface GameContextValue {
  state: GameState;
  hydrated: boolean;
  lastAward: AwardResult | null;
  clearLastAward: () => void;
  checkIn: () => void;
  awardScenarioView: (eventId: string) => void;
  awardTradeSetupView: (symbol: string) => void;
  awardChatQuestion: () => void;
  awardBriefingRead: (station: string) => void;
  awardQuizResult: (station: string, scorePct: number) => void;
}

const GameContext = createContext<GameContextValue | null>(null);

export function GameProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<GameState>(EMPTY_STATE);
  const [hydrated, setHydrated] = useState(false);
  const [lastAward, setLastAward] = useState<AwardResult | null>(null);
  const hasCheckedInRef = useRef(false);

  useEffect(() => {
    setState(loadState());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) saveState(state);
  }, [hydrated, state]);

  const run = useCallback((mutation: Mutation) => {
    setState((prev) => {
      const prevRank = rankForXP(prev.xp);
      const { patch, xpGained } = mutation(prev);
      let next: GameState = { ...prev, ...patch, xp: prev.xp + xpGained };

      const newRank = rankForXP(next.xp);
      const leveledUp = newRank.id !== prevRank.id && next.xp > prev.xp;

      const newlyUnlocked: AchievementDefinition[] = [];
      const unlock = (id: string) => {
        if (!next.achievements.includes(id)) {
          next = { ...next, achievements: [...next.achievements, id] };
          const def = ACHIEVEMENTS.find((a) => a.id === id);
          if (def) newlyUnlocked.push(def);
        }
      };

      if (next.streak >= 1) unlock("first_watch");
      if (next.streak >= 7) unlock("storm_chaser");
      if (next.streak >= 30) unlock("veteran_watch");
      if (next.quizzesCertified.length >= TOTAL_STATIONS) unlock("full_forecast");
      if (next.seenSetups.length >= 5) unlock("analyst");
      if (next.chatCountLifetime >= 10) unlock("inquisitive");
      if (Object.values(next.quizBestScores).some((s) => s >= 1)) unlock("perfect_bulletin");

      if (xpGained > 0 || leveledUp || newlyUnlocked.length > 0) {
        setLastAward({ xpGained, leveledUp, newRank: leveledUp ? newRank : null, newAchievements: newlyUnlocked });
      }
      return next;
    });
  }, []);

  const checkIn = useCallback(() => {
    if (hasCheckedInRef.current) return;
    hasCheckedInRef.current = true;
    run((prev) => {
      const today = todayKey();
      if (prev.lastCheckinDate === today) return { patch: {}, xpGained: 0 };
      const continuedStreak = prev.lastCheckinDate === yesterdayKey();
      return {
        patch: { lastCheckinDate: today, streak: continuedStreak ? prev.streak + 1 : 1 },
        xpGained: XP_VALUES.daily_checkin,
      };
    });
  }, [run]);

  useEffect(() => {
    if (hydrated) checkIn();
  }, [hydrated, checkIn]);

  const awardScenarioView = useCallback(
    (eventId: string) => {
      run((prev) => {
        if (prev.seenScenarios.includes(eventId)) return { patch: {}, xpGained: 0 };
        return { patch: { seenScenarios: [...prev.seenScenarios, eventId] }, xpGained: XP_VALUES.view_scenario };
      });
    },
    [run]
  );

  const awardTradeSetupView = useCallback(
    (symbol: string) => {
      run((prev) => {
        if (prev.seenSetups.includes(symbol)) return { patch: {}, xpGained: 0 };
        return { patch: { seenSetups: [...prev.seenSetups, symbol] }, xpGained: XP_VALUES.view_trade_setup };
      });
    },
    [run]
  );

  const awardChatQuestion = useCallback(() => {
    run((prev) => {
      const today = todayKey();
      const sameDay = prev.chatCountDate === today;
      const countToday = sameDay ? prev.chatCountToday : 0;
      const patch: Partial<GameState> = {
        chatCountDate: today,
        chatCountToday: countToday + 1,
        chatCountLifetime: prev.chatCountLifetime + 1,
      };
      const xpGained = countToday < DAILY_CHAT_XP_CAP ? XP_VALUES.ask_chat : 0;
      return { patch, xpGained };
    });
  }, [run]);

  const awardBriefingRead = useCallback(
    (station: string) => {
      run((prev) => {
        if (prev.briefingsRead.includes(station)) return { patch: {}, xpGained: 0 };
        return { patch: { briefingsRead: [...prev.briefingsRead, station] }, xpGained: XP_VALUES.read_briefing };
      });
    },
    [run]
  );

  const awardQuizResult = useCallback(
    (station: string, scorePct: number) => {
      run((prev) => {
        const prevBest = prev.quizBestScores[station] ?? 0;
        const quizBestScores = { ...prev.quizBestScores, [station]: Math.max(prevBest, scorePct) };
        const alreadyCertified = prev.quizzesCertified.includes(station);
        const nowPasses = scorePct >= QUIZ_PASS_THRESHOLD;

        if (nowPasses && !alreadyCertified) {
          return {
            patch: { quizBestScores, quizzesCertified: [...prev.quizzesCertified, station] },
            xpGained: XP_VALUES.pass_quiz,
          };
        }
        return { patch: { quizBestScores }, xpGained: XP_VALUES.retake_quiz };
      });
    },
    [run]
  );

  const clearLastAward = useCallback(() => setLastAward(null), []);

  return (
    <GameContext.Provider
      value={{
        state,
        hydrated,
        lastAward,
        clearLastAward,
        checkIn,
        awardScenarioView,
        awardTradeSetupView,
        awardChatQuestion,
        awardBriefingRead,
        awardQuizResult,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

export function useGame(): GameContextValue {
  const ctx = useContext(GameContext);
  if (!ctx) throw new Error("useGame must be used within GameProvider");
  return ctx;
}
