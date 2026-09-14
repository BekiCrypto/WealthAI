"""The Macro Brain (spec step 3 + step 8).

Holds a library of textbook macro relationships (inflation -> Fed expectations
-> yields -> USD -> gold/equities/crypto, etc.) but never applies them
blindly: `classify_world_state` always re-derives each regime field from the
*current* technical trend and recent surprises in the DB, and only uses the
relationship map to explain *why* a field is set the way it is. This is the
"checks historical market reactions and current market regime" behavior the
spec calls for, implemented as an explainable rules engine -- the natural
place to later swap in a learned/statistical model without changing the
downstream World State schema.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.event import EconomicEvent
from app.services.analysis import technical
from app.services.ingestion import geopolitical, market_data

# Textbook relationships kept as documentation/reasoning hints, not hard rules.
RELATIONSHIP_NOTES = {
    "inflation_up": "Inflation surprises higher tend to lift Fed-hike expectations and yields, "
                    "which typically supports USD and pressures Gold/equities/crypto.",
    "yields_up": "Rising yields raise the opportunity cost of holding non-yielding assets "
                 "(Gold) and growth equities, and often strengthen USD.",
    "geopolitical_risk_up": "Escalating geopolitical risk typically drives safe-haven demand "
                            "(Gold, sometimes USD/JPY/CHF) and pressures risk assets (equities, "
                            "high-beta crypto).",
    "usd_up": "A stronger dollar is a headwind for USD-denominated commodities (Gold, Oil) "
              "and for crypto risk appetite.",
}

SYMBOL_ROLE = {
    "DX-Y.NYB": "usd",
    "^TNX": "yields",
    "CL=F": "oil",
    "GC=F": "gold",
    "^GSPC": "equities",
    "BTC-USD": "crypto",
    "EURUSD=X": "eurusd",
    "ETH-USD": "eth",
}


def _bias_for(db: Session, symbol: str) -> tuple[str, technical.TechnicalSnapshot | None]:
    bars = market_data.price_history(db, symbol, limit=300)
    snapshot = technical.compute_snapshot(symbol, bars)
    if snapshot is None:
        return "unknown", None
    return technical.technical_bias(snapshot), snapshot


def _inflation_regime(db: Session) -> tuple[str, str]:
    latest_cpi = (
        db.query(EconomicEvent)
        .filter(EconomicEvent.name.ilike("%CPI%"), EconomicEvent.status == "released")
        .order_by(EconomicEvent.actual_released_at.desc())
        .first()
    )
    if latest_cpi is None or latest_cpi.surprise is None:
        return "unknown", "No released CPI print yet to gauge the inflation trend."
    if latest_cpi.surprise > 0.05:
        return "elevated", f"Latest CPI surprised to the upside by {latest_cpi.surprise:+.2f} vs consensus."
    if latest_cpi.surprise < -0.05:
        return "cooling", f"Latest CPI surprised to the downside by {latest_cpi.surprise:+.2f} vs consensus."
    return "stable", "Latest CPI printed close to consensus."


def classify_world_state(db: Session) -> dict:
    usd_bias, _ = _bias_for(db, "DX-Y.NYB")
    yields_bias, _ = _bias_for(db, "^TNX")
    oil_bias, _ = _bias_for(db, "CL=F")
    gold_bias, _ = _bias_for(db, "GC=F")
    equities_bias, _ = _bias_for(db, "^GSPC")
    crypto_bias, _ = _bias_for(db, "BTC-USD")
    inflation, inflation_reason = _inflation_regime(db)
    geo_risk = geopolitical.geopolitical_risk_score(db)

    geo_level = "high" if geo_risk >= 65 else "elevated" if geo_risk >= 45 else "low"

    # Risk regime: simple weighted vote across equities/yields/geopolitics.
    risk_off_votes = sum(
        [
            equities_bias == "bearish",
            yields_bias == "bullish",  # rising yields = tightening = risk-off pressure
            geo_level in ("high", "elevated"),
        ]
    )
    risk_regime = "Risk-Off" if risk_off_votes >= 2 else "Risk-On" if risk_off_votes == 0 else "Neutral"

    regime = {
        "risk_regime": risk_regime,
        "inflation": inflation,
        "usd": usd_bias,
        "yields": yields_bias,
        "oil": oil_bias,
        "gold": gold_bias,
        "equities": equities_bias,
        "crypto": crypto_bias,
        "geopolitical_risk": geo_level,
        "geopolitical_risk_score": geo_risk,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    reasoning = {
        "risk_regime": f"{risk_off_votes}/3 risk-off signals triggered (equities trend, yields trend, geopolitical risk).",
        "inflation": inflation_reason,
        "usd": f"USD Index (DXY) technical trend classified as {usd_bias}.",
        "yields": f"US 10Y yield technical trend classified as {yields_bias}. {RELATIONSHIP_NOTES['yields_up'] if yields_bias == 'bullish' else ''}".strip(),
        "geopolitical_risk": f"Geopolitical risk score {geo_risk}/100 from recent GDELT-sourced headlines. {RELATIONSHIP_NOTES['geopolitical_risk_up'] if geo_level != 'low' else ''}".strip(),
        "gold": f"Gold technical trend classified as {gold_bias}, considered alongside USD ({usd_bias}) and yields ({yields_bias}).",
    }

    return {"regime": regime, "reasoning": reasoning}
