from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from app.services.analysis import technical


@dataclass
class FakeBar:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


def make_uptrend_bars(n: int = 260, start: float = 100.0, step: float = 0.5) -> list[FakeBar]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars = []
    price = start
    for i in range(n):
        price += step
        bars.append(
            FakeBar(
                ts=base + timedelta(days=i),
                open=price - 0.1,
                high=price + 0.2,
                low=price - 0.3,
                close=price,
                volume=1000.0,
            )
        )
    return bars


def make_downtrend_bars(n: int = 260, start: float = 200.0, step: float = 0.5) -> list[FakeBar]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars = []
    price = start
    for i in range(n):
        price -= step
        bars.append(
            FakeBar(
                ts=base + timedelta(days=i),
                open=price + 0.1,
                high=price + 0.3,
                low=price - 0.2,
                close=price,
                volume=1000.0,
            )
        )
    return bars


def test_compute_snapshot_empty_returns_none():
    assert technical.compute_snapshot("TEST", []) is None


def test_uptrend_is_classified_bullish():
    bars = make_uptrend_bars()
    snapshot = technical.compute_snapshot("TEST", bars)
    assert snapshot is not None
    assert snapshot.trend == "uptrend"
    assert snapshot.sma_20 is not None and snapshot.sma_50 is not None
    assert snapshot.sma_20 > snapshot.sma_50  # short-term average above long-term in an uptrend
    assert technical.technical_bias(snapshot) == "bullish"


def test_downtrend_is_classified_bearish():
    bars = make_downtrend_bars()
    snapshot = technical.compute_snapshot("TEST", bars)
    assert snapshot is not None
    assert snapshot.trend == "downtrend"
    assert technical.technical_bias(snapshot) == "bearish"


def test_rsi_bounds():
    bars = make_uptrend_bars()
    df = technical.bars_to_frame(bars)
    rsi_series = technical.rsi(df["close"])
    valid = rsi_series.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_support_resistance_bounds_last_close():
    bars = make_uptrend_bars()
    df = technical.bars_to_frame(bars)
    support, resistance = technical.support_resistance(df)
    assert support < df["close"].iloc[-1] < resistance or support <= df["close"].iloc[-1] <= resistance
