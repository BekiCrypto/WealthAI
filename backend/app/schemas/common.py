from datetime import datetime

from pydantic import BaseModel


class EventOut(BaseModel):
    id: int
    name: str
    country: str
    category: str
    importance: str
    scheduled_at: datetime
    previous: float | None = None
    consensus: float | None = None
    ai_estimate: float | None = None
    ai_estimate_low: float | None = None
    ai_estimate_high: float | None = None
    prob_upside_surprise: float | None = None
    prob_downside_surprise: float | None = None
    prob_inline: float | None = None
    actual: float | None = None
    surprise: float | None = None
    unit: str
    status: str

    model_config = {"from_attributes": True}


class NewsOut(BaseModel):
    id: int
    source: str
    title: str
    url: str
    published_at: datetime
    tags: str
    sentiment: float
    fact_tier: str

    model_config = {"from_attributes": True}


class ScoreBreakdown(BaseModel):
    symbol: str
    bullish_pct: float
    confidence: str
    macro: str
    technical: str
    sentiment: str
    geopolitical: str
    reasons: list[str]


class WorldStateOut(BaseModel):
    created_at: datetime
    regime: dict
    scores: dict
    reasoning: dict

    model_config = {"from_attributes": True}


class TechnicalSnapshot(BaseModel):
    symbol: str
    last_price: float
    trend: str
    rsi_14: float | None = None
    sma_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    ema_20: float | None = None
    atr_14: float | None = None
    support: float | None = None
    resistance: float | None = None
    volatility_20d: float | None = None


class PredictionOut(BaseModel):
    id: int
    created_at: datetime
    symbol: str
    direction: str
    probability: float
    confidence: str
    reasoning: str
    main_risk: str
    invalidation: str
    horizon_hours: float

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    used_context: dict
