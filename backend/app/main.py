"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import health, conversation, voice, upload, template, preview, export, llm

app = FastAPI(
    title="Conversational CV Builder API",
    version="0.1.0",
    description="AI-powered conversational CV builder — POC",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(conversation.router, prefix="/api", tags=["Conversation"])
app.include_router(voice.router, prefix="/api", tags=["Voice"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(template.router, prefix="/api", tags=["Template"])
app.include_router(preview.router, prefix="/api", tags=["Preview"])
app.include_router(export.router, prefix="/api", tags=["Export"])
app.include_router(llm.router, prefix="/api", tags=["LLM POC"])
