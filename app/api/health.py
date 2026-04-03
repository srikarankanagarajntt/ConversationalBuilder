from fastapi import APIRouter

router = APIRouter()

@router.get("/health/live")
async def health_live() -> dict:
    return {"status": "UP", "check": "live"}

@router.get("/health/ready")
async def health_ready() -> dict:
    return {"status": "UP", "check": "ready"}
