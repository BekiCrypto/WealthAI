"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/events", label: "Calendar" },
  { href: "/chat", label: "Ask AI" },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <div
      style={{
        borderBottom: "1px solid var(--border)",
        background: "var(--bg-panel)",
        position: "sticky",
        top: 0,
        zIndex: 10,
      }}
    >
      <div
        className="page"
        style={{ paddingTop: 14, paddingBottom: 14, display: "flex", alignItems: "center", gap: 28 }}
      >
        <Link href="/" style={{ fontWeight: 700, fontSize: 16, letterSpacing: "0.02em" }}>
          WealthAI <span style={{ color: "var(--text-dim)", fontWeight: 400 }}>Market Intelligence</span>
        </Link>
        <nav style={{ display: "flex", gap: 18 }}>
          {LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm"
                style={{
                  color: active ? "var(--accent)" : "var(--text-dim)",
                  fontWeight: active ? 600 : 400,
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
