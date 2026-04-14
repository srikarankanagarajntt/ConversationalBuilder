"""Response DTOs for all API endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.models.cv_schema import CvSchema


class BaseResponseModel(BaseModel):
    """Base model with camelCase serialization."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class SessionResponse(BaseResponseModel):
    sessionId: str
    createdAt: str
    status: str = "active"


class ConversationResponse(BaseResponseModel):
    sessionId: str
    reply: str
    cvDraft: CvSchema
    missingFields: List[str] = []
    nextQuestion: Optional[str] = None
    transcript: Optional[str] = None


class TranscribeResponse(BaseResponseModel):
    transcript: str
    durationSeconds: Optional[float] = None


class UploadExtractResponse(BaseResponseModel):
    sessionId: str
    extractedFields: Dict[str, Any]
    cvDraft: CvSchema
    missingFields: List[str] = []


class TemplateOption(BaseResponseModel):
    templateId: str
    templateName: str
    description: str
    fileType: str = ""  # docx, pptx, pdf
    fileBase64: str = ""  # Base64 encoded file content


class TemplateListResponse(BaseResponseModel):
    templates: List[TemplateOption]


class PreviewResponse(BaseResponseModel):
    sessionId: str
    cvDraft: CvSchema
    completenessScore: int  # 0-100
    missingFields: List[str] = []


class ExportJobResponse(BaseResponseModel):
    jobId: str
    sessionId: str
    format: str
    status: str = "pending"  # pending | ready | failed
    downloadUrl: Optional[str] = None


class ErrorDetail(BaseResponseModel):
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseResponseModel):
    code: str
    message: str
    traceId: str
    details: List[ErrorDetail] = []


class UploadCvResponse(BaseResponseModel):
    sessionId: str
    cvDraft: CvSchema
    missingFields: List[str] = []
