from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.requests import CreateSessionRequest, ConversationMessageRequest
from app.models.responses import SessionResponse, ConversationMessageResponse
from app.services.state_service import StateService, get_state_service
from app.services.conversation_service import ConversationService, get_conversation_service

router = APIRouter()

@router.post("/session", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    user=Depends(get_current_user),
    state_service: StateService = Depends(get_state_service),
) -> SessionResponse:
    return state_service.create_session(request, user)

@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user=Depends(get_current_user),
    state_service: StateService = Depends(get_state_service),
) -> SessionResponse:
    return state_service.get_session_response(session_id)

@router.post("/message", response_model=ConversationMessageResponse)
async def send_message(
    request: ConversationMessageRequest,
    user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationMessageResponse:
    return await conversation_service.handle_message(request)
