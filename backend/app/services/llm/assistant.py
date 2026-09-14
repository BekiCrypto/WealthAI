"""Lets users ask the AI free-text questions (spec step 9), answered from the
live world state / intelligence scores / calendar rather than the model's
general knowledge alone. Degrades to a deterministic templated answer if no
ANTHROPIC_API_KEY is configured, so the rest of the app stays usable without
a key.
"""

import json

from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.analysis.intelligence_score import compute_all_scores
from app.services.analysis.macro_brain import classify_world_state
from app.services.ingestion.economic_calendar import upcoming_events
from app.services.ingestion.news_feed import latest_news

SYSTEM_PROMPT = """You are the WealthAI Market Intelligence assistant. You are given a live \
snapshot of the world state (macro regime), per-asset intelligence scores, upcoming economic \
events, and recent headlines. Answer the user's question using ONLY this context plus your \
general financial knowledge for explanation -- do not invent live prices, data prints, or news \
you were not given. Structure answers around: what happened -> why it matters -> what the \
market expects -> what might happen next -> your confidence -> what would prove you wrong. \
Keep answers concise and concrete. Never give this as individual financial advice; frame \
everything as probabilistic intelligence, not certainty."""


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
        }
        for e in upcoming_events(db)
    ]
    news = [
        {"source": n.source, "title": n.title, "published_at": n.published_at.isoformat(), "sentiment": n.sentiment}
        for n in latest_news(db, limit=20)
    ]
    return {"world_state": world, "intelligence_scores": scores, "upcoming_events": events, "recent_news": news}


def _fallback_answer(query: str, context: dict) -> str:
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
    if context["upcoming_events"]:
        next_event = context["upcoming_events"][0]
        lines.append(
            f"Next major event: {next_event['name']} ({next_event['country']}) at {next_event['scheduled_at']}, "
            f"consensus {next_event['consensus']}, AI estimate {next_event['ai_estimate']}."
        )
    lines.append(f"Your question was: \"{query}\" -- set ANTHROPIC_API_KEY to get a full narrative answer.")
    return "\n".join(lines)


def answer_query(db: Session, query: str) -> tuple[str, dict]:
    context = build_context(db)
    settings = get_settings()

    if not settings.anthropic_api_key:
        return _fallback_answer(query, context), context

    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
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
    answer = "".join(block.text for block in message.content if block.type == "text")
    return answer, context
