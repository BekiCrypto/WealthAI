---
name: WealthAI — Storm Warning
description: A live meteorological forecast console for markets, where every asset is a tracked system and confidence is a forecast-cone width, not a bare percentage.
colors:
  bg: "#0a0f16"
  bg-panel: "#10161f"
  bg-panel-alt: "#161e29"
  bg-raised: "#1b2430"
  border: "#232e3b"
  border-strong: "#33404f"
  text: "#e9eef3"
  text-dim: "#8b98a8"
  text-faint: "#5a6675"
  pressure: "#0f4c56"
  pressure-bright: "#3ecad9"
  pressure-dim: "#1a3a42"
  bullish: "#35d0a0"
  bearish: "#f2543d"
  hawkish: "#e0a83e"
  dovish: "#38b6d6"
  neutral: "#7c8a9a"
  severe: "#c81e3a"
typography:
  display:
    fontFamily: "var(--font-display-raw), Space Grotesk, ui-sans-serif, system-ui, sans-serif"
    fontWeight: 700
    letterSpacing: "-0.01em"
  mono:
    fontFamily: "var(--font-mono-raw), Space Mono, ui-monospace, SF Mono, Menlo, monospace"
    fontFeature: "font-variant-numeric: tabular-nums"
  body:
    fontFamily: "var(--font-body-raw), Plus Jakarta Sans, ui-sans-serif, system-ui, sans-serif"
    fontWeight: 400
rounded:
  sm: "6px"
  md: "10px"
  pill: "999px"
spacing:
  panel-padding: "20px 22px"
  page-padding: "28px 20px 72px"
  grid-gap: "16px"
components:
  button-primary:
    backgroundColor: "{colors.pressure-bright}"
    textColor: "#04141a"
    typography: "{typography.display}"
    rounded: "{rounded.sm}"
    padding: "11px 18px"
  tag-bullish:
    backgroundColor: "{colors.bullish}"
    textColor: "{colors.bullish}"
    typography: "{typography.mono}"
    rounded: "{rounded.pill}"
    padding: "5px 11px"
  tag-bearish:
    backgroundColor: "{colors.bearish}"
    textColor: "{colors.bearish}"
    typography: "{typography.mono}"
    rounded: "{rounded.pill}"
    padding: "5px 11px"
  panel:
    backgroundColor: "{colors.bg-panel}"
    rounded: "{rounded.md}"
    padding: "{spacing.panel-padding}"
---

# Design System: WealthAI — Storm Warning

## Overview

**Creative North Star: "The Storm Warning Desk"**

WealthAI reads the market like a forecast-center meteorologist reads the atmosphere: every asset is a tracked system, every economic release is an advisory, and confidence is expressed as a forecast-cone width or an instrument-dial reading, never a bare percentage sitting alone. The world is a deep storm-slate situation board — cold blue-grey near-black, not a navy-purple "dark fintech" default — lit by one saturated pressure-teal that functions as the desk's own structural accent (rails, borders, active state, chart lines), not a decorative sprinkle. This was a deliberate refusal of the category-default trading-dashboard skin: WealthAI's positioning is showing its reasoning chain and never overstating certainty, and the visual world materializes that as an actual severity-tiered advisory language — bullish/bearish and hawkish/dovish read as weather-service colors (all-clear teal-green, warning red-orange, advisory amber, the pressure-teal family), with one reserved saturated crimson for the single most severe tier (shock-level geopolitical risk), rather than flat red/green.

Data readouts are teletype-bulletin material (Space Mono, tabular numerals) because the product's honesty commitments — visible "Synthetic" flags, explicit confidence levels, explicit invalidation conditions — read better as instrument print than as decorative UI chrome. Headlines carry scientific-instrument heritage (Space Grotesk) with no eyebrow/kicker label ever placed above them; the heading itself, not a small caps tag floating over it, carries the hierarchy.

**Key Characteristics:**
- Deep storm-slate ground with one dominant structural accent (pressure-teal), not a multi-accent palette.
- Advisory-severity color language stands in for bullish/bearish/hawkish/dovish, with a single reserved crimson for the most severe tier only.
- Space Grotesk (display) / Space Mono (data and bulletin body) / Plus Jakarta Sans (UI prose) — a three-role type stack, each role used for its heritage, not decoratively.
- Real instrument components (forecast-cone SVG, 270° pressure-gauge dial, labeled trajectory sparklines) replace flat bars, bare percentages, and decorative charts.
- No eyebrows/kickers, no colored-border alerts, no bare sparklines — each banned in favor of a load-bearing alternative documented below.

## Colors

