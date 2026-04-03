from app.models.cv_schema import CvSchema
from app.models.session import ConversationMessage

class PromptService:
    def build_conversation_prompt(self, schema: CvSchema, history: list[ConversationMessage], message: str) -> str:
        return (
            "You are an NTT DATA CV builder assistant. Use the NTT resume structure. "
            "Update the canonical CV schema from the user input and ask the next best follow-up question.\n"
            f"User message: {message}"
        )

_prompt_service = PromptService()

def get_prompt_service() -> PromptService:
    return _prompt_service
