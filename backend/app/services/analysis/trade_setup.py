"""Trade setup engine: turns the Intelligence Score into a concrete entry,
bias, stop (invalidation), and staged targets -- the closest thing in the
app to spec step 9's "give me the highest-probability Gold setup" -- instead
of leaving "72% bullish" as an abstract call nobody can actually act on or
disprove.

Direction/bias and conviction come from the Intelligence Score (macro +
technical + sentiment + geopolitical, spec step 7); the actual entry/stop/
target *levels* come from pure price structure (trend, RSI, support/
resistance, ATR), since macro conviction alone doesn't tell you where to
place a stop.

Every setup carries three staged targets (TP1/TP2/TP3), the standard
scale-out structure -- take partial profit at 1R and move the stop to
breakeven, take more at the structural level, let the rest run to an
extension -- rather than a single arbitrary number. All of it is built from
daily-bar technicals, so the timeframe is fixed and stated explicitly
(TIMEFRAME_NOTE) rather than left implicit; there's no intraday/weekly
variant yet (see README roadmap).

When the score is too close to 50/50, confidence is Low, or the mechanical
stop/TP2 math produces a risk/reward below MIN_RISK_REWARD, this
deliberately returns direction="none" rather than manufacturing a
low-probability trade to fill the space -- not every asset has a good setup
on a given day, and pretending otherwise is exactly the kind of overclaiming
this app is trying not to do.
"""

from app.schemas.common import ScoreBreakdown, TechnicalSnapshot

LONG_THRESHOLD = 55.0
SHORT_THRESHOLD = 45.0
OVERBOUGHT = 70.0
OVERSOLD = 30.0
MIN_RISK_REWARD = 1.2  # below this (measured at TP2), the stop isn't justified by the target

SCORE_COMPONENTS = ("macro", "technical", "sentiment", "geopolitical")

TIMEFRAME = "Swing (daily chart)"
TIMEFRAME_NOTE = (
    "Entry, stop and targets are all sized from daily-bar structure (SMA/ATR/support-resistance "
    "over the trailing ~300 daily bars), so this setup is meant to play out over days to a couple "
    "of weeks, not intraday. There's no intraday or weekly variant yet."
)


def _opposing_risk(direction: str, score: ScoreBreakdown) -> str:
    """Names whichever component of the score disagrees with this setup's
    direction -- a specific, derived 'main risk' instead of a generic line.
    """
    opposite = "bearish" if direction == "long" else "bullish"
    opposing = [c for c in SCORE_COMPONENTS if getattr(score, c) == opposite]
    if opposing:
        return (
            f"{'/'.join(opposing).capitalize()} signal(s) are still {opposite} -- a shift there "
            f"would undercut this {direction}."
        )
    return f"No individual signal component currently opposes this {direction}, but overall confidence is only {score.confidence}."


def _target(label: str, price: float, entry: float, risk: float, note: str) -> dict:
    return {
        "label": label,
        "price": round(price, 4),
        "pct_from_entry": round((price - entry) / entry * 100, 2),
        "r_multiple": round(abs(price - entry) / risk, 2) if risk else None,
        "note": note,
    }


def _no_setup(symbol: str, score: ScoreBreakdown, reason: str) -> dict:
    return {
        "symbol": symbol,
        "direction": "none",
        "setup_type": None,
        "timeframe": TIMEFRAME,
        "timeframe_note": TIMEFRAME_NOTE,
        "confidence": score.confidence,
        "probability": score.bullish_pct,
        "entry_price": None,
        "entry_pct_from_last": None,
        "stop_price": None,
        "stop_pct_from_entry": None,
        "risk_reward": None,
        "targets": [],
        "reasoning": reason,
        "invalidation": "",
        "main_risk": "",
    }


