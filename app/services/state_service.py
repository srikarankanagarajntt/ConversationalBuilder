from uuid import uuid4
from datetime import datetime, timedelta
from app.models.requests import CreateSessionRequest
from app.models.responses import SessionResponse
from app.models.cv_schema import CvSchema
from app.models.session import SessionContext
import logging

logger = logging.getLogger(__name__)

class StateService:
    def __init__(self, session_ttl_minutes: int = 30) -> None:
        self._sessions: dict[str, SessionContext] = {}
        self._session_ttl_minutes = session_ttl_minutes  # Time-to-live in minutes

    def create_session(self, request: CreateSessionRequest, user: dict) -> SessionResponse:
        # Check if an active session already exists for this portal_id
        existing_session = self._find_active_session_by_portal_id(request.portal_id)

        if existing_session:
            logger.info(f"Existing session found for portal_id: {request.portal_id}, reusing: {existing_session.session_id}")
            existing_session.last_accessed = datetime.utcnow()
            return self.get_session_response(existing_session.session_id)

        # Create new session_id with format: {uuid}|{portal_id}
        uuid_part = str(uuid4())
        session_id = f"{uuid_part}|{request.portal_id}"
        cv_schema = CvSchema(sessionId=session_id)
        # For POC: Use portal_id from request to create session
        session = SessionContext(
            session_id=session_id,
            language=request.language,
            portal_id=request.portal_id,  # Store the portal ID for state tracking
            cv_schema=cv_schema
        )
        self._sessions[session_id] = session
        logger.info(f"New session created: {session_id} for portal_id: {request.portal_id}")
        return self.get_session_response(session_id)

    def get_session(self, session_id: str) -> SessionContext:
        session = self._sessions[session_id]
        # Update last_accessed timestamp
        session.last_accessed = datetime.utcnow()
        return session

    def _find_active_session_by_portal_id(self, portal_id: int) -> SessionContext | None:
        """Find an active session for the given portal_id that hasn't expired."""
        current_time = datetime.utcnow()
        ttl_delta = timedelta(minutes=self._session_ttl_minutes)

        for session in self._sessions.values():
            # Check if this session belongs to the portal_id
            if session.portal_id == portal_id:
                # Check if session is still valid (not expired)
                session_age = current_time - session.created_at
                if session_age <= ttl_delta:
                    return session

        return None

    def get_session_response(self, session_id: str) -> SessionResponse:
        session = self.get_session(session_id)
        return SessionResponse(session_id=session.session_id, language=session.language, cv_schema=session.cv_schema)

    def update_session(self, session: SessionContext) -> None:
        session.last_accessed = datetime.utcnow()
        self._sessions[session.session_id] = session

    def cleanup_expired_sessions(self) -> int:
        """Remove sessions older than TTL. Returns count of removed sessions."""
        current_time = datetime.utcnow()
        ttl_delta = timedelta(minutes=self._session_ttl_minutes)

        expired_sessions = [
            session_id for session_id, session in self._sessions.items()
            if (current_time - session.created_at) > ttl_delta
        ]

        for session_id in expired_sessions:
            del self._sessions[session_id]
            logger.info(f"Session expired and removed: {session_id}")

        total_sessions = len(self._sessions)
        logger.info(f"Cleanup completed: Removed {len(expired_sessions)} sessions. Remaining: {total_sessions}")
        return len(expired_sessions)

    def get_session_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "total_sessions": len(self._sessions),
            "ttl_minutes": self._session_ttl_minutes,
            "sessions": [
                {
                    "session_id": s.session_id,
                    "portal_id": s.portal_id,
                    "created_at": s.created_at.isoformat(),
                    "last_accessed": s.last_accessed.isoformat(),
                    "age_seconds": (datetime.utcnow() - s.created_at).total_seconds()
                }
                for s in self._sessions.values()
            ]
        }

    def flush_all_sessions(self) -> int:
        """Flush all sessions immediately. Returns count of flushed sessions."""
        count = len(self._sessions)
        self._sessions.clear()
        logger.info(f"All sessions flushed! Removed: {count} sessions")
        return count

_state_service = StateService()

def get_state_service() -> StateService:
    return _state_service
