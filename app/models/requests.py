from pydantic import BaseModel, Field
from typing import Any

class CreateSessionRequest(BaseModel):
    language: str = "en"

class ConversationMessageRequest(BaseModel):
    session_id: str
    message: str

class SelectTemplateRequest(BaseModel):
    session_id: str
    template_id: str

class UpdatePreviewRequest(BaseModel):
    edits: dict[str, Any] = Field(default_factory=dict)

class ExportRequest(BaseModel):
    session_id: str
    format: str = "pdf"
