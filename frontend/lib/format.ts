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
