"use client";

/**
 * A real instrument dial (270° arc, like a barometer) reading an actual
 * probability/confidence value -- not a decorative ring standing in for
 * content the page should show instead; the number and label are the
 * content, the arc is how a forecast desk would read it at a glance.
 */
export default function PressureGauge({
  value,
  color,
  label,
  size = 92,
}: {
  value: number; // 0-100
  color: string;
  label: string;
  size?: number;
}) {
  const clamped = Math.max(0, Math.min(100, value));
  const arcFraction = 0.75; // 270 degrees of the ring is drawn
  const strokeWidth = size * 0.09;
  const radius = size / 2 - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const arcLength = circumference * arcFraction;
  const gapLength = circumference - arcLength;
  const filled = (clamped / 100) * arcLength;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: "rotate(135deg)" }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--bg-panel-alt)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={`${arcLength} ${gapLength}`}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={`${filled} ${circumference - filled}`}
          style={{ transition: "stroke-dasharray 400ms cubic-bezier(0.16, 1, 0.3, 1)" }}
        />
      </svg>
      <div style={{ marginTop: -size * 0.62, display: "flex", flexDirection: "column", alignItems: "center", overflow: "hidden" }}>
        <span key={Math.round(clamped)} className="mono digit-roll" style={{ fontSize: size * 0.24, fontWeight: 700, color }}>
          {Math.round(clamped)}%
        </span>
      </div>
      <span className="text-dim mono" style={{ fontSize: 10, letterSpacing: "0.06em", marginTop: -2 }}>
        {label.toUpperCase()}
      </span>
    </div>
  );
}
