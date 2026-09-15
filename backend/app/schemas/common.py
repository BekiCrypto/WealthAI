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
    source: str

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
    """Internally, every field is always populated by compute_snapshot() so
    macro_brain/intelligence_score can reason over real numbers regardless of
    licensing. `redistributable`/`price_disclosure` default to the
    full-fidelity internal case; routers/assets.py builds a gated copy for
    the public API response when the symbol's provider isn't redistributable
    (see services/ingestion/providers.py).
    """

    symbol: str
    redistributable: bool = True
    price_disclosure: str | None = None
    last_price: float | None
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


class TradeSetup(BaseModel):
    """A concrete entry/stop/target derived from the Intelligence Score and
    price structure -- spec step 9's "highest-probability setup," not just
    an abstract bullish/bearish call. `entry_price`/`stop_price`/
    `target_price` are withheld (null) for non-redistributable symbols, same
    as TechnicalSnapshot; the `_pct_from_*` ratio fields are our own derived
    output and are always shown regardless of licensing.
    """

    symbol: str
    redistributable: bool = True
    price_disclosure: str | None = None
    direction: str  # long, short, none
    setup_type: str | None
    confidence: str
    probability: float
    entry_price: float | None
    stop_price: float | None
    target_price: float | None
    risk_reward: float | None
    entry_pct_from_last: float | None
    stop_pct_from_entry: float | None
    target_pct_from_entry: float | None
    reasoning: str
    invalidation: str
    main_risk: str


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    used_context: dict


class IndicatorEducation(BaseModel):
    """An explicit, educational briefing on an economic indicator: what it
    is, why it matters, and how to read it -- meant to teach the reader, not
    just hand them a decision.
    """

    name: str
    category: str
    what_it_is: str
    why_it_matters: str
    market_impact_chain: str
    how_to_read: str
    historical_context: str
    watch_for: str
    inverted: bool

    model_config = {"from_attributes": True}
