from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.requests import CreateSessionRequest, ConversationMessageRequest
from app.models.responses import SessionResponse, ConversationMessageResponse
from app.services.state_service import StateService, get_state_service
from app.services.conversation_service import ConversationService, get_conversation_service
from app.services.session_validator import validate_session_exists

router = APIRouter()

@router.post("/session", response_model=SessionResponse, tags=["Session Management"])
async def create_or_get_session(
    request: CreateSessionRequest,
    user=Depends(get_current_user),
    state_service: StateService = Depends(get_state_service),
) -> SessionResponse:
    """
    Entry Point: Create or get existing session using portal_id.

    This is the gateway endpoint - users must call this first to get a session_id.
    All other API operations require a valid session_id.

    If a session already exists for this portal_id (within 30 minutes), it will be reused.
    Otherwise, a new session is created.

    Args:
        portal_id: Your portal/user ID (required)
        language: Preferred language (default: "en")

    Returns:
        session_id: Use this for all subsequent API calls
        cv_schema: Your CV data structure
    """
    return state_service.create_session(request, user)

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


