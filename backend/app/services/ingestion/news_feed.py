"""News ingestion via public RSS feeds (no API key required).

Sentiment is a naive lexicon-based score in [-1, +1] -- good enough to feed
directionally into the intelligence score, not a substitute for a proper
NLP/FinBERT sentiment model in production. Fact-tiering (confirmed / reported
/ rumor, per spec step 2) defaults to "reported" for wire-service headlines;
a licensed news feed with structured metadata could set this more precisely.
"""

import logging
from datetime import datetime, timezone

import feedparser
from sqlalchemy.orm import Session

from app.models.news import NewsItem

logger = logging.getLogger(__name__)

FEEDS = {
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Investing.com": "https://www.investing.com/rss/news.rss",
    "FXStreet": "https://www.fxstreet.com/rss/news",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
}

TAG_KEYWORDS = {
    "gold": ["gold", "xau", "bullion"],
    "fed": ["fed ", "federal reserve", "fomc", "powell"],
    "inflation": ["inflation", "cpi", "pce"],
    "usd": ["dollar", "usd", "dxy"],
    "oil": ["oil", "crude", "opec", "wti", "brent"],
    "equities": ["stocks", "s&p", "nasdaq", "dow jones", "equities"],
    "crypto": ["bitcoin", "btc", "ethereum", "crypto"],
    "rates": ["yield", "treasury", "interest rate", "bond"],
    "geopolitics": ["war", "conflict", "sanctions", "ceasefire", "military", "geopolitical"],
}

POSITIVE_WORDS = {
    "surge", "rally", "gain", "gains", "rise", "rises", "rose", "beat", "beats", "strong",
    "growth", "recovery", "optimism", "boost", "upgrade", "record high", "cooling inflation",
    "ceasefire", "de-escalate", "de-escalation",
}
NEGATIVE_WORDS = {
    "plunge", "slump", "fall", "falls", "fell", "crash", "miss", "misses", "weak", "recession",
    "fear", "fears", "downgrade", "selloff", "sell-off", "war", "conflict", "sanctions",
    "hawkish", "default", "crisis", "escalate", "escalation",
}


def _score_sentiment(text: str) -> float:
    lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in lower)
    if pos == 0 and neg == 0:
        return 0.0
    return round((pos - neg) / max(pos + neg, 1), 2)


def _tag(text: str) -> list[str]:
    lower = text.lower()
    return [tag for tag, keywords in TAG_KEYWORDS.items() if any(k in lower for k in keywords)]


def fetch_and_store_news(db: Session, feeds: dict[str, str] | None = None, limit_per_feed: int = 30) -> int:
    feeds = feeds or FEEDS
    written = 0

    for source, url in feeds.items():
        try:
            parsed = feedparser.parse(url)
        except Exception as exc:
            logger.warning("news_feed: failed to fetch %s: %s", source, exc)
            continue

        for entry in parsed.entries[:limit_per_feed]:
            link = entry.get("link")
            title = entry.get("title")
            if not link or not title:
                continue
            if db.query(NewsItem).filter(NewsItem.url == link).first():
                continue

            published = entry.get("published_parsed") or entry.get("updated_parsed")
            published_at = (
                datetime(*published[:6], tzinfo=timezone.utc) if published else datetime.now(timezone.utc)
            )

            item = NewsItem(
                source=source,
                title=title,
                url=link,
                published_at=published_at,
                tags=",".join(_tag(title)),
                sentiment=_score_sentiment(title),
                fact_tier="reported",
            )
            db.add(item)
            written += 1

    db.commit()
    logger.info("news_feed: wrote %d new items", written)
    return written


def latest_news(db: Session, limit: int = 50, tag: str | None = None) -> list[NewsItem]:
    query = db.query(NewsItem)
    if tag:
        query = query.filter(NewsItem.tags.contains(tag))
    return query.order_by(NewsItem.published_at.desc()).limit(limit).all()
