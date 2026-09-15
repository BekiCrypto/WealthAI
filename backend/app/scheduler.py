"""Background scheduler: periodically refreshes market data, news, geopolitical
events and economic-calendar actuals, then recomputes the World State and
persists a snapshot (spec step 8: "every new piece of important information
updates this state"). Uses APScheduler in-process; a heavier deployment would
move this to Celery/Kafka workers as noted in the project README.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.database import SessionLocal
from app.models.world_state import WorldStateSnapshot
from app.services.analysis.intelligence_score import compute_all_scores
from app.services.analysis.macro_brain import classify_world_state
from app.services.analysis.prediction_engine import resolve_due_predictions
from app.services.ingestion.economic_calendar import seed_calendar, sync_actuals_from_fred
from app.services.ingestion.geopolitical import fetch_and_store_geo_events
from app.services.ingestion.market_data import fetch_and_store_crypto_prices, fetch_and_store_prices
from app.services.ingestion.news_feed import fetch_and_store_news

logger = logging.getLogger(__name__)
settings = get_settings()


def job_refresh_market_data():
    db = SessionLocal()
    try:
        fetch_and_store_prices(db)
    except Exception:
        logger.exception("scheduler: market data refresh failed")
    finally:
        db.close()


def job_refresh_crypto_prices():
    db = SessionLocal()
    try:
        fetch_and_store_crypto_prices(db)
    except Exception:
        logger.exception("scheduler: crypto price refresh failed")
    finally:
        db.close()


def job_refresh_news():
    db = SessionLocal()
    try:
        fetch_and_store_news(db)
    except Exception:
        logger.exception("scheduler: news refresh failed")
    finally:
        db.close()


def job_refresh_geopolitical():
    db = SessionLocal()
    try:
        fetch_and_store_geo_events(db)
    except Exception:
        logger.exception("scheduler: geopolitical refresh failed")
    finally:
        db.close()


def job_refresh_calendar():
    db = SessionLocal()
    try:
        sync_actuals_from_fred(db)
    except Exception:
        logger.exception("scheduler: calendar refresh failed")
    finally:
        db.close()


def job_refresh_world_state():
    db = SessionLocal()
    try:
        world = classify_world_state(db)
        scores = compute_all_scores(db, settings.tracked_symbols)
        db.add(WorldStateSnapshot(regime=world["regime"], scores=scores, reasoning=world["reasoning"]))
        db.commit()
        resolve_due_predictions(db)
    except Exception:
        logger.exception("scheduler: world state refresh failed")
    finally:
        db.close()


def bootstrap():
    """Runs once at startup: seed the demo calendar and do an initial data
    pull so the UI isn't empty on first load.
    """
    db = SessionLocal()
    try:
        seed_calendar(db)
    finally:
        db.close()
    job_refresh_market_data()
    job_refresh_crypto_prices()
    job_refresh_news()
    job_refresh_geopolitical()
    job_refresh_world_state()


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(job_refresh_market_data, "interval", seconds=settings.market_data_interval, id="market_data")
    scheduler.add_job(job_refresh_crypto_prices, "interval", seconds=settings.market_data_interval, id="crypto_prices")
    scheduler.add_job(job_refresh_news, "interval", seconds=settings.news_interval, id="news")
    scheduler.add_job(job_refresh_geopolitical, "interval", seconds=settings.geopolitical_interval, id="geopolitical")
    scheduler.add_job(job_refresh_calendar, "interval", seconds=settings.economic_calendar_interval, id="calendar")
    scheduler.add_job(job_refresh_world_state, "interval", seconds=settings.world_state_interval, id="world_state")
    return scheduler
