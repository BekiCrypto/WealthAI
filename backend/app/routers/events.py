from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import EconomicEvent
from app.schemas.common import EventOut
from app.services.analysis.prediction_engine import generate_pre_event_scenario, record_post_release_reaction
from app.services.ingestion.economic_calendar import upcoming_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/calendar", response_model=list[EventOut])
def calendar(hours_ahead: int = 24 * 14, db: Session = Depends(get_db)):
    return upcoming_events(db, hours_ahead=hours_ahead)


@router.get("/{event_id}/scenario")
def scenario(event_id: int, db: Session = Depends(get_db)):
    event = db.get(EconomicEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    return generate_pre_event_scenario(event)


@router.get("/{event_id}/reaction")
def reaction(event_id: int, db: Session = Depends(get_db)):
    event = db.get(EconomicEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    return record_post_release_reaction(db, event)
