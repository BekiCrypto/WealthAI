export interface EconomicEvent {
  id: number;
  name: string;
  country: string;
  category: string;
  importance: "low" | "medium" | "high";
  scheduled_at: string;
  previous: number | null;
  consensus: number | null;
  ai_estimate: number | null;
  ai_estimate_low: number | null;
  ai_estimate_high: number | null;
  prob_upside_surprise: number | null;
  prob_downside_surprise: number | null;
  prob_inline: number | null;
  actual: number | null;
  surprise: number | null;
  unit: string;
  status: "scheduled" | "released";
  source: string;
}

export interface ScoreBreakdown {
  symbol: string;
  bullish_pct: number;
  confidence: "Low" | "Medium" | "High";
  macro: string;
  technical: string;
  sentiment: string;
  geopolitical: string;
  reasons: string[];
}

export interface WorldStateRegime {
  risk_regime: string;
  inflation: string;
  usd: string;
  yields: string;
  oil: string;
  gold: string;
  equities: string;
  crypto: string;
  geopolitical_risk: string;
  geopolitical_risk_score: number;
  updated_at: string;
}

export interface WorldState {
  created_at: string;
  regime: WorldStateRegime;
  scores: Record<string, ScoreBreakdown>;
  reasoning: Record<string, string>;
}

export interface TechnicalSnapshot {
  symbol: string;
  redistributable: boolean;
  price_disclosure: string | null;
  last_price: number | null;
  trend: string;
  rsi_14: number | null;
  sma_20: number | null;
  sma_50: number | null;
  sma_200: number | null;
  ema_20: number | null;
  atr_14: number | null;
  support: number | null;
  resistance: number | null;
  volatility_20d: number | null;
}

export interface NewsItem {
  id: number;
  source: string;
  title: string;
  url: string;
  published_at: string;
  tags: string;
  sentiment: number;
  fact_tier: string;
}

export interface PriceBar {
  ts: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface IndicatorEducation {
  name: string;
  category: string;
  what_it_is: string;
  why_it_matters: string;
  market_impact_chain: string;
  how_to_read: string;
  historical_context: string;
  watch_for: string;
  inverted: boolean;
}

export interface OutcomeBand {
  unit: string;
  previous: number | null;
  consensus: number | null;
  low: number | null;
  high: number | null;
  ai_estimate: number | null;
  ai_estimate_z: number | null;
  ai_estimate_effective_z: number | null;
  effective_range: [number, number] | null;
  actual: number | null;
  actual_z: number | null;
  effective_z: number | null;
  magnitude: "big" | "moderate" | "small" | null;
  policy_lean: "hawkish" | "dovish" | "neutral" | null;
  inverted: boolean;
  basis: string;
  disclosure: string;
}

export interface EventScenario {
  event: string;
  country: string;
  scheduled_at: string;
  consensus: number | null;
  ai_estimate: number | null;
  likely_range: [number | null, number | null];
  probabilities: { hot: number | null; cool: number | null; in_line: number | null };
  outcome_band: OutcomeBand;
  basis: string;
  disclosure: string;
  education: IndicatorEducation;
  scenarios: Record<string, { description: string; asset_impact: Record<string, string> }>;
}