Nearly monochrome storm-slate at rest, broken only by the pressure-teal structural accent and the advisory-severity language carrying all functional meaning.

### Primary
- **Pressure Teal** (`--pressure-bright` `#3ecad9`): the one saturated accent, committed to carrying 40-50% of any surface at page scale — chart lines, active nav tab, focus rings, gauge fill, buttons, selection color. Never scattered as a decorative highlight elsewhere.
- **Pressure Teal, deep** (`--pressure` `#0f4c56`) / **Pressure Teal, dim** (`--pressure-dim` `#1a3a42`): the same hue pulled down for structural fills (instrument-rail bottom glow, hover border) where the bright value would be too loud.

### Secondary — Advisory-Severity Language
This is the product's functional color system, not decoration — it carries bullish/bearish and hawkish/dovish meaning end to end.
- **All-Clear Teal-Green** (`--bullish` `#35d0a0`): bullish bias, positive conviction.
- **Warning Red-Orange** (`--bearish` `#f2543d`): bearish bias, stop levels, invalidation.
- **Advisory Amber** (`--hawkish` `#e0a83e`): hawkish policy lean; also aliased as `--warn`.
- **Dovish Teal** (`--dovish` `#38b6d6`): dovish policy lean, kept in the pressure-teal family rather than a separate hue.
- **Reserved Crimson** (`--severe` `#c81e3a`): the single most severe tier only — shock-level geopolitical risk and the bulletin stamp on synthetic-data disclosures. Never used for ordinary bearish/warning states; diluting it to a general "danger" color would erase the one true top-severity signal.

### Neutral
- **Storm Ground** (`--bg` `#0a0f16`): page background.
- **Panel** (`--bg-panel` `#10161f`) / **Panel Alt** (`--bg-panel-alt` `#161e29`) / **Raised** (`--bg-raised` `#1b2430`): stacked surface layers, each one step lighter — panels, nested cards, the level-up toast strip.
- **Border** (`--border` `#232e3b`) / **Border Strong** (`--border-strong` `#33404f`): hairline dividers and hover/active borders.
- **Text** (`--text` `#e9eef3`), **Text Dim** (`--text-dim` `#8b98a8`), **Text Faint** (`--text-faint` `#5a6675`): a three-step reading hierarchy over the dark ground.

### Named Rules
**The Severity-Not-Decoration Rule.** Every functional color (bullish/bearish/hawkish/dovish/severe) maps to a specific product meaning defined in PRODUCT.md and must never be reassigned to a purely decorative role. `--severe` in particular renders only the single most severe tier — it is not a generic "alert red."

**The One Accent Rule.** Pressure-teal is the only saturated non-functional accent. New UI reaches for the neutral/border scale before introducing a second decorative hue.

## Typography

**Display Font:** Space Grotesk (with ui-sans-serif, system-ui, sans-serif fallback)
**Body Font:** Plus Jakarta Sans (with ui-sans-serif, system-ui, sans-serif fallback)
**Label/Mono Font:** Space Mono (with ui-monospace, SF Mono, Menlo, monospace fallback), `font-variant-numeric: tabular-nums`

**Character:** Space Grotesk's scientific-instrument heritage (drawn for ESA identity work) carries headlines and buttons; Space Mono's teletype-bulletin heritage carries every instrument readout, advisory bulletin body, and tabular data so numbers read like a wire print, not a UI label; Plus Jakarta Sans stays unobtrusive for prose so it never competes with the two characterful faces. All three are loaded via `next/font/google` and composed into public `--font-display` / `--font-mono` / `--font-body` tokens from private `*-raw` variables — a deliberate split (documented inline in `app/globals.css`) to avoid a circular custom-property reference.

### Hierarchy
- **Display / Headline** (700, `h1`-`h3` cascade, `letter-spacing: -0.01em`): page and section titles (`Situation Board`, `Advisory Schedule`, `Plotted Track`). Carries its own visual weight with no eyebrow/kicker above it.
- **Body** (400-600, Plus Jakarta Sans, browser default sizes as used): descriptive prose — reasoning, invalidation, risk copy.
- **Data/Label** (400-700, Space Mono, 10-14px, tabular numerals): every instrument readout (gauge percentages, trajectory deltas, table cells, nav tabs, tags, rank insignia, advisory bulletin body).

### Named Rules
**The Single-Size Bulletin Rule.** Advisory bulletin body text (`.bulletin-body`) never resizes for hierarchy — one size, ranked only by weight and case, matching real NOAA teletype bulletins. Do not introduce a second bulletin-body size to fake emphasis.

