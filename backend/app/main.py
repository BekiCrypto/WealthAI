import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import assets, chat, events, health, news, predictions, world_state
from app.scheduler import bootstrap, create_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()
scheduler = create_scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models  # noqa: F401 -- ensure all models are registered before create_all

    Base.metadata.create_all(bind=engine)
    bootstrap()
    scheduler.start()
    logger.info("WealthAI backend started, scheduler running")
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(assets.router, prefix=settings.api_prefix)
app.include_router(events.router, prefix=settings.api_prefix)
app.include_router(world_state.router, prefix=settings.api_prefix)
app.include_router(predictions.router, prefix=settings.api_prefix)
app.include_router(news.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "live", "docs": "/docs"}
