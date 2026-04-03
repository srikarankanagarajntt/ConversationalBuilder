"""In-memory session context model."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.cv_schema import CvSchema


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SessionContext(BaseModel):
    sessionId: str
    userId: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "active"
    cvDraft: CvSchema = Field(default_factory=CvSchema)
    conversationHistory: List[ChatMessage] = Field(default_factory=list)
    missingFields: List[str] = Field(default_factory=list)
