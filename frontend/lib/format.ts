export function directionClass(direction: string | undefined | null): string {
  const d = (direction || "").toLowerCase();
  if (["bullish", "risk-on", "uptrend", "elevated:bullish"].includes(d)) return "tag-bullish";
  if (["bearish", "risk-off", "downtrend"].includes(d)) return "tag-bearish";
  if (["neutral", "range_bound", "stable"].includes(d)) return "tag-neutral";
  if (["high", "elevated"].includes(d)) return "tag-warn";
  return "tag-unknown";
}

export function formatCountdown(targetIso: string, nowMs: number): string {
  const target = new Date(targetIso).getTime();
  const diff = target - nowMs;
  const past = diff < 0;
  const abs = Math.abs(diff);
  const hours = Math.floor(abs / 3_600_000);
  const minutes = Math.floor((abs % 3_600_000) / 60_000);
  const label = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
  return past ? `${label} ago` : `in ${label}`;
}

export function formatPercent(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${value.toFixed(digits)}%`;
}

export function formatNumber(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: 0 });
}

/** A storm-category-style conviction tier derived from how far the score
 * leans from neutral and how confident the underlying signals are --
 * "WATCH" (worth monitoring, low conviction) through "WARNING" (strong,
 * high-confidence lean), matching the advisory-bulletin severity language
 * used across the app. */
export function convictionTier(bullishPct: number, confidence: string): { label: string; tagClass: string } {
  const distance = Math.abs(bullishPct - 50);
  const bullish = bullishPct >= 50;
  if (confidence === "High" && distance >= 20) {
    return { label: "Warning", tagClass: bullish ? "tag-bullish" : "tag-bearish" };
  }
  if (confidence !== "Low" && distance >= 10) {
    return { label: "Advisory", tagClass: "tag-warn" };
  }
  return { label: "Watch", tagClass: "tag-neutral" };
}
