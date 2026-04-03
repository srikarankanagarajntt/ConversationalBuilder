from fastapi import APIRouter, Depends

from app.services.state_service import StateService, get_state_service

router = APIRouter()

@router.get("/stats", tags=["Cache Management"])
async def get_cache_stats(
    state_service: StateService = Depends(get_state_service),
) -> dict:
    """
    Get current cache statistics and active sessions.

    Returns information about:
    - Total number of sessions in cache
    - TTL configuration
    - Details of each active session

    Returns:
        Cache statistics with session details
    """
    return state_service.get_session_stats()

@router.post("/cleanup", tags=["Cache Management"])
async def manual_cleanup(
    state_service: StateService = Depends(get_state_service),
) -> dict:
    """
    Manually trigger cleanup of expired sessions.

    Normally cleanup runs automatically every 30 minutes.
    Use this endpoint to trigger cleanup immediately (e.g., for testing).

    Returns:
        Number of removed sessions and remaining sessions
    """
    removed_count = state_service.cleanup_expired_sessions()
    return {
        "message": "Manual cleanup completed",
        "removed_sessions": removed_count,
        "remaining_sessions": state_service.get_session_stats()["total_sessions"]
    }

@router.post("/flush", tags=["Cache Management"])
async def flush_cache(
    state_service: StateService = Depends(get_state_service),
) -> dict:
    """
    Flush all sessions immediately (for testing/debugging).

    WARNING: This will delete all active sessions.
    Use with caution - only for testing/debugging purposes.

    Returns:
        Number of flushed sessions
    """
    removed_count = state_service.flush_all_sessions()
    return {
        "message": "All sessions flushed",
        "flushed_sessions": removed_count
    }

