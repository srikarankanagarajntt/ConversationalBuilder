"""In-memory session state store.

All access to session / CV state goes through this service only, so a future
migration to Redis or DynamoDB only requires replacing this implementation.
"""
from __future__ import annotations

from typing import Dict, Optional

from app.core.exceptions import SessionNotFoundError
from app.models.cv_schema import CvSchema
from app.models.session import SessionContext, ChatMessage

# In-memory store: { session_id: SessionContext }
_store: Dict[str, SessionContext] = {}


class StateService:
    def create_session(self, session_id: str, user_id: Optional[str] = None) -> SessionContext:
        session = SessionContext(sessionId=session_id, userId=user_id)
        session.cvDraft.sessionId = session_id
        _store[session_id] = session
        return session

    def get_session(self, session_id: str) -> SessionContext:
        session = _store.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return session

    def update_cv(self, session_id: str, cv: CvSchema) -> SessionContext:
        session = self.get_session(session_id)
        session.cvDraft = cv
        return session

    def add_message(self, session_id: str, role: str, content: str) -> None:
        session = self.get_session(session_id)
        session.conversationHistory.append(ChatMessage(role=role, content=content))

    def update_missing_fields(self, session_id: str, missing: list[str]) -> None:
        session = self.get_session(session_id)
        session.missingFields = missing
