"""No-op auth stub — authentication disabled for local POC."""
from __future__ import annotations


async def require_auth() -> dict:
    """Returns a fixed stub principal.  No token required."""
    return {"sub": "dev-user", "email": "dev@example.com"}
