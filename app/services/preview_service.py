from app.models.requests import UpdatePreviewRequest
from app.models.responses import PreviewResponse
from app.services.state_service import get_state_service
from app.services.validation_service import get_validation_service

class PreviewService:
    def get_preview(self, session_id: str) -> PreviewResponse:
        session = get_state_service().get_session(session_id)
        validation_errors = get_validation_service().find_missing_fields(session.cv_schema)
        return PreviewResponse(
            session_id=session_id,
            preview_data=session.cv_schema.model_dump(by_alias=True),
            validation_errors=validation_errors,
        )

    def update_preview(self, session_id: str, request: UpdatePreviewRequest) -> PreviewResponse:
        session = get_state_service().get_session(session_id)
        header = request.edits.get("header", {})
        if isinstance(header, dict) and "fullName" in header:
            session.cv_schema.header.full_name = str(header["fullName"])
        get_state_service().update_session(session)
        return self.get_preview(session_id)

_preview_service = PreviewService()

def get_preview_service() -> PreviewService:
    return _preview_service
