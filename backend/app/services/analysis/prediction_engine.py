"""Prediction engine: pre-event scenario analysis (spec step 4), post-release
reaction (spec step 5), and calibration tracking (spec step 10) so the system
learns which signals actually work over thousands of predictions.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.event import EconomicEvent
from app.models.prediction import Prediction, PredictionOutcome
from app.services.ingestion import market_data

# Which assets each event category is expected to move, and in which
# direction *if* the print comes in hot (above consensus). Cool prints imply
# the opposite. This is the explainable link between "what happened" and
# "what it means for markets" (spec step 4/6).
CATEGORY_ASSET_IMPACT = {
    "inflation": {"GC=F": -1, "DX-Y.NYB": 1, "^GSPC": -1, "BTC-USD": -1, "^TNX": 1},
    "employment": {"GC=F": -1, "DX-Y.NYB": 1, "^GSPC": 0, "^TNX": 1},
    "growth": {"GC=F": 0, "^GSPC": 1, "DX-Y.NYB": 0.3},
    "central_bank": {"GC=F": -1, "DX-Y.NYB": 1, "^GSPC": -1, "^TNX": 1, "BTC-USD": -1},
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
