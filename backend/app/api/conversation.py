"""Conversation endpoints — text-based CV building."""
from __future__ import annotations

from fastapi import APIRouter
import uuid

from app.models.requests import CreateSessionRequest, ConversationMessageRequest, PersonalInfoRequest
from app.models.responses import SessionResponse, ConversationResponse
from app.services.conversation_service import ConversationService
from app.services.state_service import StateService

router = APIRouter()
state_service = StateService()
conversation_service = ConversationService(state_service)


@router.post("/session", response_model=SessionResponse)
async def create_session(
    body: CreateSessionRequest,
):
    """Create a new CV-building session."""
    session_id = str(uuid.uuid4())
    session = state_service.create_session(session_id, user_id=body.userId)
    return SessionResponse(
        sessionId=session.sessionId,
        createdAt=session.createdAt,
        status=session.status,
    )


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
):
    """Return current session metadata."""
    session = state_service.get_session(session_id)
    return SessionResponse(
        sessionId=session.sessionId,
        createdAt=session.createdAt,
        status=session.status,
    )


@router.post("/conversation/message", response_model=ConversationResponse)
async def send_message(
    body: ConversationMessageRequest,
):
    """Process a user chat message and advance the CV conversation."""
    return await conversation_service.handle_message(body.sessionId, body.message)


@router.post("/conversation/personal-info", response_model=ConversationResponse)
async def submit_personal_info(
    body: PersonalInfoRequest,
):
    """Handle personal info modal submission."""
    return await conversation_service.handle_personal_info_submission(
        body.sessionId,
        body.fullName,
        body.email,
        body.phone,
        body.location,
        body.linkedin,
        body.summary,
        body.skills,
    )
