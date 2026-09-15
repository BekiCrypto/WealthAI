export type XPAction =
  | "daily_checkin"
  | "view_scenario"
  | "view_trade_setup"
  | "ask_chat"
  | "read_briefing"
  | "pass_quiz"
  | "retake_quiz";

export interface RankDefinition {
  id: string;
  title: string;
  minXP: number;
  insignia: string; // short glyph/mark rendered in the badge, not an emoji icon substitute -- see RankBadge
}

export interface AchievementDefinition {
  id: string;
  title: string;
  description: string;
}

export interface GameState {
  xp: number;
  streak: number;
  lastCheckinDate: string | null; // YYYY-MM-DD, local
  seenScenarios: string[]; // event ids, deduped
  seenSetups: string[]; // symbols, deduped
  chatCountToday: number;
  chatCountDate: string | null;
  briefingsRead: string[]; // indicator names
  quizzesCertified: string[]; // indicator names, passed at least once
  quizBestScores: Record<string, number>; // indicator name -> best % score
  chatCountLifetime: number;
  achievements: string[]; // achievement ids unlocked
}

export interface AwardResult {
  xpGained: number;
  leveledUp: boolean;
  newRank: RankDefinition | null;
  newAchievements: AchievementDefinition[];
}
