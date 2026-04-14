from pydantic import BaseModel, Field
from app.models.cv_schema import CvSchema
from datetime import datetime

class ConversationMessage(BaseModel):
    role: str
    content: str

class SessionContext(BaseModel):
    session_id: str
    language: str = "en"
    host_address: str | None = None  # Tracks the user's host/IP address
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    cv_schema: CvSchema
    selected_template: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Track creation time
    last_accessed: datetime = Field(default_factory=datetime.utcnow)  # Track last access
