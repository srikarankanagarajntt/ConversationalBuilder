from uuid import uuid4
from app.models.requests import CreateSessionRequest
from app.models.responses import SessionResponse
from app.models.cv_schema import CvSchema
from app.models.session import SessionContext

class StateService:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionContext] = {}

    def create_session(self, request: CreateSessionRequest, user: dict) -> SessionResponse:
        session_id = str(uuid4())
        cv_schema = CvSchema(sessionId=session_id)
        session = SessionContext(session_id=session_id, language=request.language, cv_schema=cv_schema)
        self._sessions[session_id] = session
        return self.get_session_response(session_id)

    def get_session(self, session_id: str) -> SessionContext:
        return self._sessions[session_id]

    def get_session_response(self, session_id: str) -> SessionResponse:
        session = self.get_session(session_id)
        return SessionResponse(session_id=session.session_id, language=session.language, cv_schema=session.cv_schema)

    def update_session(self, session: SessionContext) -> None:
        self._sessions[session.session_id] = session

_state_service = StateService()

def get_state_service() -> StateService:
    return _state_service
