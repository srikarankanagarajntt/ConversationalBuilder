"""
Session Validator Service
Handles session validation and enforcement of session-first architecture.
Keeps session management decoupled from business logic.
"""

from app.core.exceptions import AppException
from app.services.state_service import get_state_service


def validate_session_exists(session_id: str) -> None:
    """
    Validate that a session exists and is active.

    Raises AppException if:
    - Session ID is missing
    - Session doesn't exist
    - Session has expired

    Args:
        session_id: The session ID to validate

    Raises:
        AppException: If session is invalid or missing
    """
    if not session_id or not session_id.strip():
        raise AppException(
            code="SESSION_REQUIRED",
            message="Session ID is required. Please create a session first using the /session endpoint.",
            status_code=401,
            details=[
                {
                    "field": "session_id",
                    "issue": "Missing session ID. POST /api/conversation/session to create/get session."
                }
            ]
        )

    state_service = get_state_service()

    try:
        session = state_service.get_session(session_id)
    except KeyError:
        raise AppException(
            code="SESSION_NOT_FOUND",
            message="Session not found or has expired. Please create a new session using the /session endpoint.",
            status_code=404,
            details=[
                {
                    "field": "session_id",
                    "issue": f"Session '{session_id}' does not exist or has expired. Endpoint: POST /api/conversation/session"
                }
            ]
        )
    except Exception as e:
        raise AppException(
            code="SESSION_ERROR",
            message="Error validating session. Please create a new session using the /session endpoint.",
            status_code=400,
            details=[
                {
                    "field": "session_id",
                    "issue": f"Session validation failed: {str(e)}"
                }
            ]
        )


def get_validated_session(session_id: str):
    """
    Get and validate a session in one call.

    Args:
        session_id: The session ID to retrieve

    Returns:
        SessionContext: The valid session

    Raises:
        AppException: If session is invalid
    """
    validate_session_exists(session_id)
    state_service = get_state_service()
    return state_service.get_session(session_id)


def extract_host_address_from_session_id(session_id: str) -> str | None:
    """
    Extract host_address from session_id format: {uuid}|{host_address}

    Args:
        session_id: Session ID in format "uuid|host_address"

    Returns:
        Host address as string, or None if format is invalid
    """
    if not session_id or "|" not in session_id:
        return None

    try:
        parts = session_id.split("|")
        if len(parts) == 2:
            return parts[1]
    except (ValueError, IndexError):
        pass

    return None
