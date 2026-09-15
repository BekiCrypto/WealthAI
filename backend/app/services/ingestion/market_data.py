"""Market price ingestion.

Uses yfinance (free, keyless) for equities/FX/commodities/rates, and
Coinbase's public exchange API for crypto -- see providers.py for why the
split matters: yfinance's data isn't licensed for redistribution, so those
symbols' raw prices are withheld at the API layer (routers/assets.py), while
Coinbase's public market data is meant for third-party display and is shown
live. Everything downstream (technical analysis, scoring) only depends on
the PriceBar table, not on which provider filled it.
"""

import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.price import PriceBar
from app.services.ingestion.providers import COINBASE_SYMBOLS

logger = logging.getLogger(__name__)
settings = get_settings()

COINBASE_CANDLES_URL = "https://api.exchange.coinbase.com/products/{product_id}/candles"


def fetch_and_store_prices(db: Session, symbols: list[str] | None = None, period: str = "1y") -> int:
    """Fetch recent daily bars for each non-crypto symbol via yfinance and
    upsert into the DB. Crypto symbols are skipped here -- see
    fetch_and_store_crypto_prices, which uses Coinbase instead. Never raises
    on a single-symbol failure -- logs and continues so one bad ticker
    doesn't stall ingestion.
    """
    import yfinance as yf

    symbols = [s for s in (symbols or settings.tracked_symbols) if s not in COINBASE_SYMBOLS]
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


def fetch_and_store_crypto_prices(db: Session, symbols: list[str] | None = None) -> int:
    """Fetch daily candles for crypto symbols from Coinbase's public exchange
    API (no key required) and upsert into the DB. This is the one provider
    in the app whose data is actually licensed for public display -- see
    providers.py.
    """
    symbols = symbols or list(COINBASE_SYMBOLS)
    written = 0

    for symbol in symbols:
        try:
            resp = httpx.get(
                COINBASE_CANDLES_URL.format(product_id=symbol),
                params={"granularity": 86400},
                headers={"User-Agent": "WealthAI/0.1"},
                timeout=15.0,
            )
            resp.raise_for_status()
            candles = resp.json()
        except Exception as exc:
            logger.warning("market_data: Coinbase fetch failed for %s: %s", symbol, exc)
            continue

        for candle in candles:
            ts, low, high, open_, close, volume = candle
            ts_utc = datetime.fromtimestamp(ts, tz=timezone.utc)

            stmt = insert(PriceBar).values(
                symbol=symbol,
                ts=ts_utc,
                interval="1d",
                open=float(open_),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=float(volume),
            ).on_conflict_do_update(
                index_elements=["symbol", "ts"],
                set_={"open": float(open_), "high": float(high), "low": float(low), "close": float(close), "volume": float(volume)},
            )
            db.execute(stmt)
            written += 1

    db.commit()
    logger.info("market_data: wrote/updated %d crypto bars across %d symbols", written, len(symbols))
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
