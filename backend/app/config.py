from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    app_name: str = "WealthAI Market Intelligence"
    environment: str = "development"
    api_prefix: str = "/api"
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    database_url: str = "postgresql+psycopg2://wealthai:wealthai@localhost:5432/wealthai"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    anthropic_api_key: str | None = None
    llm_model: str = "claude-sonnet-5"

    # Optional external data providers (app degrades gracefully without these)
    fred_api_key: str | None = None
    news_api_key: str | None = None

    # Scheduler intervals (seconds)
    market_data_interval: int = 300
    news_interval: int = 600
    geopolitical_interval: int = 900
    economic_calendar_interval: int = 3600
    world_state_interval: int = 300

    # Tracked universe
    tracked_symbols: List[str] = [
        "GC=F",       # Gold futures
        "CL=F",       # WTI Crude futures
        "DX-Y.NYB",   # US Dollar Index
        "^TNX",       # US 10Y Treasury yield
        "^GSPC",      # S&P 500
        "EURUSD=X",   # EUR/USD
        "BTC-USD",    # Bitcoin
        "ETH-USD",    # Ethereum
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
