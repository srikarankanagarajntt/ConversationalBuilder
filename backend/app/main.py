"""FastAPI application entry point."""
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import configure_logging
from app.api import health, conversation, voice, upload, template, preview, export, llm

configure_logging()
logger = logging.getLogger(__name__)

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


def _exc_info(exc: BaseException) -> tuple[type[BaseException], BaseException, object]:
    return (type(exc), exc, exc.__traceback__)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.error(
        "HTTPException | method=%s | path=%s | status=%s | detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
        exc_info=_exc_info(exc),
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.error(
        "RequestValidationError | method=%s | path=%s | errors=%s",
        request.method,
        request.url.path,
        exc.errors(),
        exc_info=_exc_info(exc),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception | method=%s | path=%s",
        request.method,
        request.url.path,
        exc_info=_exc_info(exc),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
