from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import NewsOut
from app.services.ingestion.news_feed import latest_news

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/latest", response_model=list[NewsOut])
def news_latest(tag: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    return latest_news(db, limit=limit, tag=tag)
