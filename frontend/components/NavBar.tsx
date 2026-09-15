"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import RankBadge from "@/components/game/RankBadge";

const LINKS = [
  { href: "/", label: "Situation Board" },
  { href: "/events", label: "Advisories" },
  { href: "/learn", label: "Handbook" },
  { href: "/chat", label: "Ask the Forecaster" },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <div className="instrument-rail">
      <div className="instrument-rail-inner page">
        <Link href="/" className="wordmark">
          <svg className="wordmark-mark" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.4" />
            <path d="M12 4.5 13.6 10.4 19.5 12 13.6 13.6 12 19.5 10.4 13.6 4.5 12 10.4 10.4Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
            <circle cx="12" cy="12" r="1.3" fill="currentColor" />
          </svg>
          <span>
            WealthAI<span className="wordmark-sub"> Storm Center</span>
          </span>
        </Link>
        <nav className="instrument-tabs">
          {LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link key={link.href} href={link.href} className={`instrument-tab ${active ? "instrument-tab-active" : ""}`}>
                {link.label}
              </Link>
            );
          })}
        </nav>
        <div className="instrument-rail-badge">
          <RankBadge />
        </div>
      </div>
    </div>
  );
}
