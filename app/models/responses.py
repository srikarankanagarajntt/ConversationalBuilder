from pydantic import BaseModel, Field
from typing import Any
from app.models.cv_schema import CvSchema

class ErrorDetail(BaseModel):
    field: str | None = None
    issue: str

class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)

class ErrorResponse(BaseModel):
    error: ErrorBody

class SessionResponse(BaseModel):
    session_id: str
    language: str
    cv_schema: CvSchema

class ConversationMessageResponse(BaseModel):
    assistant_message: str
    updated_fields: dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    next_step: str = "continue_conversation"

class VoiceTranscriptionResponse(BaseModel):
    session_id: str
    transcript: str
    detected_language: str = "en"

class UploadCvResponse(BaseModel):
    session_id: str
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)

class TemplateOption(BaseModel):
    template_id: str
    template_name: str
    description: str

class TemplateOptionsResponse(BaseModel):
    options: list[TemplateOption]

class TemplateSelectionResponse(BaseModel):
    session_id: str
    template_id: str
    template_name: str
    message: str

class PreviewResponse(BaseModel):
    session_id: str
    preview_data: dict[str, Any] = Field(default_factory=dict)
    validation_errors: list[str] = Field(default_factory=list)

class ExportResponse(BaseModel):
    job_id: str
    file_name: str
    download_url: str
    status: str = "completed"

class ExportStatusResponse(BaseModel):
    job_id: str
    status: str
    download_url: str | None = None
