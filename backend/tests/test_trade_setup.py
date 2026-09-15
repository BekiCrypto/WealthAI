from app.schemas.common import ScoreBreakdown, TechnicalSnapshot, TradeSetup
from app.services.analysis.trade_setup import generate_trade_setup
from app.services.ingestion.providers import gate_trade_setup


def make_score(bullish_pct=72.0, confidence="High", macro="bullish", technical="bullish", sentiment="neutral", geopolitical="bullish"):
    return ScoreBreakdown(
        symbol="TEST", bullish_pct=bullish_pct, confidence=confidence,
        macro=macro, technical=technical, sentiment=sentiment, geopolitical=geopolitical,
        reasons=["Technical: bullish", "Macro: bullish", "Sentiment: neutral", "Geopolitical: bullish"],
    )


def make_snapshot(trend="uptrend", rsi=55.0, last_price=100.0, atr=2.0, support=95.0, resistance=110.0, sma_20=98.0):
    return TechnicalSnapshot(
        symbol="TEST", last_price=last_price, trend=trend, rsi_14=rsi,
        sma_20=sma_20, sma_50=90.0, sma_200=80.0, ema_20=97.0, atr_14=atr,
        support=support, resistance=resistance, volatility_20d=0.2,
    )


def target(setup, label):
    return next(t for t in setup["targets"] if t["label"] == label)


def test_uptrend_continuation_is_long_with_staged_targets():
    setup = generate_trade_setup("TEST", make_score(), make_snapshot())
    assert setup["direction"] == "long"
    assert setup["setup_type"] == "trend_continuation"
    assert setup["entry_price"] == 100.0
    assert setup["stop_price"] < setup["entry_price"]
    assert [t["label"] for t in setup["targets"]] == ["TP1", "TP2", "TP3"]

    tp1, tp2, tp3 = target(setup, "TP1"), target(setup, "TP2"), target(setup, "TP3")
    # Staged targets must be strictly increasing for a long, and each further
    # out than the last -- otherwise "scale out" doesn't mean anything.
    assert setup["entry_price"] < tp1["price"] < tp2["price"] < tp3["price"]
    assert tp1["r_multiple"] == 1.0  # TP1 is defined as exactly 1R
    assert tp2["price"] == 110.0  # resistance, since it's above entry
    assert setup["risk_reward"] == tp2["r_multiple"]  # headline R:R is TP2's


def test_overbought_uptrend_waits_for_pullback_instead_of_chasing():
    setup = generate_trade_setup("TEST", make_score(), make_snapshot(rsi=78.0))
    assert setup["direction"] == "long"
    assert setup["setup_type"] == "wait_for_pullback"
    assert setup["entry_price"] == 98.0  # sma_20, not the current (overbought) price


def test_downtrend_bearish_score_is_short_with_staged_targets():
    score = make_score(bullish_pct=25.0, macro="bearish", technical="bearish", geopolitical="neutral")
    # A tighter resistance (closer stop) and farther support (bigger target) than the shared
    # long-side fixture, so this short has a favorable risk/reward and isn't filtered out.
    setup = generate_trade_setup(
        "TEST", score, make_snapshot(trend="downtrend", rsi=45.0, support=90.0, resistance=102.0)
    )
    assert setup["direction"] == "short"
    assert setup["setup_type"] == "trend_continuation"
    assert setup["stop_price"] > setup["entry_price"]

    tp1, tp2, tp3 = target(setup, "TP1"), target(setup, "TP2"), target(setup, "TP3")
    # Staged targets must be strictly decreasing for a short.
    assert setup["entry_price"] > tp1["price"] > tp2["price"] > tp3["price"]
    assert tp2["price"] == 90.0  # support, below entry
    assert setup["risk_reward"] >= 1.2


def test_range_bound_long_enters_at_support():
    setup = generate_trade_setup("TEST", make_score(), make_snapshot(trend="range_bound"))
    assert setup["direction"] == "long"
    assert setup["setup_type"] == "range_long"
    assert setup["entry_price"] == 95.0  # support


def test_countertrend_setup_is_flagged_and_downgraded_to_low_confidence():
    # bullish score but a confirmed downtrend -- technicals disagree with the score
    setup = generate_trade_setup("TEST", make_score(), make_snapshot(trend="downtrend", rsi=50.0))
    assert setup["direction"] == "long"
    assert setup["setup_type"] == "countertrend_reversal"
    assert setup["confidence"] == "Low"


def test_low_confidence_score_yields_no_setup():
    setup = generate_trade_setup("TEST", make_score(confidence="Low"), make_snapshot())
    assert setup["direction"] == "none"
    assert setup["entry_price"] is None
    assert setup["targets"] == []


def test_neutral_score_yields_no_setup():
    setup = generate_trade_setup("TEST", make_score(bullish_pct=50.0), make_snapshot())
    assert setup["direction"] == "none"


def test_poor_risk_reward_is_suppressed_rather_than_shown():
    # Entry via SMA20 pullback, but resistance/support are positioned so the
    # mechanical stop/TP2 math produces risk_reward well under 1:1 -- a real
    # trader wouldn't take this, so the engine should say "no setup" rather
    # than dress up an unfavorable trade as a signal.
    setup = generate_trade_setup(
        "TEST", make_score(), make_snapshot(rsi=78.0, support=80.0, resistance=99.0, sma_20=98.0)
    )
    assert setup["direction"] == "none"
    assert "risk/reward" in setup["reasoning"]


def test_missing_price_data_yields_no_setup():
    snapshot = make_snapshot()
    snapshot = snapshot.model_copy(update={"last_price": None})
    setup = generate_trade_setup("TEST", make_score(), snapshot)
    assert setup["direction"] == "none"


def test_main_risk_names_the_opposing_component():
    score = make_score(sentiment="bearish")
    setup = generate_trade_setup("TEST", score, make_snapshot())
    assert "sentiment" in setup["main_risk"].lower()
    assert "still bearish" in setup["main_risk"]


def test_timeframe_is_always_stated():
    setup = generate_trade_setup("TEST", make_score(), make_snapshot())
    assert setup["timeframe"] == "Swing (daily chart)"
    assert "daily" in setup["timeframe_note"].lower()
    # Even a "none" setup states the timeframe, since it's a property of the
    # engine (daily bars), not of whether a directional call was made.
    none_setup = generate_trade_setup("TEST", make_score(confidence="Low"), make_snapshot())
    assert none_setup["timeframe"] == "Swing (daily chart)"


def test_gate_withholds_prices_for_non_redistributable_symbol():
    setup = generate_trade_setup("GC=F", make_score(), make_snapshot())
    gated = gate_trade_setup(TradeSetup(**setup))
    assert gated.redistributable is False
    assert gated.entry_price is None
    assert gated.stop_price is None
    assert gated.entry_pct_from_last is not None  # ratios survive the gate
    assert gated.risk_reward is not None
    assert gated.price_disclosure is not None
    assert len(gated.targets) == 3
    for t in gated.targets:
        assert t.price is None  # each staged target's absolute price is withheld too
        assert t.pct_from_entry is not None
        assert t.r_multiple is not None


def test_gate_passes_through_redistributable_symbol_untouched():
    setup = generate_trade_setup("BTC-USD", make_score(), make_snapshot())
    gated = gate_trade_setup(TradeSetup(**setup))
    assert gated.redistributable is True
    assert gated.entry_price == setup["entry_price"]
    assert gated.price_disclosure is None
    assert gated.targets[1].price == setup["targets"][1]["price"]
