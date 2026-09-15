import type { Metadata } from "next";
import NavBar from "@/components/NavBar";
import { GameProvider } from "@/lib/game/GameProvider";
import LevelUpToast from "@/components/game/LevelUpToast";
import { spaceGrotesk, spaceMono, plusJakarta } from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "WealthAI — Market Intelligence",
  description: "A live storm-warning center for markets: tracked systems, advisories and forecast cones instead of bare buy/sell calls.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${spaceMono.variable} ${plusJakarta.variable}`}>
      <body>
        <GameProvider>
          <NavBar />
          <main className="page">{children}</main>
          <LevelUpToast />
        </GameProvider>
      </body>
    </html>
  );
}
