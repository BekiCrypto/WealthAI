from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GeoEvent(Base):
    """A geopolitical event, sourced primarily from GDELT's public event stream."""

    __tablename__ = "geo_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    actor1: Mapped[str] = mapped_column(String(128), default="")
    actor2: Mapped[str] = mapped_column(String(128), default="")
    event_code: Mapped[str] = mapped_column(String(16), default="")  # CAMEO code
    event_description: Mapped[str] = mapped_column(String(256), default="")
    goldstein_scale: Mapped[float] = mapped_column(Float, default=0.0)  # -10 (conflict) .. +10 (cooperation)
    avg_tone: Mapped[float] = mapped_column(Float, default=0.0)
    location: Mapped[str] = mapped_column(String(128), default="")
    url: Mapped[str] = mapped_column(Text, default="")
