"""Technical analysis: trend, RSI, SMA/EMA, ATR, support/resistance,
volatility -- combined with macro intelligence per spec step 6 so the final
signal isn't based on economic news alone.
"""

import pandas as pd

from app.models.price import PriceBar
from app.schemas.common import TechnicalSnapshot


def bars_to_frame(bars: list[PriceBar]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ts": [b.ts for b in bars],
            "open": [b.open for b in bars],
            "high": [b.high for b in bars],
            "low": [b.low for b in bars],
            "close": [b.close for b in bars],
            "volume": [b.volume for b in bars],
        }
    )


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def support_resistance(df: pd.DataFrame, lookback: int = 60) -> tuple[float, float]:
    window = df.tail(lookback)
    return float(window["low"].min()), float(window["high"].max())


def classify_trend(df: pd.DataFrame) -> str:
    if len(df) < 50:
        return "insufficient_data"
    close = df["close"]
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]
    last = close.iloc[-1]
    if last > sma20 > sma50:
        return "uptrend"
    if last < sma20 < sma50:
        return "downtrend"
    return "range_bound"


def compute_snapshot(symbol: str, bars: list[PriceBar]) -> TechnicalSnapshot | None:
    if not bars:
        return None
    df = bars_to_frame(bars)
    close = df["close"]
    last_price = float(close.iloc[-1])

    sma20 = close.rolling(20).mean().iloc[-1] if len(df) >= 20 else None
    sma50 = close.rolling(50).mean().iloc[-1] if len(df) >= 50 else None
    sma200 = close.rolling(200).mean().iloc[-1] if len(df) >= 200 else None
    ema20 = close.ewm(span=20, adjust=False).mean().iloc[-1] if len(df) >= 20 else None
    rsi14 = rsi(close).iloc[-1] if len(df) >= 15 else None
    atr14 = atr(df).iloc[-1] if len(df) >= 15 else None
    support, resistance = support_resistance(df) if len(df) >= 10 else (None, None)

    returns = close.pct_change().dropna()
    vol20 = float(returns.tail(20).std() * (252 ** 0.5)) if len(returns) >= 20 else None

    return TechnicalSnapshot(
        symbol=symbol,
        last_price=last_price,
        trend=classify_trend(df),
        rsi_14=round(float(rsi14), 2) if rsi14 is not None and pd.notna(rsi14) else None,
        sma_20=round(float(sma20), 4) if sma20 is not None and pd.notna(sma20) else None,
        sma_50=round(float(sma50), 4) if sma50 is not None and pd.notna(sma50) else None,
        sma_200=round(float(sma200), 4) if sma200 is not None and pd.notna(sma200) else None,
        ema_20=round(float(ema20), 4) if ema20 is not None and pd.notna(ema20) else None,
        atr_14=round(float(atr14), 4) if atr14 is not None and pd.notna(atr14) else None,
        support=round(support, 4) if support is not None else None,
        resistance=round(resistance, 4) if resistance is not None else None,
        volatility_20d=round(vol20, 4) if vol20 is not None else None,
    )


def technical_bias(snapshot: TechnicalSnapshot) -> str:
    """Collapse the technical snapshot into bullish/bearish/neutral for the
    intelligence-score aggregator. A confirmed trend dominates the read;
    RSI overbought/oversold is a caution flag within a trend, not a reversal
    signal, and only drives the call when the market is range-bound.
    """
    if snapshot.trend == "uptrend":
        return "bullish"
    if snapshot.trend == "downtrend":
        return "bearish"
    if snapshot.rsi_14 is not None and snapshot.rsi_14 >= 70:
        return "bearish"  # range-bound and overbought: mean-reversion risk
    if snapshot.rsi_14 is not None and snapshot.rsi_14 <= 30:
        return "bullish"  # range-bound and oversold: mean-reversion opportunity
    return "neutral"
