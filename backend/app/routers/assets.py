from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas.common import ScoreBreakdown, TechnicalSnapshot
from app.services.analysis import technical
from app.services.analysis.intelligence_score import compute_all_scores, compute_intelligence_score
from app.services.ingestion import market_data

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
    return snapshot


@router.get("/{symbol}/score", response_model=ScoreBreakdown)
def intelligence_score(symbol: str, db: Session = Depends(get_db)):
    score = compute_intelligence_score(db, symbol)
    if score is None:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol} yet")
    return score


@router.get("/{symbol}/prices")
def prices(symbol: str, limit: int = 300, db: Session = Depends(get_db)):
    bars = market_data.price_history(db, symbol, limit=limit)
    return [
        {"ts": b.ts.isoformat(), "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume}
        for b in bars
    ]
