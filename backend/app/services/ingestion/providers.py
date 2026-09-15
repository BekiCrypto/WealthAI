"""Data-provider registry: the licensing boundary of the app.

Most free market-data plans (Alpha Vantage, Twelve Data, FMP, Finnhub free
tier) permit personal use only and prohibit redistributing the data to third
parties. `yfinance` is arguably stricter still -- it scrapes Yahoo's
undocumented endpoints rather than using a licensed API at all. Public crypto
exchange REST APIs (Coinbase, Kraken, Binance) are the exception: their
market-data endpoints are meant to be consumed by third-party sites and
apps, no key required.

So every symbol's price data provider is tagged `redistributable` here, and
that flag -- not a per-request guess -- is what routers/assets.py checks
before deciding whether to return a raw price/OHLCV number or withhold it in
favor of derived-only output (intelligence score, trend label, bounded
oscillators). Swapping in a licensed feed later means changing exactly one
line here; nothing downstream needs to change.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderInfo:
    name: str
    redistributable: bool
    note: str


YFINANCE = ProviderInfo(
    name="yfinance",
    redistributable=False,
    note="Scraped from Yahoo Finance's undocumented endpoints; Yahoo's terms do not license "
    "redistribution. Used here to compute derived analysis (trend, RSI, intelligence score) "
    "only -- raw price/OHLCV values are withheld from public API responses.",
)

COINBASE = ProviderInfo(
    name="coinbase",
    redistributable=True,
    note="Coinbase Exchange's public market-data REST API is unauthenticated and intended for "
    "third-party consumption, so raw prices/OHLCV are shown live.",
)

# Symbols whose price data comes from Coinbase's public exchange API instead of yfinance.
# Coinbase product ids happen to match our existing "BTC-USD" / "ETH-USD" symbol convention.
COINBASE_SYMBOLS = {"BTC-USD", "ETH-USD"}


def provider_for_symbol(symbol: str) -> ProviderInfo:
    if symbol in COINBASE_SYMBOLS:
        return COINBASE
    return YFINANCE


def is_redistributable(symbol: str) -> bool:
    return provider_for_symbol(symbol).redistributable


PRICE_SCALE_FIELDS = ("last_price", "sma_20", "sma_50", "sma_200", "ema_20", "atr_14", "support", "resistance")


def gate_technical_snapshot(snapshot):
    """Withholds raw price-scale numbers for a non-redistributable symbol,
    keeping only the interpretation layer: trend (categorical), RSI (a
    bounded 0-100 oscillator), and volatility (a ratio) -- our own derived
    analysis, not the underlying provider's data. Redistributable symbols
    (crypto, via Coinbase) pass through untouched.
    """
    provider = provider_for_symbol(snapshot.symbol)
    if provider.redistributable:
        return snapshot.model_copy(update={"redistributable": True})

    return snapshot.model_copy(
        update={
            "redistributable": False,
            "price_disclosure": (
                f"Live price withheld: {snapshot.symbol}'s data comes from {provider.name}, "
                "whose free tier isn't licensed for public redistribution. Trend, RSI and "
                "volatility below are our own derived analysis, not the underlying data."
            ),
            **{field: None for field in PRICE_SCALE_FIELDS},
        }
    )
