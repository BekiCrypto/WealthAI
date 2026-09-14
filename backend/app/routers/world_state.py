from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.world_state import WorldStateSnapshot
from app.schemas.common import WorldStateOut
from app.services.analysis.intelligence_score import compute_all_scores
from app.services.analysis.macro_brain import classify_world_state

router = APIRouter(prefix="/world-state", tags=["world-state"])


@router.get("", response_model=WorldStateOut)
def current_world_state(db: Session = Depends(get_db)):
    world = classify_world_state(db)
    scores = compute_all_scores(db, get_settings().tracked_symbols)
    latest = db.query(WorldStateSnapshot).order_by(WorldStateSnapshot.created_at.desc()).first()
    return WorldStateOut(
        created_at=latest.created_at if latest else datetime.now(timezone.utc),
        regime=world["regime"],
        scores=scores,
        reasoning=world["reasoning"],
    )


@router.get("/history", response_model=list[WorldStateOut])
def world_state_history(limit: int = 50, db: Session = Depends(get_db)):
    snapshots = (
        db.query(WorldStateSnapshot).order_by(WorldStateSnapshot.created_at.desc()).limit(limit).all()
    )
    return list(reversed(snapshots))
