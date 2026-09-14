from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prediction import Prediction
from app.schemas.common import PredictionOut
from app.services.analysis.prediction_engine import calibration_stats, record_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", response_model=list[PredictionOut])
def list_predictions(symbol: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Prediction)
    if symbol:
        query = query.filter(Prediction.symbol == symbol)
    return query.order_by(Prediction.created_at.desc()).limit(limit).all()


@router.post("", response_model=PredictionOut)
def create_prediction(
    symbol: str,
    direction: str,
    probability: float,
    confidence: str,
    reasoning: str,
    main_risk: str = "",
    invalidation: str = "",
    horizon_hours: float = 24.0,
    db: Session = Depends(get_db),
):
    return record_prediction(
        db, symbol, direction, probability, confidence, reasoning, main_risk, invalidation, horizon_hours
    )


@router.get("/calibration")
def calibration(db: Session = Depends(get_db)):
    return calibration_stats(db)
