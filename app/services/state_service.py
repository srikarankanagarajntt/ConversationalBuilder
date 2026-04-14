from uuid import uuid4
from datetime import datetime, timedelta
import logging

from app.models.requests import CreateSessionRequest
from app.models.responses import SessionResponse
from app.models.cv_schema import CvSchema
from app.models.session import SessionContext

logger = logging.getLogger(__name__)


class StateService:
    def __init__(self, session_ttl_minutes: int = 30) -> None:
        self._sessions: dict[str, SessionContext] = {}
        self._session_ttl_minutes = session_ttl_minutes

    def _is_session_expired(self, session: SessionContext) -> bool:
        current_time = datetime.utcnow()
        ttl_delta = timedelta(minutes=self._session_ttl_minutes)
        return (current_time - session.created_at) > ttl_delta

    def _remove_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def create_session(self, request: CreateSessionRequest, user: dict) -> SessionResponse:
        host_address = user.get("host_address")

        if not host_address:
            raise ValueError("host_address is required to create a session.")

        existing_session = self._find_active_session_by_host_address(host_address)

        if existing_session:
            logger.info(
                f"Existing session found for host_address: {host_address}, reusing: {existing_session.session_id}"
            )
            existing_session.last_accessed = datetime.utcnow()
            self._sessions[existing_session.session_id] = existing_session
            return self.get_session_response(existing_session.session_id)

        uuid_part = str(uuid4())
        session_id = f"{uuid_part}|{host_address}"
        cv_schema = CvSchema(sessionId=session_id)

        session = SessionContext(
            session_id=session_id,
            language=request.language,
            host_address=host_address,
            cv_schema=cv_schema,
        )

        self._sessions[session_id] = session
        logger.info(f"New session created: {session_id} for host_address: {host_address}")
        return self.get_session_response(session_id)

    def get_session(self, session_id: str) -> SessionContext:
        session = self._sessions.get(session_id)

        if session is None:
            raise KeyError(f"Session not found: {session_id}")

        if self._is_session_expired(session):
            self._remove_session(session_id)
            raise KeyError(f"Session expired: {session_id}")

        session.last_accessed = datetime.utcnow()
        return session

    def _find_active_session_by_host_address(self, host_address: str) -> SessionContext | None:
        """Find an active session for the given host_address that hasn't expired."""
        current_time = datetime.utcnow()
        ttl_delta = timedelta(minutes=self._session_ttl_minutes)

        expired_session_ids: list[str] = []

        for session_id, session in self._sessions.items():
            if session.host_address != host_address:
                continue

            if (current_time - session.created_at) <= ttl_delta:
                return session

            expired_session_ids.append(session_id)

        for session_id in expired_session_ids:
            self._remove_session(session_id)
            logger.info(f"Expired session removed during lookup: {session_id}")

        return None

    def get_session_response(self, session_id: str) -> SessionResponse:
        session = self.get_session(session_id)
        return SessionResponse(
            session_id=session.session_id,
            language=session.language,
            cv_schema=session.cv_schema,
        )

    def update_session(self, session: SessionContext) -> None:
        if not session.session_id:
            raise ValueError("session.session_id is required.")

        if self._is_session_expired(session):
            self._remove_session(session.session_id)
            raise KeyError(f"Session expired: {session.session_id}")

        session.last_accessed = datetime.utcnow()
        self._sessions[session.session_id] = session

    def cleanup_expired_sessions(self) -> int:
        """Remove sessions older than TTL. Returns count of removed sessions."""
        current_time = datetime.utcnow()
        ttl_delta = timedelta(minutes=self._session_ttl_minutes)

        expired_sessions = [
            session_id
            for session_id, session in self._sessions.items()
            if (current_time - session.created_at) > ttl_delta
        ]

        for session_id in expired_sessions:
            del self._sessions[session_id]
            logger.info(f"Session expired and removed: {session_id}")

        total_sessions = len(self._sessions)
        logger.info(
            f"Cleanup completed: Removed {len(expired_sessions)} sessions. Remaining: {total_sessions}"
        )
        return len(expired_sessions)

    def get_session_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "total_sessions": len(self._sessions),
            "ttl_minutes": self._session_ttl_minutes,
            "sessions": [
                {
                    "session_id": s.session_id,
                    "host_address": s.host_address,
                    "created_at": s.created_at.isoformat(),
                    "last_accessed": s.last_accessed.isoformat(),
                    "age_seconds": (datetime.utcnow() - s.created_at).total_seconds(),
                }
                for s in self._sessions.values()
            ],
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