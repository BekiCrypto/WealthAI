import type {
  EconomicEvent,
  EventScenario,
  NewsItem,
  PriceBar,
  ScoreBreakdown,
  TechnicalSnapshot,
  WorldState,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`POST ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  worldState: () => apiGet<WorldState>("/world-state"),
  calendar: (hoursAhead = 24 * 14) => apiGet<EconomicEvent[]>(`/events/calendar?hours_ahead=${hoursAhead}`),
  eventScenario: (id: number) => apiGet<EventScenario>(`/events/${id}/scenario`),
  assetScores: () => apiGet<Record<string, ScoreBreakdown>>("/assets/scores"),
  assetScore: (symbol: string) => apiGet<ScoreBreakdown>(`/assets/${encodeURIComponent(symbol)}/score`),
  assetTechnical: (symbol: string) => apiGet<TechnicalSnapshot>(`/assets/${encodeURIComponent(symbol)}/technical`),
  assetPrices: (symbol: string, limit = 300) =>
    apiGet<PriceBar[]>(`/assets/${encodeURIComponent(symbol)}/prices?limit=${limit}`),
  newsLatest: (limit = 30) => apiGet<NewsItem[]>(`/news/latest?limit=${limit}`),
  chat: (query: string) => apiPost<{ answer: string; used_context: unknown }>("/chat", { query }),
};

export const TRACKED_SYMBOLS = [
  "GC=F",
  "CL=F",
  "DX-Y.NYB",
  "^TNX",
  "^GSPC",
  "EURUSD=X",
  "BTC-USD",
  "ETH-USD",
];

export const SYMBOL_LABELS: Record<string, string> = {
  "GC=F": "Gold",
  "CL=F": "Crude Oil (WTI)",
  "DX-Y.NYB": "US Dollar Index",
  "^TNX": "US 10Y Yield",
  "^GSPC": "S&P 500",
  "EURUSD=X": "EUR/USD",
  "BTC-USD": "Bitcoin",
  "ETH-USD": "Ethereum",
};

// Maps our internal (yfinance-style) symbols to TradingView's symbol format
// for the embedded chart widget.
export const TRADINGVIEW_SYMBOL_MAP: Record<string, string> = {
  "GC=F": "TVC:GOLD",
  "CL=F": "TVC:USOIL",
  "DX-Y.NYB": "TVC:DXY",
  "^TNX": "TVC:US10Y",
  "^GSPC": "TVC:SPX",
  "EURUSD=X": "FX:EURUSD",
  "BTC-USD": "COINBASE:BTCUSD",
  "ETH-USD": "COINBASE:ETHUSD",
};
