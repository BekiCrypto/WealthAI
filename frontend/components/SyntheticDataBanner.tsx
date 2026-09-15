"use client";

/**
 * A visible, honest flag for anything derived from demo/heuristic data
 * rather than measured history -- e.g. the seeded economic calendar, or the
 * surprise-probability/asset-impact heuristics in the prediction engine.
 * Styled as a stamped advisory bulletin (a real weather-service convention:
 * every bulletin is stamped with its confidence class), not a colored
 * border -- impossible to miss without relying on a border-as-alarm trick.
 */
export default function SyntheticDataBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="bulletin">
      <span className="bulletin-stamp">SYNTHETIC</span>
      <span className="bulletin-body">{children}</span>
    </div>
  );
}
