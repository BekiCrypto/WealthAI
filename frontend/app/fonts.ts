import { Space_Grotesk, Space_Mono, Plus_Jakarta_Sans } from "next/font/google";

// Display: Space Grotesk was drawn for the European Space Agency's identity
// work -- a scientific-instrument heritage that fits a forecast console
// directly, not a generic "clean sans" pick.
export const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display-raw",
  display: "swap",
});

// Data/instrument readouts and advisory-bulletin body: teletype-bulletin
// heritage -- real NOAA/NWS advisories were wire-printed on fixed-width
// machines. Used here for measurement and data, never as a "technical"
// costume.
export const spaceMono = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-mono-raw",
  display: "swap",
});

// UI/body prose: unobtrusive against the bold display + mono pairing.
export const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body-raw",
  display: "swap",
});