def generate_trade_setup(symbol: str, score: ScoreBreakdown, snapshot: TechnicalSnapshot) -> dict:
    if snapshot.last_price is None or snapshot.atr_14 is None:
        return _no_setup(symbol, score, "Not enough price history yet to size a stop and target.")

    if score.confidence == "Low":
        return _no_setup(
            symbol, score,
            "Intelligence score confidence is Low -- the underlying signals conflict, so no "
            "setup is offered rather than guessing.",
        )

    if score.bullish_pct >= LONG_THRESHOLD:
        direction = "long"
    elif score.bullish_pct <= SHORT_THRESHOLD:
        direction = "short"
    else:
        return _no_setup(
            symbol, score,
            f"Intelligence score is {score.bullish_pct}% bullish -- too close to neutral for a "
            "directional setup.",
        )

    price = snapshot.last_price
    atr = snapshot.atr_14
    support = snapshot.support
    resistance = snapshot.resistance
    rsi = snapshot.rsi_14
    trend = snapshot.trend

    if direction == "long":
        if trend == "uptrend" and rsi is not None and rsi >= OVERBOUGHT:
            setup_type = "wait_for_pullback"
            entry = snapshot.sma_20 or price
            entry_note = (
                f"{symbol} is in an uptrend but RSI ({rsi}) is overbought -- entering here risks "
                "chasing a short-term top. A pullback toward the 20-period average is a better entry."
            )
        elif trend == "uptrend":
            setup_type = "trend_continuation"
            entry = price
            entry_note = (
                f"{symbol} is in a confirmed uptrend with room before overbought (RSI {rsi}); "
                "the current price is a reasonable continuation entry."
            )
        elif trend == "range_bound" and support is not None:
            setup_type = "range_long"
            entry = support
            entry_note = (
                f"{symbol} is range-bound; buying near the range's support offers a better "
                "risk/reward than chasing the middle of the range."
            )
        else:
            setup_type = "countertrend_reversal"
            entry = price
            entry_note = (
                f"{symbol}'s technical trend ({trend.replace('_', ' ')}) doesn't confirm the "
                "bullish score -- this is a countertrend call, lower-confidence by nature."
            )

        stop = (support - 0.5 * atr) if support is not None else entry - 1.5 * atr
        if stop >= entry:
            stop = entry - 1.5 * atr
        risk = entry - stop
        structural = resistance is not None and resistance > entry
        tp2_price = resistance if structural else entry + 2 * risk
        tp1_price = entry + risk
        tp3_price = entry + (tp2_price - entry) * 1.5

    else:  # short
        if trend == "downtrend" and rsi is not None and rsi <= OVERSOLD:
            setup_type = "wait_for_bounce"
            entry = snapshot.sma_20 or price
            entry_note = (
                f"{symbol} is in a downtrend but RSI ({rsi}) is oversold -- entering here risks "
                "chasing a short-term bottom. A bounce toward the 20-period average is a better entry."
            )
        elif trend == "downtrend":
            setup_type = "trend_continuation"
            entry = price
            entry_note = (
                f"{symbol} is in a confirmed downtrend with room before oversold (RSI {rsi}); "
                "the current price is a reasonable continuation entry."
            )
        elif trend == "range_bound" and resistance is not None:
            setup_type = "range_short"
            entry = resistance
            entry_note = (
                f"{symbol} is range-bound; selling near the range's resistance offers a better "
                "risk/reward than chasing the middle of the range."
            )
        else:
            setup_type = "countertrend_reversal"
            entry = price
            entry_note = (
                f"{symbol}'s technical trend ({trend.replace('_', ' ')}) doesn't confirm the "
                "bearish score -- this is a countertrend call, lower-confidence by nature."
            )

        stop = (resistance + 0.5 * atr) if resistance is not None else entry + 1.5 * atr
        if stop <= entry:
            stop = entry + 1.5 * atr
        risk = stop - entry
        structural = support is not None and support < entry
        tp2_price = support if structural else entry - 2 * risk
        tp1_price = entry - risk
        tp3_price = entry - (entry - tp2_price) * 1.5

    targets = [
        _target("TP1", tp1_price, entry, risk, "1R -- take partial profit here and move the stop to breakeven."),
        _target(
            "TP2", tp2_price, entry, risk,
            "The next structural level (support/resistance)." if structural
            else "No nearby structural level, so this is 2x the risk distance instead.",
        ),
        _target("TP3", tp3_price, entry, risk, "An extension beyond the structural target for any portion left to run."),
    ]
    risk_reward = targets[1]["r_multiple"]  # TP2 is the headline risk/reward

    if risk_reward is not None and risk_reward < MIN_RISK_REWARD:
        return _no_setup(
            symbol, score,
            f"A {direction} setup exists technically ({setup_type.replace('_', ' ')}), but its "
            f"risk/reward to TP2 is only {risk_reward}:1 -- the stop is too far from entry relative "
            f"to the target to be worth taking, so no setup is offered.",
        )

    confidence = "Low" if setup_type == "countertrend_reversal" else score.confidence
    probability = score.bullish_pct if direction == "long" else round(100 - score.bullish_pct, 1)

    return {
        "symbol": symbol,
        "direction": direction,
        "setup_type": setup_type,
        "timeframe": TIMEFRAME,
        "timeframe_note": TIMEFRAME_NOTE,
        "confidence": confidence,
        "probability": probability,
        "entry_price": round(entry, 4),
        "entry_pct_from_last": round((entry - price) / price * 100, 2),
        "stop_price": round(stop, 4),
        "stop_pct_from_entry": round((stop - entry) / entry * 100, 2),
        "risk_reward": risk_reward,
        "targets": targets,
        "reasoning": entry_note,
        "invalidation": (
            f"A sustained move through {stop:.4g} (the stop level) invalidates this setup -- "
            f"treat it as evidence the {direction} thesis is wrong, not just noise."
        ),
        "main_risk": _opposing_risk(direction, score),
    }
