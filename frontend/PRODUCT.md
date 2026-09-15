# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Retail and prosumer traders, plus macro-curious individuals who are not
professional analysts, who currently piece together market context by hand
across TradingView, financial Twitter/news, and scattered economic
calendars. They arrive wanting to understand *why* markets are moving or
about to move, not just receive a bare buy/sell signal. They check in
around scheduled economic releases (CPI, NFP, FOMC, etc.) and periodically
throughout the day/week to gauge the macro regime and specific asset setups.

## Product Purpose

WealthAI is a live global market intelligence app. It continuously ingests
economic data, central-bank decisions, geopolitical events, news sentiment,
and market prices, then connects them into a single narrative per asset:
what happened, why it matters, what the market expects, what might happen
next, how confident the system is, and what would prove it wrong. Success
means a user leaves understanding the mechanism behind a market move or
setup, not just a directional call they have to trust blindly.

## Positioning

Unlike black-box "BTC will go up" signal tools, WealthAI always shows its
reasoning chain (macro regime -> technical structure -> sentiment ->
geopolitical risk), states a confidence level and an explicit invalidation
condition for every call, and distinguishes confirmed facts from
expectations, heuristics, and rumor. Nothing is presented as more certain
than it is: demo/seeded data and hand-picked (not yet statistically
calibrated) heuristic relationships are visibly flagged rather than passed
off as measured fact. Education is load-bearing, not a side feature -- an
indicator glossary and inline briefings teach the underlying mechanism
(including counter-intuitive cases like inverted indicators) alongside
every score and setup, so a user can eventually evaluate the app's calls
rather than only trust them.

## Operating Context

Core workflows: checking the live World State (macro regime) and
per-asset Intelligence Scores on the dashboard; drilling into an upcoming
economic event's pre-release scenario (likely range, surprise
probabilities, expected asset reaction) and, post-release, its outcome
band; opening an asset's detail page for its technical snapshot,
Intelligence Score breakdown, and Trade Setup (bias, entry, stop, staged
TP1/TP2/TP3 targets, timeframe); asking the AI assistant free-text
questions grounded in live data; and learning the indicators themselves in
the Learning Center. Data refreshes continuously via a background
scheduler (prices every 5 min, news every 10 min, geopolitical every 15
min, world state every 5 min); users may check in mid-session and expect
numbers to have moved.

## Capabilities and Constraints

- **No licensed market-data feed.** Equities/commodities/FX/rates prices
  come from `yfinance` (scraped, not licensed for redistribution) and are
  used only to compute derived analysis; raw prices/OHLCV for these
  symbols are withheld from the API and UI, replaced by percentage
  distances, ratios, and categorical reads (trend, RSI, confidence). Crypto
  (BTC-USD, ETH-USD) comes from Coinbase's public exchange API and *is*
  licensed for display, so raw prices show normally. This licensing gate is
  a hard legal constraint any redesign must preserve, including for new
  gamification/UI surfaces -- never invent a way to display a withheld
  price.
- **Daily-bar technical analysis only.** No intraday or weekly timeframe
  exists yet; every Trade Setup states "Swing (daily chart)" explicitly.
- **No backend user accounts or authentication exist.** Any per-user state
  (gamification progress, XP, streaks, quiz results, achievements) must be
  implemented as client-side persisted state (e.g. localStorage), not a
  server-side user record, until an account system is built.
- **Demo-grade and heuristic data is explicitly flagged, never silently
  presented as fact.** The economic calendar is currently seeded/synthetic
  (`source: "seed"`); the prediction engine's surprise-probability and
  asset-impact tables are hand-picked heuristics (`basis: "heuristic"`).
  Both carry a visible "Synthetic" disclosure in the UI. A redesign must
  keep these disclosures at least as visible as today, not decorate them
  away.
- **Stack:** Next.js (App Router) / React / TypeScript frontend; FastAPI /
  Python backend (separate repo folder, not touched by frontend-only
  design work) with SQLAlchemy models over Postgres (SQLite in local dev).
  TradingView's embeddable widget is used for live charts and is
  independent of the licensing gate above (it is TradingView's own
  authorized data, not WealthAI's).
- **Existing content system a redesign must carry forward faithfully:**
  the intelligence-score reasoning chain (macro/technical/sentiment/
  geopolitical), the outcome-band diverging surprise visualization
  (dovish<->hawkish, with an `inverted` flag for indicators like the
  unemployment rate), the Trade Setup structure (bias, entry, SL,
  TP1/TP2/TP3 with R-multiples, timeframe), and the indicator glossary's
  six-part briefings (what it is / why it matters / market impact chain /
  how to read it / historical context / watch for).

## Evidence on Hand

Real, live data: current price bars (yfinance for non-crypto, Coinbase for
crypto), real RSS news headlines, real GDELT-sourced geopolitical
headlines, and a real FastAPI backend computing real technical indicators
and intelligence scores against that data. Synthetic/demo data, clearly
flagged in-product: the 8-event seeded economic calendar and the
prediction engine's heuristic probability/impact tables (not yet backed by
a measured historical-reaction dataset -- that backtest pipeline is future
work). No user testimonials, case studies, pricing, or customer logos exist
or should be invented.

## Product Principles

1. **Show the reasoning, not just the verdict.** Every score, band, and
   setup carries its "why" and an explicit invalidation condition.
2. **Never overstate certainty.** Demo data, heuristic (not calibrated)
   relationships, and licensing-withheld prices are always visibly flagged,
   never smoothed over for a cleaner-looking surface.
3. **Teach the mechanism, not just the call.** Education is a first-class
   product surface, not documentation bolted on the side.
4. **Preserve functional color/structure meaning.** Bullish/bearish,
   hawkish/dovish (amber/teal), and redistributable-vs-withheld are
   information the user relies on; any visual refresh keeps these
   distinctions legible even while changing their rendition.
5. **Respect the licensing boundary structurally, not cosmetically.** The
   redistribution gate is enforced in the data layer already; new UI must
   never work around it to "look more complete."

## Accessibility & Inclusion

No formal accessibility standard has been confirmed as a target; treat
WCAG 2.2 AA as the working default for a data-dense financial tool (color
is never the sole signal, given how much of this product's meaning lives
in bullish/bearish and hawkish/dovish color coding).
