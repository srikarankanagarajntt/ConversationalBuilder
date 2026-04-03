"""Response DTOs for all API endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.models.cv_schema import CvSchema


class SessionResponse(BaseModel):
    sessionId: str
    createdAt: str
    status: str = "active"


class ConversationResponse(BaseModel):
    sessionId: str
    reply: str
    cvDraft: CvSchema
    missingFields: List[str] = []
    nextQuestion: Optional[str] = None


class TranscribeResponse(BaseModel):
    transcript: str
    durationSeconds: Optional[float] = None


class UploadExtractResponse(BaseModel):
    sessionId: str
    extractedFields: Dict[str, Any]
    cvDraft: CvSchema
    missingFields: List[str] = []


class TemplateOption(BaseModel):
    templateId: str
    templateName: str
    description: str
    previewImageUrl: str = ""


class TemplateListResponse(BaseModel):
    templates: List[TemplateOption]


class PreviewResponse(BaseModel):
    sessionId: str
    cvDraft: CvSchema
    completenessScore: int  # 0-100
    missingFields: List[str] = []


class ExportJobResponse(BaseModel):
    jobId: str
    sessionId: str
    format: str
    status: str = "pending"  # pending | ready | failed
    downloadUrl: Optional[str] = None


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    traceId: str
    details: List[ErrorDetail] = []
