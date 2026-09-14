# WealthAI — Live Global Market Intelligence

WealthAI watches economic data, central-bank decisions, geopolitical events, news
sentiment and market prices, then connects them for the user:

**What happened → why it matters → what the market expects → what might happen
next → how confident the AI is → what would prove it wrong.**

It is explicitly an *intelligence and decision-support* system, not a "BTC will
go up" oracle: every score comes with its reasoning, a confidence level, and an
invalidation condition.

## Status

This is a working v1 built end-to-end and verified against live data (real
price ingestion, real RSS news, a demo economic calendar, a live TradingView
chart, and a functioning chat endpoint). It intentionally uses free/keyless
data sources with graceful degradation everywhere a production deployment
would plug in a licensed feed — see [Data sources](#data-sources-and-what-a-production-version-would-change) below.

## Architecture

```
frontend/   Next.js (App Router) dashboard, calendar, asset pages, AI chat
backend/    FastAPI: ingestion -> analysis -> scoring -> prediction -> API
  app/services/ingestion/   market data (yfinance), news (RSS), geopolitical
                             events (GDELT), economic calendar (seed + FRED)
  app/services/analysis/    technical indicators, macro brain (world state),
                             intelligence score, prediction engine
  app/services/llm/         Claude-backed chat grounded in live DB state
  app/scheduler.py          APScheduler jobs refreshing each source on its
                             own interval and persisting World State snapshots
postgres/redis   via docker-compose (Redis is provisioned for future
                 caching/pub-sub; nothing reads/writes it yet -- see Roadmap)
```

Each spec step maps to a concrete module:

| Spec step | Where |
|---|---|
| 1. Collect information | `app/services/ingestion/*` |
| 2. Verify & organize (facts vs expectations vs rumor) | `NewsItem.fact_tier`, `EconomicEvent` lifecycle |
| 3. Macro Brain (relationships, checked against current regime) | `app/services/analysis/macro_brain.py` |
| 4. Predict before releases | `app/services/analysis/prediction_engine.py::generate_pre_event_scenario` |
| 5. React after release | `prediction_engine.py::record_post_release_reaction` |
| 6. Technical analysis fused with macro | `app/services/analysis/technical.py` + `intelligence_score.py` |
| 7. Intelligence Score with reasons | `intelligence_score.py`, `/api/assets/{symbol}/score` |
| 8. Live World State | `macro_brain.py::classify_world_state`, `WorldStateSnapshot` |
| 9. Ask the AI | `app/services/llm/assistant.py`, `/api/chat` |
| 10. Learn from every prediction | `Prediction` / `PredictionOutcome` models, `calibration_stats` |

## Getting started

### Docker (recommended)

```bash
cp backend/.env.example backend/.env   # add ANTHROPIC_API_KEY etc. if you have them
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

### Manual dev setup

**Backend**

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env     # defaults to a local Postgres; swap DATABASE_URL for
                          # sqlite:///dev.db if you just want to try it quickly
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

> Dev-mode note: in this project's sandbox, `next dev` (Turbopack) had an HMR
> websocket handshake failure that silently prevented client-side hydration
> (chunks loaded, no console errors, but React never took over). `npm run
> build && npm run start` was unaffected and is what Docker actually runs. If
> you ever see a dashboard stuck on "Loading live market intelligence…" with
> no errors in a dev environment, try a production build before assuming the
> app is broken.

### Tests

```bash
cd backend && pytest
```

Covers the technical-analysis math (RSI bounds, trend classification, support/
resistance) with synthetic price series — no network or DB required.

## API overview

All endpoints are under `/api` (see `/docs` for full schemas):

- `GET /world-state` — current regime + all intelligence scores + reasoning
- `GET /assets/{symbol}/score` / `/technical` / `/prices`
- `GET /events/calendar`, `GET /events/{id}/scenario`, `GET /events/{id}/reaction`
- `GET /predictions`, `POST /predictions`, `GET /predictions/calibration`
- `GET /news/latest`
- `POST /chat` — `{ "query": "..." }`

## Data sources (and what a production version would change)

| Need | This build uses | Production would use |
|---|---|---|
| Market prices | `yfinance` (free) | Licensed feed (Polygon, Tiingo, Refinitiv) |
| Economic calendar + consensus | Seeded demo calendar; actuals backfilled from FRED if `FRED_API_KEY` is set | TradingEconomics / Investing.com licensed calendar |
| News | Public RSS feeds, naive lexicon sentiment | Licensed news API + a real sentiment/NLP model (FinBERT etc.) |
| Geopolitical events | GDELT DOC 2.0 API (article search), Goldstein scale *approximated* from our own tone lexicon | Full GDELT Events table, or a licensed geopolitical risk feed |
| LLM | Claude via `ANTHROPIC_API_KEY`; falls back to a deterministic data summary if unset | Same, likely with a larger/curated context window and RAG over historical analysis |

Every ingestion function fails soft: a dead API or rate limit is logged and
skipped rather than crashing the scheduler or the request.

## Roadmap

- Redis is provisioned but unused — candidate for caching hot endpoints
  (`/world-state`, `/assets/scores`) and later a pub/sub bridge to
  websocket-push the frontend instead of polling.
- Kafka for event streaming once ingestion volume justifies it (per the
  original tech plan: Redis first, Kafka later).
- Replace the heuristic pre-release estimate (`economic_calendar.py::_estimate_probabilities`)
  with a model calibrated against `PredictionOutcome` history once enough
  predictions have been recorded.
- Alembic migrations (currently `Base.metadata.create_all` on startup, fine
  for a single-environment v1, not for iterating on schema in production).
- Multi-timeframe technical analysis (currently daily bars only).
