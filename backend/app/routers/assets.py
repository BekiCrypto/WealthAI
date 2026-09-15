from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas.common import ScoreBreakdown, TechnicalSnapshot, TradeSetup
from app.services.analysis import technical
from app.services.analysis.intelligence_score import compute_all_scores, compute_intelligence_score
from app.services.analysis.trade_setup import generate_trade_setup
from app.services.ingestion import market_data
from app.services.ingestion.providers import gate_technical_snapshot, gate_trade_setup, is_redistributable

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("")
def list_assets():
    return {"symbols": get_settings().tracked_symbols}


@router.get("/scores")
def all_scores(db: Session = Depends(get_db)):
    return compute_all_scores(db, get_settings().tracked_symbols)


@router.get("/{symbol}/technical", response_model=TechnicalSnapshot)
def technical_snapshot(symbol: str, db: Session = Depends(get_db)):
    bars = market_data.price_history(db, symbol, limit=300)
    snapshot = technical.compute_snapshot(symbol, bars)
    if snapshot is None:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol} yet")
    return gate_technical_snapshot(snapshot)


@router.get("/{symbol}/score", response_model=ScoreBreakdown)
def intelligence_score(symbol: str, db: Session = Depends(get_db)):
    score = compute_intelligence_score(db, symbol)
    if score is None:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol} yet")
    return score


@router.get("/setups", response_model=list[TradeSetup])
def all_trade_setups(db: Session = Depends(get_db)):
    """All tracked symbols' current setups, for a dashboard-level view of
    where the highest-probability entries are right now -- most callers
    only care about the subset with an actual direction (see
    `direction != "none"` on the frontend).
    """
    setups = []
    for symbol in get_settings().tracked_symbols:
        bars = market_data.price_history(db, symbol, limit=300)
        snapshot = technical.compute_snapshot(symbol, bars)
        score = compute_intelligence_score(db, symbol)
        if snapshot is None or score is None:
            continue
        setup = generate_trade_setup(symbol, score, snapshot)
        setups.append(gate_trade_setup(TradeSetup(**setup)))
    return setups


@router.get("/{symbol}/setup", response_model=TradeSetup)
def trade_setup(symbol: str, db: Session = Depends(get_db)):
    """The highest-probability entry/exit signal for this symbol right now
    (spec step 9), or direction="none" if the score is too close to neutral
    or too low-confidence to act on. Uses the full-fidelity technical
    snapshot internally to size the stop/target correctly, then gates the
    *response* the same way /technical does.
    """
    bars = market_data.price_history(db, symbol, limit=300)
    snapshot = technical.compute_snapshot(symbol, bars)
    score = compute_intelligence_score(db, symbol)
    if snapshot is None or score is None:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol} yet")
    setup = generate_trade_setup(symbol, score, snapshot)
    return gate_trade_setup(TradeSetup(**setup))


@router.get("/{symbol}/prices")
def prices(symbol: str, limit: int = 300, db: Session = Depends(get_db)):
    if not is_redistributable(symbol):
        raise HTTPException(
            status_code=403,
            detail=(
                f"Raw price history for {symbol} isn't shown: its data provider's free tier "
                "isn't licensed for public redistribution. Use /assets/{symbol}/technical or "
                "/assets/{symbol}/score for derived analysis instead."
            ),
        )
    bars = market_data.price_history(db, symbol, limit=limit)
    return [
        {"ts": b.ts.isoformat(), "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume}
        for b in bars
    ]
