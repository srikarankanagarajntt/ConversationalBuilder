from pydantic import BaseModel, Field
from app.models.cv_schema import CvSchema
from datetime import datetime

class ConversationMessage(BaseModel):
    role: str
    content: str

class SessionContext(BaseModel):
    session_id: str
    language: str = "en"
    portal_id: int | None = None  # For POC: tracks the user's portal ID
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    cv_schema: CvSchema
    selected_template: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Track creation time
    last_accessed: datetime = Field(default_factory=datetime.utcnow)  # Track last access
