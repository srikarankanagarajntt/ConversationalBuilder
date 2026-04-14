from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.api import health, conversation, voice, upload, template, preview, export, cache
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.services.state_service import get_state_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Async background task for session cleanup (replaces APScheduler)
_cleanup_task: asyncio.Task | None = None
_cleanup_stop_event = asyncio.Event()

async def _cleanup_sessions_periodically() -> None:
    """Background task to cleanup expired sessions every 30 minutes."""
    while not _cleanup_stop_event.is_set():
        try:
            state_service = get_state_service()
            removed_count = state_service.cleanup_expired_sessions()
            logger.info(f"Session cleanup task executed. Removed {removed_count} expired sessions.")
        except Exception as e:
            logger.exception(f"Failed during session cleanup: {e}")
        # Wait up to 30 minutes, or exit early if stop event is set
        try:
            await asyncio.wait_for(_cleanup_stop_event.wait(), timeout=1800)
        except asyncio.TimeoutError:
            # Timeout -> run next cycle
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _cleanup_task
    # Startup event
    try:
        _cleanup_stop_event.clear()
        _cleanup_task = asyncio.create_task(_cleanup_sessions_periodically())
        logger.info("✅ Background session cleanup task started (30-minute interval)")
    except Exception as e:
        logger.error(f"❌ Failed to start cleanup task: {e}")

    yield

    # Shutdown event
    _cleanup_stop_event.set()
    if _cleanup_task:
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("🛑 Background cleanup task shutdown")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Conversational CV Builder backend skeleton using NTT template aligned canonical CV schema.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router, tags=["health"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["conversation"])
app.include_router(cache.router, prefix="/api/cache", tags=["cache"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(template.router, prefix="/api/template", tags=["template"])
app.include_router(preview.router, prefix="/api/preview", tags=["preview"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"message": "Conversational CV Builder API is running."}
