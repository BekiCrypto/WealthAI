"""Prediction engine: pre-event scenario analysis (spec step 4), post-release
reaction (spec step 5), and calibration tracking (spec step 10) so the system
learns which signals actually work over thousands of predictions.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.event import EconomicEvent
from app.models.prediction import Prediction, PredictionOutcome
from app.services.education.glossary import get_education
from app.services.ingestion import market_data

# Which assets each event category is expected to move, and in which
# direction *if* the print comes in hot (above consensus). Cool prints imply
# the opposite. This is the explainable link between "what happened" and
# "what it means for markets" (spec step 4/6).
#
# This table -- like the surprise-probability heuristic in
# economic_calendar.py -- is hand-picked from textbook macro relationships,
# not fitted to measured historical reactions. It is deliberately marked
# `basis: "heuristic"` everywhere it's returned from this module so the UI
# can warn the user rather than presenting it as calibrated fact. Replacing
# it with real statistics is the backtest-pipeline roadmap item.
CATEGORY_ASSET_IMPACT = {
    "inflation": {"GC=F": -1, "DX-Y.NYB": 1, "^GSPC": -1, "BTC-USD": -1, "^TNX": 1},
    "employment": {"GC=F": -1, "DX-Y.NYB": 1, "^GSPC": 0, "^TNX": 1},
    "growth": {"GC=F": 0, "^GSPC": 1, "DX-Y.NYB": 0.3},
    "central_bank": {"GC=F": -1, "DX-Y.NYB": 1, "^GSPC": -1, "^TNX": 1, "BTC-USD": -1},
}

# Events where a HIGHER print is actually the dovish/easing signal (bad for
# the currency/hawkish case), not the hawkish one -- e.g. a higher
# unemployment rate or more jobless claims means a weaker labor market, the
# opposite of a higher payrolls or CPI print. Getting this backwards is a
# common retail-tool mistake this app explicitly guards against.
INVERTED_EVENTS = {"US Unemployment Rate"}

HEURISTIC_DISCLOSURE = (
    "Bands and probabilities are derived from this release's own consensus/previous spread "
    "using a simple heuristic model (basis=\"heuristic\"), not yet calibrated against measured "
    "historical market reactions. See the README roadmap for the planned backtest pipeline."
)


def _band_sigma(event: EconomicEvent) -> float | None:
    if event.ai_estimate_low is None or event.ai_estimate_high is None:
        return None
    sigma = (event.ai_estimate_high - event.ai_estimate_low) / 2
    return sigma if sigma > 0 else None


def _magnitude(abs_z: float) -> str:
    if abs_z >= 1.5:
        return "big"
    if abs_z >= 0.5:
        return "moderate"
    return "small"


def _policy_lean(z: float, inverted: bool) -> str:
    effective = -z if inverted else z
    if effective > 0.5:
        return "hawkish"
    if effective < -0.5:
        return "dovish"
    return "neutral"


def build_outcome_band(event: EconomicEvent) -> dict:
    """The diverging miss<->beat band that drives the event card's hero
    visualization: consensus at the center, the AI's likely range either
    side of it, and -- once released -- where the actual print landed,
    expressed as a z-score against this release's own expected spread so
    the band is scaled to the event, not an arbitrary fixed axis.
    """
    sigma = _band_sigma(event)
    inverted = event.name in INVERTED_EVENTS
    sign = -1 if inverted else 1

    ai_z = round((event.ai_estimate - event.consensus) / sigma, 2) if (sigma and event.ai_estimate is not None and event.consensus is not None) else None

    actual_z = None
    effective_z = None
    magnitude = None
    policy_lean = None
    if sigma and event.actual is not None and event.consensus is not None:
        actual_z = round((event.actual - event.consensus) / sigma, 2)
        effective_z = round(sign * actual_z, 2)
        magnitude = _magnitude(abs(actual_z))
        policy_lean = _policy_lean(actual_z, inverted)

    return {
        "unit": event.unit,
        "previous": event.previous,
        "consensus": event.consensus,
        "low": event.ai_estimate_low,
        "high": event.ai_estimate_high,
        "ai_estimate": event.ai_estimate,
        "ai_estimate_z": ai_z,
        # effective_z / effective_range are ai_z and [-1, 1] rotated by `sign` so the
        # horizontal position on the outcome band always means "dovish <-> hawkish",
        # regardless of whether the underlying metric is inverted -- the frontend
        # should plot position from these, not from the raw z-scores above.
        "ai_estimate_effective_z": round(sign * ai_z, 2) if ai_z is not None else None,
        "effective_range": [sign * -1.0, sign * 1.0] if sigma else None,
        "actual": event.actual,
        "actual_z": actual_z,
        "effective_z": effective_z,
        "magnitude": magnitude,
        "policy_lean": policy_lean,
        "inverted": inverted,
        "basis": "heuristic",
        "disclosure": HEURISTIC_DISCLOSURE,
    }


def generate_pre_event_scenario(event: EconomicEvent) -> dict:
    """Builds the "before the release" intelligence briefing: expected number,
    likely range, surprise probabilities, and what each scenario means for
    the major assets it affects.
    """
    impacts = CATEGORY_ASSET_IMPACT.get(event.category, {})

    def scenario_impacts(hot: bool) -> dict:
        sign = 1 if hot else -1
        return {
            symbol: ("bullish" if sign * weight > 0 else "bearish" if sign * weight < 0 else "neutral")
            for symbol, weight in impacts.items()
        }

    return {
        "event": event.name,
        "country": event.country,
        "scheduled_at": event.scheduled_at.isoformat(),
        "consensus": event.consensus,
        "ai_estimate": event.ai_estimate,
        "likely_range": [event.ai_estimate_low, event.ai_estimate_high],
        "probabilities": {
            "hot": event.prob_upside_surprise,
            "cool": event.prob_downside_surprise,
            "in_line": event.prob_inline,
        },
        "outcome_band": build_outcome_band(event),
        "basis": "heuristic",
        "disclosure": HEURISTIC_DISCLOSURE,
        "education": get_education(event.name, event.category).__dict__,
        "scenarios": {
            "hot": {"description": f"{event.name} prints above consensus", "asset_impact": scenario_impacts(True)},
            "cool": {"description": f"{event.name} prints below consensus", "asset_impact": scenario_impacts(False)},
            "base": {"description": f"{event.name} prints in line with consensus", "asset_impact": {s: "neutral" for s in impacts}},
        },
    }


def record_post_release_reaction(db: Session, event: EconomicEvent) -> dict:
    """Compares the forecast with the actual print and drafts the immediate
    post-release read (spec step 5). Requires the event to already be marked
    'released' with an actual value.
    """
    if event.actual is None or event.consensus is None:
        return {"error": "event has no actual/consensus to compare"}

    surprise = event.surprise if event.surprise is not None else round(event.actual - event.consensus, 3)
    direction = "hot" if surprise > 0 else "cool" if surprise < 0 else "in_line"
    impacts = CATEGORY_ASSET_IMPACT.get(event.category, {})
    sign = 1 if direction == "hot" else -1 if direction == "cool" else 0
    asset_reaction = {
        symbol: ("bullish" if sign * weight > 0 else "bearish" if sign * weight < 0 else "neutral")
        for symbol, weight in impacts.items()
    }

    return {
        "event": event.name,
        "forecast": event.consensus,
        "actual": event.actual,
        "surprise": surprise,
        "surprise_direction": direction,
        "expected_asset_reaction": asset_reaction,
        "outcome_band": build_outcome_band(event),
        "basis": "heuristic",
        "disclosure": HEURISTIC_DISCLOSURE,
        "education": get_education(event.name, event.category).__dict__,
        "note": "Compare expected_asset_reaction against realized price moves to check whether "
                "the market followed the textbook relationship or diverged (regime-dependent).",
    }


def record_prediction(
    db: Session,
    symbol: str,
    direction: str,
    probability: float,
    confidence: str,
    reasoning: str,
    main_risk: str = "",
    invalidation: str = "",
    horizon_hours: float = 24.0,
    linked_event_id: int | None = None,
) -> Prediction:
    prediction = Prediction(
        symbol=symbol,
        direction=direction,
        probability=probability,
        confidence=confidence,
        reasoning=reasoning,
        main_risk=main_risk,
        invalidation=invalidation,
        horizon_hours=horizon_hours,
        linked_event_id=linked_event_id,
        resolves_at=datetime.now(timezone.utc) + timedelta(hours=horizon_hours),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def resolve_due_predictions(db: Session) -> int:
    """Checks predictions past their resolution horizon, compares direction
    against realized price change, and records calibration data (Brier score
    component) -- the mechanism behind spec step 10.
    """
    now = datetime.now(timezone.utc)
    due = (
        db.query(Prediction)
        .filter(Prediction.resolves_at <= now)
        .outerjoin(PredictionOutcome, PredictionOutcome.prediction_id == Prediction.id)
        .filter(PredictionOutcome.id.is_(None))
        .all()
    )

    resolved = 0
    for pred in due:
        history = market_data.price_history(db, pred.symbol, limit=400)
        if len(history) < 2:
            continue

        price_then = next((b.close for b in history if b.ts >= pred.created_at), history[0].close)
        price_now = history[-1].close
        change = (price_now - price_then) / price_then if price_then else 0.0

        if change > 0.002:
            actual_direction = "bullish"
        elif change < -0.002:
            actual_direction = "bearish"
        else:
            actual_direction = "neutral"

        correct = actual_direction == pred.direction
        outcome_value = 1.0 if correct else 0.0
        brier = (pred.probability - outcome_value) ** 2

        db.add(
            PredictionOutcome(
                prediction_id=pred.id,
                price_at_prediction=price_then,
                price_at_resolution=price_now,
                actual_direction=actual_direction,
                correct=correct,
                brier_component=brier,
            )
        )
        resolved += 1

    db.commit()
    return resolved


def calibration_stats(db: Session) -> dict:
    outcomes = db.query(PredictionOutcome).all()
    if not outcomes:
        return {"n": 0, "hit_rate": None, "brier_score": None}
    n = len(outcomes)
    hit_rate = sum(1 for o in outcomes if o.correct) / n
    brier_score = sum(o.brier_component for o in outcomes) / n
    return {"n": n, "hit_rate": round(hit_rate, 3), "brier_score": round(brier_score, 4)}
