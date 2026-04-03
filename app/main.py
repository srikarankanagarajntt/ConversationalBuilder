from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from app.api import health, conversation, voice, upload, template, preview, export, cache
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.services.state_service import get_state_service

logger = logging.getLogger(__name__)
settings = get_settings()

# Background scheduler for session cleanup
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    try:
        scheduler.add_job(
            cleanup_sessions,
            "interval",
            minutes=30,
            id="cleanup_sessions",
            name="Cleanup expired sessions every 30 minutes"
        )
        scheduler.start()
        logger.info("✅ Background session cleanup scheduler started (30-minute interval)")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")

    yield

    # Shutdown event
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Background scheduler shutdown")

def cleanup_sessions():
    """Background task to cleanup expired sessions every 30 minutes."""
    state_service = get_state_service()
    removed_count = state_service.cleanup_expired_sessions()
    logger.info(f"Session cleanup task executed. Removed {removed_count} expired sessions.")

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
