from fastapi import APIRouter, Depends, Request

from app.core.security import get_current_user
from app.models.requests import CreateSessionRequest, ConversationMessageRequest
from app.models.responses import SessionResponse, ConversationMessageResponse
from app.services.state_service import StateService, get_state_service
from app.services.conversation_service import ConversationService, get_conversation_service
from app.services.session_validator import validate_session_exists

router = APIRouter()

@router.post("/session", response_model=SessionResponse, tags=["Session Management"])
async def create_or_get_session(
    raw_request: Request,
    user=Depends(get_current_user),
    state_service: StateService = Depends(get_state_service),
) -> SessionResponse:
    """
    Entry Point: Create or get existing session using client host IP from headers.

    This endpoint does not require a request body.
    """
    # Prefer host IP from headers; fall back to connection info.
    header_ip = (
        raw_request.headers.get("host_ip_address")
        or raw_request.headers.get("x-host-ip-address")
        or raw_request.headers.get("x-real-ip")
        or (raw_request.headers.get("x-forwarded-for").split(",")[0].strip() if raw_request.headers.get("x-forwarded-for") else None)
    )
    fallback_ip = raw_request.client.host if raw_request.client else None
    host_ip = header_ip or fallback_ip

    # Inject host_address into user context for StateService
    if isinstance(user, dict):
        user = {**user, "host_address": host_ip}
    else:
        try:
            setattr(user, "host_address", host_ip)
        except Exception:
            user = {"host_address": host_ip}

    # No client payload; use default session request
    req_model = CreateSessionRequest(language="en")

    return state_service.create_session(req_model, user)

@router.get("/session/{session_id}", response_model=SessionResponse, tags=["Session Management"])
async def get_session(
    session_id: str,
    user=Depends(get_current_user),
    state_service: StateService = Depends(get_state_service),
) -> SessionResponse:
    """
    Get existing session details.

    Validates that the session exists and is still active.

    Args:
        session_id: Your session ID (from /session endpoint)

    Returns:
        Session details including current cv_schema
    """
    # Validate session exists
    validate_session_exists(session_id)
    return state_service.get_session_response(session_id)

@router.post("/message", response_model=ConversationMessageResponse, tags=["Conversation"])
async def send_message(
    request: ConversationMessageRequest,
    user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationMessageResponse:
    """
    Send a message in the conversation.

    Requires: Valid session_id from /session endpoint

    Args:
        session_id: Your session ID (from /session endpoint)
        message: Your message text

    Returns:
        Assistant response and updated fields
    """
    # Validate session exists before processing message
    validate_session_exists(request.session_id)
    return await conversation_service.handle_message(request)


