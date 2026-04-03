"""Health check endpoints — no auth required."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health/live")
async def liveness():
    """Kubernetes / ALB liveness probe."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    """Readiness probe — extend to check downstream deps when needed."""
    return {"status": "ready"}
