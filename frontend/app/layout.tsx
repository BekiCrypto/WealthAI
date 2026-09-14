import type { Metadata } from "next";
import NavBar from "@/components/NavBar";
import "./globals.css";

export const metadata: Metadata = {
  title: "WealthAI — Market Intelligence",
  description: "Live global market intelligence: what happened, why it matters, what might happen next.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <NavBar />
        <main className="page">{children}</main>
      </body>
    </html>
  );
}
