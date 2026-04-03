"""Upload endpoint — CV file ingestion and structured extraction."""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.models.responses import UploadExtractResponse
from app.services.file_parser_service import FileParserService
from app.services.llm_service import LLMService
from app.services.cv_schema_service import CvSchemaService
from app.services.state_service import StateService
from app.services.validation_service import ValidationService

router = APIRouter()
state_service = StateService()
llm_service = LLMService()
cv_schema_service = CvSchemaService()
validation_service = ValidationService()
file_parser_service = FileParserService()


@router.post("/upload/cv", response_model=UploadExtractResponse)
async def upload_cv(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload an existing CV file (PDF/DOCX/PPTX) and extract structured fields."""
    raw_bytes = await file.read()
    raw_text = await file_parser_service.extract_text(raw_bytes, content_type=file.content_type or "")
    extracted = await llm_service.extract_cv_data(raw_text)
    session = state_service.get_session(session_id)
    updated_cv = cv_schema_service.merge_partial_update(session.cvDraft, extracted)
    missing = validation_service.get_missing_fields(updated_cv)
    state_service.update_cv(session_id, updated_cv)
    return UploadExtractResponse(
        sessionId=session_id,
        extractedFields=extracted,
        cvDraft=updated_cv,
        missingFields=missing,
    )
