"""Lets users ask the AI free-text questions (spec step 9), answered from the
live world state / intelligence scores / calendar rather than the model's
general knowledge alone. Degrades to a deterministic templated answer if no
ANTHROPIC_API_KEY is configured, or if the configured key fails at request
time (bad credentials, no credits, rate limiting, a network blip) -- a key
being *present* is not a guarantee every call succeeds, and chat should stay
usable either way rather than surfacing a raw 500.
"""

import json
import logging

from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.common import TradeSetup
from app.services.analysis import technical
from app.services.analysis.intelligence_score import compute_all_scores, compute_intelligence_score
from app.services.analysis.macro_brain import classify_world_state
from app.services.analysis.trade_setup import generate_trade_setup
from app.services.education.glossary import get_education
from app.services.ingestion.economic_calendar import upcoming_events
from app.services.ingestion.market_data import price_history
from app.services.ingestion.news_feed import latest_news
from app.services.ingestion.providers import gate_trade_setup

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the WealthAI Market Intelligence assistant. You are given a live \
snapshot of the world state (macro regime), per-asset intelligence scores, trade setups (entry/ \
stop/target derived from each score, when one exists), upcoming economic events (each with an \
educational briefing on what the indicator is and how to read it), and recent headlines. Answer \
the user's question using ONLY this context plus your general financial knowledge for \
explanation -- do not invent live prices, data prints, or news you were not given. Structure \
answers around: what happened -> why it matters -> what the market expects -> what might happen \
next -> your confidence -> what would prove you wrong. If asked for a "setup" or "trade," use \
the trade_setups context: if a symbol's entry is null it means its provider isn't licensed for \
public redistribution -- use the percentage fields (entry_pct_from_last etc.) and risk_reward \
instead of ever inventing an absolute price. If a symbol's direction is "none," say plainly that \
there is no high-probability setup right now rather than manufacturing one. This app is \
explicitly educational: don't just hand over a call -- teach the reader the underlying mechanism \
(e.g. how a surprise in an indicator transmits through rates, currency and risk appetite to \
reach the asset in question), and flag when an indicator is "inverted" (a higher print is the \
dovish/bearish-for-hawks outcome, like the unemployment rate) since that is a common source of \
retail mistakes. Keep answers concise and concrete. Never give this as individual financial \
advice; frame everything as probabilistic intelligence, not certainty."""


def build_context(db: Session) -> dict:
    settings = get_settings()
    world = classify_world_state(db)
    scores = compute_all_scores(db, settings.tracked_symbols)
    events = [
        {
            "name": e.name,
            "country": e.country,
            "scheduled_at": e.scheduled_at.isoformat(),
            "consensus": e.consensus,
            "ai_estimate": e.ai_estimate,
            "status": e.status,
            "actual": e.actual,
            "surprise": e.surprise,
            "education": {
                "why_it_matters": get_education(e.name, e.category).why_it_matters,
                "market_impact_chain": get_education(e.name, e.category).market_impact_chain,
                "inverted": get_education(e.name, e.category).inverted,
            },
        }
        for e in upcoming_events(db)
    ]
    news = [
        {"source": n.source, "title": n.title, "published_at": n.published_at.isoformat(), "sentiment": n.sentiment}
        for n in latest_news(db, limit=20)
    ]

    trade_setups = {}
    for symbol in settings.tracked_symbols:
        bars = price_history(db, symbol, limit=300)
        snapshot = technical.compute_snapshot(symbol, bars)
        score = compute_intelligence_score(db, symbol)
        if snapshot is None or score is None:
            continue
        gated = gate_trade_setup(TradeSetup(**generate_trade_setup(symbol, score, snapshot)))
        trade_setups[symbol] = gated.model_dump()

    return {
        "world_state": world,
        "intelligence_scores": scores,
        "trade_setups": trade_setups,
        "upcoming_events": events,
        "recent_news": news,
    }


def _fallback_answer(query: str, context: dict, reason: str | None = None) -> str:
    regime = context["world_state"]["regime"]
    lines = [
        f"(No LLM key configured -- deterministic summary of live data.)",
        f"Risk regime: {regime['risk_regime']}. Inflation: {regime['inflation']}. USD: {regime['usd']}. "
        f"Yields: {regime['yields']}. Geopolitical risk: {regime['geopolitical_risk']}.",
    ]
    if context["intelligence_scores"]:
        lines.append("Intelligence scores: " + ", ".join(
            f"{sym} {s['bullish_pct']}% bullish ({s['confidence']} confidence)"
            for sym, s in context["intelligence_scores"].items()
        ))
    active_setups = {sym: s for sym, s in context["trade_setups"].items() if s["direction"] != "none"}
    if active_setups:
        lines.append("Active trade setups: " + ", ".join(
            f"{sym} {s['direction']} ({s['probability']}% probability, R:R {s['risk_reward']})"
            for sym, s in active_setups.items()
        ))
    else:
        lines.append("No high-probability trade setups across the tracked universe right now.")
    if context["upcoming_events"]:
        next_event = context["upcoming_events"][0]
        lines.append(
            f"Next major event: {next_event['name']} ({next_event['country']}) at {next_event['scheduled_at']}, "
            f"consensus {next_event['consensus']}, AI estimate {next_event['ai_estimate']}."
        )
    lines.append(f"Your question was: \"{query}\" -- {reason or 'set ANTHROPIC_API_KEY to get a full narrative answer.'}")
    return "\n".join(lines)


def answer_query(db: Session, query: str) -> tuple[str, dict]:
    context = build_context(db)
    settings = get_settings()

    if not settings.anthropic_api_key:
        return _fallback_answer(query, context), context

    from anthropic import APIStatusError, Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
    try:
        message = client.messages.create(
            model=settings.llm_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"LIVE CONTEXT:\n{json.dumps(context, indent=2, default=str)}\n\nQUESTION: {query}",
                }
            ],
        )
    except APIStatusError as exc:
        # A configured key is not a guarantee every call succeeds -- billing,
        # rate limits, and outages all surface here. Log the real reason,
        # but never crash the chat request over it; fall back like an unset key.
        logger.warning("assistant: Anthropic API call failed (%s): %s", exc.status_code, exc.message)
        detail = getattr(exc, "body", None)
        api_message = detail.get("error", {}).get("message") if isinstance(detail, dict) else None
        reason = f"the AI service returned an error just now ({api_message or exc.message}) -- showing a deterministic summary instead."
        return _fallback_answer(query, context, reason=reason), context
    except Exception:
        logger.exception("assistant: unexpected error calling Anthropic API")
        reason = "the AI service is unreachable right now -- showing a deterministic summary instead."
        return _fallback_answer(query, context, reason=reason), context

    answer = "".join(block.text for block in message.content if block.type == "text")
    return answer, context
