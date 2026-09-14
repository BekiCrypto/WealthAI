"""Economic calendar ingestion.

A forward calendar with consensus forecasts is normally a licensed product
(Bloomberg, TradingEconomics, Investing.com). This module keeps the seam
narrow: `sync_actuals_from_fred` is the only place that talks to a real data
provider (FRED, free but keyless-optional), and `seed_calendar` provides a
believable demo calendar so the rest of the app (scenario prediction, world
state, UI) has something real to work against out of the box. Swapping in a
licensed calendar feed later only means rewriting this file.
"""

import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.event import EconomicEvent

logger = logging.getLogger(__name__)
settings = get_settings()

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Indicative mapping of tracked events to FRED series. FRED does not publish
# forward consensus, only realized data -- so this is used solely to backfill
# `previous`/`actual` for events whose scheduled_at has passed.
FRED_SERIES_MAP = {
    "US CPI YoY": "CPALTT01USM657N",
    "US Unemployment Rate": "UNRATE",
    "US Nonfarm Payrolls": "PAYEMS",
    "US ISM Manufacturing PMI": None,  # not on FRED (proprietary ISM data)
    "US GDP QoQ Annualized": "A191RL1Q225SBEA",
    "FOMC Rate Decision (Upper Bound)": "DFEDTARU",
    "ECB Deposit Rate Decision": None,  # not on FRED
    "China Manufacturing PMI": None,  # not on FRED
}


def _estimate_probabilities(consensus: float, previous: float) -> dict:
    """A small, explainable heuristic standing in for the real 'macro brain'
    quantitative model: tilts the AI estimate in the direction of recent
    momentum (consensus vs previous) and derives surprise probabilities from
    the tilt size. Replace with a calibrated statistical/ML model once enough
    historical surprise data has been collected (see prediction calibration).
    """
    momentum = consensus - previous
    tilt = momentum * 0.25  # assume trend carries through partially
    ai_estimate = round(consensus + tilt, 2)

    spread = max(abs(momentum) * 0.6, 0.15)
    low = round(consensus - spread, 2)
    high = round(consensus + spread, 2)

    if tilt > 0:
        prob_up, prob_down = 0.32, 0.21
    elif tilt < 0:
        prob_up, prob_down = 0.21, 0.32
    else:
        prob_up, prob_down = 0.26, 0.26
    prob_inline = round(1 - prob_up - prob_down, 2)

    return {
        "ai_estimate": ai_estimate,
        "ai_estimate_low": low,
        "ai_estimate_high": high,
        "prob_upside_surprise": prob_up,
        "prob_downside_surprise": prob_down,
        "prob_inline": prob_inline,
    }


def seed_calendar(db: Session) -> int:
    """Seed a believable forward calendar if none exists yet. Idempotent:
    no-ops once any event row exists.
    """
    if db.query(EconomicEvent).first() is not None:
        return 0

    now = datetime.now(timezone.utc)
    seeds = [
        dict(name="US CPI YoY", country="US", category="inflation", importance="high",
             scheduled_at=now + timedelta(hours=2), previous=3.3, consensus=3.4, unit="%"),
        dict(name="US Nonfarm Payrolls", country="US", category="employment", importance="high",
             scheduled_at=now + timedelta(days=1, hours=6), previous=175.0, consensus=180.0, unit="k"),
        dict(name="US Unemployment Rate", country="US", category="employment", importance="high",
             scheduled_at=now + timedelta(days=1, hours=6), previous=4.1, consensus=4.0, unit="%"),
        dict(name="US ISM Manufacturing PMI", country="US", category="growth", importance="medium",
             scheduled_at=now + timedelta(days=3), previous=48.5, consensus=48.8, unit="idx"),
        dict(name="FOMC Rate Decision (Upper Bound)", country="US", category="central_bank", importance="high",
             scheduled_at=now + timedelta(days=5), previous=5.25, consensus=5.25, unit="%"),
        dict(name="China Manufacturing PMI", country="CN", category="growth", importance="medium",
             scheduled_at=now + timedelta(days=7), previous=49.5, consensus=49.8, unit="idx"),
        dict(name="ECB Deposit Rate Decision", country="EU", category="central_bank", importance="high",
             scheduled_at=now + timedelta(days=10), previous=3.75, consensus=3.75, unit="%"),
        dict(name="US GDP QoQ Annualized", country="US", category="growth", importance="high",
             scheduled_at=now + timedelta(days=12), previous=2.1, consensus=2.3, unit="%"),
    ]

    count = 0
    for s in seeds:
        probs = _estimate_probabilities(s["consensus"], s["previous"])
        event = EconomicEvent(source="seed", status="scheduled", **s, **probs)
        db.add(event)
        count += 1

    db.commit()
    logger.info("economic_calendar: seeded %d events", count)
    return count


def _fetch_fred_latest(series_id: str, api_key: str) -> tuple[float | None, float | None]:
    """Returns (previous, latest) observation values for a FRED series."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 2,
    }
    resp = httpx.get(FRED_BASE_URL, params=params, timeout=15.0)
    resp.raise_for_status()
    obs = resp.json().get("observations", [])
    values = [float(o["value"]) for o in obs if o.get("value") not in (None, ".")]
    if not values:
        return None, None
    latest = values[0]
    previous = values[1] if len(values) > 1 else None
    return previous, latest


def sync_actuals_from_fred(db: Session) -> int:
    """For due events still marked 'scheduled', try to backfill the actual
    print from FRED. No-ops gracefully if FRED_API_KEY isn't configured.
    """
    if not settings.fred_api_key:
        logger.info("economic_calendar: FRED_API_KEY not set, skipping actuals sync")
        return 0

    now = datetime.now(timezone.utc)
    due = (
        db.query(EconomicEvent)
        .filter(EconomicEvent.status == "scheduled", EconomicEvent.scheduled_at <= now)
        .all()
    )

    updated = 0
    for event in due:
        series_id = FRED_SERIES_MAP.get(event.name)
        if not series_id:
            continue
        try:
            _, latest = _fetch_fred_latest(series_id, settings.fred_api_key)
        except Exception as exc:
            logger.warning("economic_calendar: FRED fetch failed for %s (%s): %s", event.name, series_id, exc)
            continue
        if latest is None:
            continue

        event.actual = latest
        event.actual_released_at = now
        event.surprise = round(latest - (event.consensus or latest), 3)
        event.status = "released"
        updated += 1

    db.commit()
    logger.info("economic_calendar: updated %d events with FRED actuals", updated)
    return updated


def upcoming_events(db: Session, hours_ahead: int = 24 * 14) -> list[EconomicEvent]:
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=hours_ahead)
    return (
        db.query(EconomicEvent)
        .filter(EconomicEvent.scheduled_at >= now - timedelta(hours=6), EconomicEvent.scheduled_at <= horizon)
        .order_by(EconomicEvent.scheduled_at.asc())
        .all()
    )
