"""Geopolitical event ingestion via GDELT's free DOC 2.0 API.

Note: the full GDELT Event Database (with real CAMEO codes and Goldstein
scale) is distributed as large rolling CSV exports updated every 15 minutes,
which is overkill for a v1 MVP. Instead this module queries GDELT's DOC 2.0
article-search API (keyless, JSON) for geopolitical-risk headlines and
derives an approximate Goldstein-scale proxy from our own tone lexicon. This
is clearly an approximation -- swapping in the full GDELT Events table (or a
licensed geopolitical risk feed) later only means rewriting this file; the
`GeoEvent` model and everything downstream stays the same.
"""

import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.geopolitical import GeoEvent
from app.services.ingestion.news_feed import _score_sentiment

logger = logging.getLogger(__name__)

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"

QUERY = "(war OR sanctions OR ceasefire OR military OR conflict OR invasion OR strike) sourcelang:english"


def fetch_and_store_geo_events(db: Session, query: str = QUERY, max_records: int = 50) -> int:
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "timespan": "1d",
        "sort": "hybridrel",
        "maxrecords": str(max_records),
    }
    try:
        resp = httpx.get(GDELT_DOC_API, params=params, timeout=20.0, headers={"User-Agent": "WealthAI/0.1"})
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("geopolitical: GDELT fetch failed: %s", exc)
        return 0

    articles = data.get("articles", [])
    written = 0

    for art in articles:
        url = art.get("url")
        title = art.get("title", "")
        if not url or not title:
            continue
        if db.query(GeoEvent).filter(GeoEvent.url == url).first():
            continue

        seen_date = art.get("seendate")  # e.g. "20260915T120000Z"
        try:
            event_date = datetime.strptime(seen_date, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            event_date = datetime.now(timezone.utc)

        tone = _score_sentiment(title)  # -1..+1
        goldstein_proxy = round(tone * 10, 2)  # scale to GDELT's -10..+10 convention

        geo = GeoEvent(
            event_date=event_date,
            actor1=art.get("domain", ""),
            actor2="",
            event_code="",
            event_description=title,
            goldstein_scale=goldstein_proxy,
            avg_tone=tone,
            location=art.get("sourcecountry", ""),
            url=url,
        )
        db.add(geo)
        written += 1

    db.commit()
    logger.info("geopolitical: wrote %d new events", written)
    return written


def recent_geo_events(db: Session, limit: int = 50) -> list[GeoEvent]:
    return db.query(GeoEvent).order_by(GeoEvent.event_date.desc()).limit(limit).all()


def geopolitical_risk_score(db: Session, lookback: int = 50) -> float:
    """Aggregate recent Goldstein proxies into a single 0..100 risk score
    (higher = more conflictual / risk-off).
    """
    events = recent_geo_events(db, limit=lookback)
    if not events:
        return 50.0  # neutral prior when we have no data
    avg_goldstein = sum(e.goldstein_scale for e in events) / len(events)
    # Goldstein -10 (max conflict) .. +10 (max cooperation) -> risk score 100..0
    risk = (10 - avg_goldstein) / 20 * 100
    return round(max(0.0, min(100.0, risk)), 1)
