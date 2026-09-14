"""The Intelligence Score (spec step 7): combines macro, technical, sentiment
and geopolitical signals into a single bullish/bearish read per asset, with
the reasons behind it surfaced to the user rather than a bare number.
"""

from sqlalchemy.orm import Session

from app.models.news import NewsItem
from app.services.analysis import technical
from app.services.analysis.macro_brain import classify_world_state
from app.services.ingestion import market_data
from app.schemas.common import ScoreBreakdown

DIRECTION_VALUE = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0, "unknown": 0.0}

# How each regime field translates into a directional lean for a given asset.
MACRO_MAP = {
    "GC=F": lambda r: (
        DIRECTION_VALUE.get({"bullish": "bearish", "bearish": "bullish", "neutral": "neutral"}.get(r["usd"], "neutral"), 0.0) * 0.5
        + DIRECTION_VALUE.get({"bullish": "bearish", "bearish": "bullish", "neutral": "neutral"}.get(r["yields"], "neutral"), 0.0) * 0.3
        + (0.6 if r["geopolitical_risk"] in ("high", "elevated") else 0.0)
    ),
    "CL=F": lambda r: (0.5 if r["geopolitical_risk"] == "high" else 0.2 if r["geopolitical_risk"] == "elevated" else 0.0)
    + (0.3 if r["risk_regime"] == "Risk-On" else -0.2 if r["risk_regime"] == "Risk-Off" else 0.0),
    "^GSPC": lambda r: (-0.6 if r["risk_regime"] == "Risk-Off" else 0.5 if r["risk_regime"] == "Risk-On" else 0.0)
    + DIRECTION_VALUE.get({"bullish": "bearish", "bearish": "bullish", "neutral": "neutral"}.get(r["yields"], "neutral"), 0.0) * 0.3,
    "BTC-USD": lambda r: (-0.5 if r["risk_regime"] == "Risk-Off" else 0.4 if r["risk_regime"] == "Risk-On" else 0.0)
    + DIRECTION_VALUE.get({"bullish": "bearish", "bearish": "bullish", "neutral": "neutral"}.get(r["usd"], "neutral"), 0.0) * 0.3,
    "ETH-USD": lambda r: (-0.5 if r["risk_regime"] == "Risk-Off" else 0.4 if r["risk_regime"] == "Risk-On" else 0.0),
    "EURUSD=X": lambda r: DIRECTION_VALUE.get({"bullish": "bearish", "bearish": "bullish", "neutral": "neutral"}.get(r["usd"], "neutral"), 0.0),
    "DX-Y.NYB": lambda r: DIRECTION_VALUE.get(r["usd"], 0.0),
}

SENTIMENT_TAG = {
    "GC=F": "gold",
    "CL=F": "oil",
    "^GSPC": "equities",
    "BTC-USD": "crypto",
    "ETH-USD": "crypto",
    "EURUSD=X": "usd",
    "DX-Y.NYB": "usd",
}


def _sentiment_lean(db: Session, symbol: str) -> tuple[str, float]:
    tag = SENTIMENT_TAG.get(symbol)
    if not tag:
        return "neutral", 0.0
    items = db.query(NewsItem).filter(NewsItem.tags.contains(tag)).order_by(NewsItem.published_at.desc()).limit(20).all()
    if not items:
        return "neutral", 0.0
    avg = sum(i.sentiment for i in items) / len(items)
    if avg > 0.15:
        return "bullish", avg
    if avg < -0.15:
        return "bearish", avg
    return "neutral", avg


def _lean_label(value: float) -> str:
    if value > 0.15:
        return "bullish"
    if value < -0.15:
        return "bearish"
    return "neutral"


def compute_intelligence_score(db: Session, symbol: str) -> ScoreBreakdown | None:
    bars = market_data.price_history(db, symbol, limit=300)
    snapshot = technical.compute_snapshot(symbol, bars)
    if snapshot is None:
        return None

    tech_direction = technical.technical_bias(snapshot)
    tech_value = DIRECTION_VALUE[tech_direction]

    world = classify_world_state(db)
    regime = world["regime"]
    macro_value = MACRO_MAP.get(symbol, lambda r: 0.0)(regime)
    macro_value = max(-1.0, min(1.0, macro_value))
    macro_direction = _lean_label(macro_value)

    sentiment_direction, sentiment_value = _sentiment_lean(db, symbol)

    geo_level = regime["geopolitical_risk"]
    geo_map_direction = {
        "GC=F": "bullish" if geo_level != "low" else "neutral",
        "CL=F": "bullish" if geo_level != "low" else "neutral",
        "^GSPC": "bearish" if geo_level == "high" else "neutral",
        "BTC-USD": "bearish" if geo_level == "high" else "neutral",
    }.get(symbol, "neutral")
    geo_value = DIRECTION_VALUE[geo_map_direction]

    # Weighted blend: technical and macro carry the most weight, sentiment and
    # geopolitics act as tilts. Weights are intentionally simple/explainable.
    combined = tech_value * 0.4 + macro_value * 0.35 + sentiment_value * 0.15 + geo_value * 0.10
    bullish_pct = round((combined + 1) / 2 * 100, 1)

    directions = [tech_direction, macro_direction, sentiment_direction, geo_map_direction]
    bullish_votes = directions.count("bullish")
    bearish_votes = directions.count("bearish")
    agreement = max(bullish_votes, bearish_votes)
    confidence = "High" if agreement >= 3 else "Medium" if agreement == 2 else "Low"

    reasons = [
        f"Technical: {tech_direction} (trend={snapshot.trend}, RSI14={snapshot.rsi_14})",
        f"Macro: {macro_direction} given risk regime={regime['risk_regime']}, USD={regime['usd']}, yields={regime['yields']}",
        f"Sentiment: {sentiment_direction} (avg headline sentiment {sentiment_value:+.2f} over last 20 stories)",
        f"Geopolitical: {geo_map_direction} (risk level={geo_level}, score={regime['geopolitical_risk_score']}/100)",
    ]

    return ScoreBreakdown(
        symbol=symbol,
        bullish_pct=bullish_pct,
        confidence=confidence,
        macro=macro_direction,
        technical=tech_direction,
        sentiment=sentiment_direction,
        geopolitical=geo_map_direction,
        reasons=reasons,
    )


def compute_all_scores(db: Session, symbols: list[str]) -> dict:
    scores = {}
    for symbol in symbols:
        score = compute_intelligence_score(db, symbol)
        if score is not None:
            scores[symbol] = score.model_dump()
    return scores
