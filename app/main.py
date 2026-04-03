from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, conversation, voice, upload, template, preview, export
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Conversational CV Builder backend skeleton using NTT template aligned canonical CV schema.",
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
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(template.router, prefix="/api/template", tags=["template"])
app.include_router(preview.router, prefix="/api/preview", tags=["preview"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"message": "Conversational CV Builder API is running."}
