import type { AchievementDefinition, GameState, RankDefinition, XPAction } from "./types";

export const RANKS: RankDefinition[] = [
  { id: "trainee", title: "Trainee Observer", minXP: 0, insignia: "•" },
  { id: "forecaster", title: "Certified Forecaster", minXP: 150, insignia: "••" },
  { id: "meteorologist", title: "Senior Meteorologist", minXP: 500, insignia: "•••" },
  { id: "chief", title: "Chief of Watch", minXP: 1200, insignia: "★" },
];

export const XP_VALUES: Record<XPAction, number> = {
  daily_checkin: 10,
  view_scenario: 5,
  view_trade_setup: 5,
  ask_chat: 8,
  read_briefing: 10,
  pass_quiz: 40,
  retake_quiz: 5,
};

export const QUIZ_PASS_THRESHOLD = 0.7; // 70% correct certifies the station
export const TOTAL_STATIONS = 8; // must match the number of entries in lib/learn/stations.ts
export const DAILY_CHAT_XP_CAP = 3; // chat still works past this; it just stops earning XP for the day

export const ACHIEVEMENTS: AchievementDefinition[] = [
  { id: "first_watch", title: "First Watch", description: "Logged your first day on the board." },
  { id: "storm_chaser", title: "Storm Chaser", description: "Kept a 7-day watch streak." },
  { id: "veteran_watch", title: "Veteran of the Watch", description: "Kept a 30-day watch streak." },
  { id: "full_forecast", title: "Full Forecast", description: "Certified on every station in the Handbook." },
  { id: "analyst", title: "Analyst", description: "Reviewed forecast tracks on 5 different systems." },
  { id: "inquisitive", title: "Inquisitive", description: "Asked the forecaster 10 questions." },
  { id: "perfect_bulletin", title: "Perfect Bulletin", description: "Scored a perfect exam on any station." },
];

export function rankForXP(xp: number): RankDefinition {
  let current = RANKS[0];
  for (const rank of RANKS) {
    if (xp >= rank.minXP) current = rank;
  }
  return current;
}

export function nextRank(xp: number): RankDefinition | null {
  const current = rankForXP(xp);
  const idx = RANKS.findIndex((r) => r.id === current.id);
  return RANKS[idx + 1] ?? null;
}

export const EMPTY_STATE: GameState = {
  xp: 0,
  streak: 0,
  lastCheckinDate: null,
  seenScenarios: [],
  seenSetups: [],
  chatCountToday: 0,
  chatCountDate: null,
  briefingsRead: [],
  quizzesCertified: [],
  quizBestScores: {},
  chatCountLifetime: 0,
  achievements: [],
};

export const STORAGE_KEY = "wealthai.forecaster.v1";
