"""Request DTOs for all API endpoints."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    userId: Optional[str] = None


class ConversationMessageRequest(BaseModel):
    sessionId: str
    message: str = Field(..., min_length=1, max_length=4000)


class TemplateSelectRequest(BaseModel):
    sessionId: str
    templateId: str


class PreviewEditRequest(BaseModel):
    sessionId: str
    patch: dict  # Partial CV fields to merge


class ExportRequest(BaseModel):
    sessionId: str
    format: str = Field("pdf", pattern="^(pdf|docx|json)$")