**The No-Kicker Rule.** No eyebrow/kicker label ever sits above a page heading. The old `.section-title` pattern was removed app-wide; this is an established convention, not an oversight — headings carry weight through `h1`-`h3`/`.heading-block` alone.

## Layout

A single constrained `.page` container (`max-width: 1240px`, `padding: 28px 20px 72px`, narrowing to `20px 16px 56px` under 560px) holds every route. Panels (`.panel`) are the base spatial unit — `20px 22px` padding, `10px` radius, 1px border — arranged in a `.grid` with a flat `16px` gap. `.grid-cols-4` collapses to 2 columns under 900px and to 1 column under 560px; `.grid-cols-2` collapses to 1 column under 560px. `.panel` always sets `min-width: 0` and `html`/`body` carry `overflow-x: hidden` as a hard backstop, specifically so a wide child (a data table, a wide chart) can never propagate its min-content width up through a flex/grid ancestor and widen the page past the viewport; any new wide content must sit inside a `.table-scroll`-style container (`overflow-x: auto` on the wrapper, an explicit `min-width` on the scrolling child) rather than being left bare.

### Named Rules
**The Contained-Overflow Rule.** Wide content never overflows the page horizontally; it scrolls inside its own explicitly-sized container. This is enforced at three layers (`.panel` min-width: 0, `body` overflow-x: hidden, `.table-scroll` opt-in), not left to chance on any single one.

## Elevation & Depth

Flat by default — panels are distinguished by layered background steps (`--bg` → `--bg-panel` → `--bg-panel-alt` → `--bg-raised`) and 1px borders, not shadows. The two shadows that do exist are both functional, not ambient decoration: the instrument rail's `backdrop-filter: blur(10px)` + translucent background for a sticky-header read-through effect, and the level-up toast's upward shadow (`0 -8px 24px -8px rgba(0,0,0,0.5)`) separating the fixed bottom strip from page content beneath it.

### Shadow Vocabulary
- **Rail glow** (`box-shadow: inset 0 -1px 0 0 color-mix(in srgb, var(--pressure) 40%, transparent)`): the sticky instrument rail's bottom edge, tying it to the structural accent.
- **Toast lift** (`box-shadow: 0 -8px 24px -8px rgba(0,0,0,0.5)`): separates the bottom-pinned level-up toast from the page.

### Named Rules
**The Layered-Not-Lifted Rule.** Depth comes from stepped background tone (four steps: ground → panel → panel-alt → raised) plus borders, not drop shadows. A new component reaches for the next background step before reaching for a shadow.

## Shapes

Two radius steps: `--radius-sm` (6px, buttons/inputs/tags-as-rectangles) and `--radius` (10px, panels/bulletins). Fully round (`999px`) is reserved for pill shapes — tags, progress tracks, the rank badge, scrollbar thumb. Borders are uniform 1px hairlines (`--border`) that strengthen to `--border-strong` only on hover/active states; there is no colored-border-as-alert pattern anywhere in the system (see Do's and Don'ts).

## Components

### Buttons
- **Shape:** 6px radius (`--radius-sm`).
- **Primary:** `--pressure-bright` background, near-black text (`#04141a`) for contrast, Space Grotesk 700, `11px 18px` padding.
- **Hover / Focus:** hover brightens via `filter: brightness(1.08)`; active nudges `translateY(1px)`; disabled drops to `opacity: 0.45`. Focus-visible everywhere gets a 2px `--pressure-bright` outline with 2px offset (themed, not browser default).

