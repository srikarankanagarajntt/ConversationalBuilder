from pydantic import BaseModel, Field
from app.models.cv_schema import CvSchema

class ConversationMessage(BaseModel):
    role: str
    content: str

class SessionContext(BaseModel):
    session_id: str
    language: str = "en"
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    cv_schema: CvSchema
    selected_template: str | None = None
