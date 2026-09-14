from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prediction(Base):
    """Every prediction the AI makes gets recorded (spec step 10) so the
    system can later check calibration: over thousands of predictions, which
    signals actually work.
    """

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    symbol: Mapped[str] = mapped_column(String(32), index=True)
    direction: Mapped[str] = mapped_column(String(8))  # bullish, bearish, neutral
    probability: Mapped[float] = mapped_column(Float)  # 0..1
    confidence: Mapped[str] = mapped_column(String(16))  # low, medium, high

    reasoning: Mapped[str] = mapped_column(Text)
    main_risk: Mapped[str] = mapped_column(Text, default="")
    invalidation: Mapped[str] = mapped_column(Text, default="")

    horizon_hours: Mapped[float] = mapped_column(Float, default=24.0)
    linked_event_id: Mapped[int | None] = mapped_column(ForeignKey("economic_events.id"), nullable=True)

    resolves_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PredictionOutcome(Base):
    """The recorded resolution of a prediction, used to compute calibration
    (Brier score) so the system learns which signals work over time.
    """

    __tablename__ = "prediction_outcomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), unique=True)

    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    price_at_prediction: Mapped[float] = mapped_column(Float)
    price_at_resolution: Mapped[float] = mapped_column(Float)
    actual_direction: Mapped[str] = mapped_column(String(8))  # bullish, bearish, neutral
    correct: Mapped[bool] = mapped_column(default=False)
    brier_component: Mapped[float] = mapped_column(Float)  # (probability - outcome)^2
