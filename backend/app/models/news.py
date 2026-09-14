from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, unique=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    tags: Mapped[str] = mapped_column(String(256), default="")  # comma-separated: gold,fed,inflation
    sentiment: Mapped[float] = mapped_column(Float, default=0.0)  # -1..+1, naive lexicon score
    fact_tier: Mapped[str] = mapped_column(String(16), default="reported")  # confirmed, reported, rumor
