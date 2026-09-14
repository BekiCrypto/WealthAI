"""Market price ingestion.

Uses yfinance (free, keyless) to pull daily OHLCV bars for the tracked
universe of equities/FX/commodities/crypto/rates. In production this module
is the seam where a licensed market-data provider (e.g. Refinitiv, Polygon,
Tiingo) would plug in instead — everything downstream (technical analysis,
scoring) only depends on the PriceBar table, not on yfinance itself.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.price import PriceBar

logger = logging.getLogger(__name__)
settings = get_settings()


def fetch_and_store_prices(db: Session, symbols: list[str] | None = None, period: str = "1y") -> int:
    """Fetch recent daily bars for each symbol and upsert into the DB.
    Returns the number of bars written. Never raises on a single-symbol
    failure -- logs and continues so one bad ticker doesn't stall ingestion.
    """
    import yfinance as yf

    symbols = symbols or settings.tracked_symbols
    written = 0

    for symbol in symbols:
        try:
            hist = yf.Ticker(symbol).history(period=period, interval="1d")
        except Exception as exc:  # network/provider errors shouldn't crash the scheduler
            logger.warning("market_data: failed to fetch %s: %s", symbol, exc)
            continue

        if hist is None or hist.empty:
            logger.warning("market_data: no data returned for %s", symbol)
            continue

        for ts, row in hist.iterrows():
            ts_utc = ts.to_pydatetime()
            if ts_utc.tzinfo is None:
                ts_utc = ts_utc.replace(tzinfo=timezone.utc)

            stmt = insert(PriceBar).values(
                symbol=symbol,
                ts=ts_utc,
                interval="1d",
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row.get("Volume", 0.0) or 0.0),
            ).on_conflict_do_update(
                index_elements=["symbol", "ts"],
                set_={
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row.get("Volume", 0.0) or 0.0),
                },
            )
            db.execute(stmt)
            written += 1

    db.commit()
    logger.info("market_data: wrote/updated %d bars across %d symbols", written, len(symbols))
    return written


def latest_price(db: Session, symbol: str) -> PriceBar | None:
    return (
        db.query(PriceBar)
        .filter(PriceBar.symbol == symbol)
        .order_by(PriceBar.ts.desc())
        .first()
    )


def price_history(db: Session, symbol: str, limit: int = 300) -> list[PriceBar]:
    bars = (
        db.query(PriceBar)
        .filter(PriceBar.symbol == symbol)
        .order_by(PriceBar.ts.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(bars))
