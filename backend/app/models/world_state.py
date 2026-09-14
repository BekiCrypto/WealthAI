from datetime import datetime, timezone

from sqlalchemy import DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WorldStateSnapshot(Base):
    """A point-in-time snapshot of the AI's live understanding of the global
    macro/market environment (spec step 8: risk regime, inflation, USD, yields,
    oil, gold, equities, crypto, geopolitical risk, plus per-asset intelligence
    scores and the reasoning behind each field).
    """

    __tablename__ = "world_state_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    regime: Mapped[dict] = mapped_column(JSON)  # {risk_regime, inflation, usd, yields, oil, gold, equities, crypto, geopolitical_risk}
    scores: Mapped[dict] = mapped_column(JSON)  # {symbol: {bullish_pct, confidence, macro, technical, sentiment, geopolitical, reasons: [...]}}
    reasoning: Mapped[dict] = mapped_column(JSON, default=dict)  # narrative explanation per regime field
