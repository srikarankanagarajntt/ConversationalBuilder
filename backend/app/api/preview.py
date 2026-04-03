"""Preview endpoints — human review and edit flow."""
from __future__ import annotations

from fastapi import APIRouter

from app.models.requests import PreviewEditRequest
from app.models.responses import PreviewResponse
from app.services.preview_service import PreviewService
from app.services.state_service import StateService
from app.services.cv_schema_service import CvSchemaService
from app.services.validation_service import ValidationService

router = APIRouter()
state_service = StateService()
cv_schema_service = CvSchemaService()
validation_service = ValidationService()
preview_service = PreviewService()


@router.get("/preview/{session_id}", response_model=PreviewResponse)
async def get_preview(
    session_id: str,
):
    """Return the current CV draft ready for preview rendering."""
    session = state_service.get_session(session_id)
    missing = validation_service.get_missing_fields(session.cvDraft)
    score = validation_service.completeness_score(session.cvDraft)
    return PreviewResponse(
        sessionId=session_id,
        cvDraft=session.cvDraft,
        completenessScore=score,
        missingFields=missing,
    )


@router.put("/preview/{session_id}", response_model=PreviewResponse)
async def update_preview(
    session_id: str,
    body: PreviewEditRequest,
):
    """Apply human edits (partial patch) to the CV draft."""
    session = state_service.get_session(session_id)
    updated_cv = cv_schema_service.merge_partial_update(session.cvDraft, body.patch)
    validation_service.validate(updated_cv)
    state_service.update_cv(session_id, updated_cv)
    missing = validation_service.get_missing_fields(updated_cv)
    score = validation_service.completeness_score(updated_cv)
    return PreviewResponse(
        sessionId=session_id,
        cvDraft=updated_cv,
        completenessScore=score,
        missingFields=missing,
    )