### Chips / Tags
- **Style:** pill-shaped (`999px`), Space Mono, 12px, `1px` border, `--bg-panel-alt` background at rest. `flex-shrink: 0` is set on every tag so a flex row wraps whole chips instead of squeezing one and mid-word-clipping its text.
- **State:** severity variants (`.tag-bullish`, `.tag-bearish`, `.tag-warn`, `.tag-severe`, `.tag-neutral`) tint border/background/text from the matching advisory color via `color-mix`. Long-text chips (ChatPanel's suggestion chips) explicitly override to `white-space: normal` to wrap their own content instead of compressing or forcing page overflow — the convention is short data pills never compress, long-text chips wrap.

### Cards / Containers
- **Corner Style:** 10px radius.
- **Background:** `--bg-panel`, 1px `--border`.
- **Shadow Strategy:** none at rest (see Elevation & Depth); `.card-link` hover lifts with `border-color: var(--pressure-dim)` + `translateY(-1px)`, not a shadow.
- **Internal Padding:** `20px 22px`.

### Inputs / Fields
- **Style:** `--bg-panel-alt` background, 1px `--border`, 6px radius.
- **Focus:** border shifts to `--pressure-bright`.

### Navigation
- **Instrument Rail** (`NavBar.tsx`): sticky top bar, translucent `--bg-panel` + blur, a bottom inset glow in the structural accent. Wordmark is a custom SVG compass-rose mark (not a glyph icon or emoji) plus "WealthAI / Storm Center" text. Nav tabs are Space Mono, 12px, lowercase-weight — active tab gets `--pressure-bright` text and a tinted background/border; inactive tabs are `--text-dim` until hover. On narrow viewports the tab row wraps to its own line and the rank badge moves to a full-width row below.

### ForecastCone (signature)
The hero visualization for an economic-event scenario (`components/ForecastCone.tsx`): a nested-Gaussian pressure-contour SVG (three stacked bands at decreasing sigma) replacing a flat probability strip, so outcomes near consensus read as visibly more probable than tail outcomes. Horizontal position is policy-adjusted (`effective_z`), so a hawkish surprise always renders right/amber and a dovish one always renders left/teal — correct even for inverted series like the unemployment rate. AI estimate and actual print are marked as distinct glyphs on the same axis, each carrying a native `<title>` tooltip.

### PressureGauge (signature)
A real 270° instrument-dial SVG (`components/PressureGauge.tsx`) used everywhere a probability or confidence percentage appears (score cards, trade setups) — never a bare tag or plain percentage text. The percentage span remounts on a `key={value}` change, driving the `.digit-roll` keyframe (translateY + opacity, 260ms, respects `prefers-reduced-motion`) so a refreshed instrument reading rolls rather than silently swapping.

### MiniTrajectory (signature)
A labeled sparkline (`components/MiniTrajectory.tsx`): a polyline of an asset's Intelligence Score conviction history, always paired with explicit delta + range text in mono. The system bans a sparkline "standing in for content" — this pairing rule is load-bearing, not optional, and any future mini-chart should follow it.

### Advisory Bulletin
The stamped-tag pattern (`.bulletin` / `.bulletin-stamp` / `.bulletin-body`, used by `SyntheticDataBanner`): a normal-bordered panel with a small stamped tag (e.g. "SYNTHETIC") plus mono body copy, not a colored border-left/right. This directly serves PRODUCT.md's constraint that demo/heuristic data must be visibly flagged, never smoothed away — the stamp reads as a weather-service confidence-class stamp, not a UI alert border.

### Rank Badge / Level-Up Toast (gamification)
`RankBadge.tsx` is a persistent pill in the instrument rail showing rank insignia, title, and an XP progress track. `LevelUpToast.tsx` is a full-width strip pinned to the bottom viewport edge (`position: fixed`, slide/fade in), deliberately not a floating corner card: a strip pinned to one edge has a small, predictable collision footprint against arbitrary page content, where a card sized to be readable can land over any element on a content-dense page. Because it is `position: fixed`, it always tracks the current viewport rather than a document position — verified via `getBoundingClientRect()` at multiple scroll offsets; a Playwright fullPage screenshot appearing to show it "mid-document" is a known capture artifact (fullPage stitching pastes fixed elements once at their viewport offset into the tall composite image), not a real positioning defect, and should not be re-flagged as one.

## Do's and Don'ts

### Do:
- **Do** keep pressure-teal as the only saturated non-functional accent, carrying 40-50% of any surface via structural elements (borders, active states, chart lines), never as scattered decoration.
- **Do** pair every sparkline/trend line with an explicit numeric label (delta + range), per MiniTrajectory.
- **Do** route wide content (tables, wide charts) through a `.table-scroll`-style container with its own `overflow-x: auto` and an explicit `min-width` on the scrolling child.
- **Do** keep short data tags `white-space: nowrap` + `flex-shrink: 0`; only long free-text chips override to wrap.
- **Do** flag synthetic/heuristic data with the stamped bulletin pattern, at least as visibly as today, per PRODUCT.md's certainty constraints.

### Don't:
- **Don't** place an eyebrow/kicker label above a page heading — the pattern was removed app-wide; headings carry their own weight.
- **Don't** use a colored border-left/right as an alert or disclosure device — the stamped bulletin tag replaced that pattern; a colored side-border is not part of this system.
- **Don't** reassign `--severe` (crimson) to ordinary bearish/warning states — it is reserved for the single most severe tier only.
- **Don't** ship a bare sparkline with no accompanying numeric label — sparklines are data readouts here, not decoration.
- **Don't** introduce a second decorative accent hue alongside pressure-teal; reach for the neutral/border scale first.

