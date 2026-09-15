"use client";

type Mastery = "not_started" | "briefed" | "certified";

export function stationMastery(read: boolean, certified: boolean): Mastery {
  if (certified) return "certified";
  if (read) return "briefed";
  return "not_started";
}

const MASTERY_LABEL: Record<Mastery, string> = {
  not_started: "Not started",
  briefed: "Briefed",
  certified: "Certified",
};

const MASTERY_CLASS: Record<Mastery, string> = {
  not_started: "tag-neutral",
  briefed: "tag-warn",
  certified: "tag-bullish",
};

export default function StationCard({
  name,
  category,
  mastery,
  bestScore,
  active,
  onSelect,
}: {
  name: string;
  category: string;
  mastery: Mastery;
  bestScore: number | null;
  active: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className="panel card-link tracked-system-card"
      style={{
        textAlign: "left",
        cursor: "pointer",
        borderColor: active ? "var(--pressure-bright)" : undefined,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10 }}>
        <div>
          <h3 style={{ fontSize: 15 }}>{name}</h3>
          <span className="text-dim text-sm" style={{ textTransform: "capitalize" }}>
            {category.replace(/_/g, " ")}
          </span>
        </div>
        <span className={`tag ${MASTERY_CLASS[mastery]}`}>{MASTERY_LABEL[mastery]}</span>
      </div>
      {bestScore !== null && (
        <div className="text-sm text-dim mono" style={{ marginTop: 10 }}>
          Best score {Math.round(bestScore * 100)}%
        </div>
      )}
    </button>
  );
}
