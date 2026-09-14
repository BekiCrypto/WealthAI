"use client";

import { useEffect, useState } from "react";
import { formatCountdown } from "@/lib/format";

export default function EventCountdown({ targetIso }: { targetIso: string }) {
  const [now, setNow] = useState<number | null>(null);

  useEffect(() => {
    setNow(Date.now());
    const id = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(id);
  }, []);

  if (now === null) return <span className="text-dim text-sm">—</span>;
  return <span className="mono text-sm">{formatCountdown(targetIso, now)}</span>;
}
