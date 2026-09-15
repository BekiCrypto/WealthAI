"use client";

/**
 * A visible, honest flag for anything derived from demo/heuristic data
 * rather than measured history -- e.g. the seeded economic calendar, or the
 * surprise-probability/asset-impact heuristics in the prediction engine.
 * Red-ruled by design: this should be impossible to miss or mistake for a
 * calibrated result.
 */
export default function SyntheticDataBanner({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        borderLeft: "3px solid var(--shock)",
        background: "rgba(179, 69, 63, 0.08)",
        borderRadius: 8,
        padding: "10px 14px",
        display: "flex",
        gap: 10,
        alignItems: "flex-start",
      }}
      className="text-sm"
    >
      <span style={{ color: "var(--shock)", fontWeight: 700 }}>Synthetic</span>
      <span className="text-dim">{children}</span>
    </div>
  );
}
