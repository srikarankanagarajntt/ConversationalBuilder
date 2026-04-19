"""Request DTOs for all API endpoints."""
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    userId: Optional[str] = None


class ConversationMessageRequest(BaseModel):
    sessionId: str
    message: str = Field(..., min_length=1, max_length=50000)


class PersonalInfoRequest(BaseModel):
    sessionId: str
    fullName: str
    email: str
    phone: str
    location: str
    summary: str = ""
    skills: List[str] = Field(default_factory=list)


class TemplateSelectRequest(BaseModel):
    sessionId: str
    templateId: str


class PreviewEditRequest(BaseModel):
    sessionId: str
    patch: dict  # Partial CV fields to merge


class ExportRequest(BaseModel):
    sessionId: str
    format: str = Field("pdf", pattern="^(pdf|docx|pptx|json)$")
    templateId: str = Field("ntt-classic", description="Template ID for DOCX export")
    language: str = Field("en", pattern="^(en|de)$", description="Language code for CV (en=English, de=German)")
