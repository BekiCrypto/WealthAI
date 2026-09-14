from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EconomicEvent(Base):
    """A scheduled macro/economic release or central-bank event.

    Tracks the full lifecycle: consensus forecast -> AI estimate -> actual print,
    so the prediction engine can compare its pre-release scenario analysis
    against what really happened.
    """

    __tablename__ = "economic_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))  # e.g. "US CPI YoY"
    country: Mapped[str] = mapped_column(String(8))  # ISO country code, e.g. "US"
    category: Mapped[str] = mapped_column(String(64))  # inflation, employment, central_bank, growth, sentiment
    importance: Mapped[str] = mapped_column(String(16), default="medium")  # low, medium, high

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    # Confirmed facts vs expectations vs AI interpretation (see spec step 2)
    previous: Mapped[float | None] = mapped_column(Float, nullable=True)
    consensus: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_estimate_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_estimate_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    prob_upside_surprise: Mapped[float | None] = mapped_column(Float, nullable=True)
    prob_downside_surprise: Mapped[float | None] = mapped_column(Float, nullable=True)
    prob_inline: Mapped[float | None] = mapped_column(Float, nullable=True)

    actual: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    surprise: Mapped[float | None] = mapped_column(Float, nullable=True)  # actual - consensus

    unit: Mapped[str] = mapped_column(String(16), default="%")
    source: Mapped[str] = mapped_column(String(64), default="seed")  # fred, manual, seed

    status: Mapped[str] = mapped_column(String(16), default="scheduled")  # scheduled, released
