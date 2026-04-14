import json

from app.models.cv_schema import CvSchema
from app.models.session import ConversationMessage

class PromptService:
    def build_conversation_prompt(self, schema: CvSchema, history: list[ConversationMessage], message: str) -> str:
        schema_payload = schema.model_dump(
            by_alias=True,
            include={
                "header": {"full_name", "job_title", "contact"},
                "professional_summary": True,
                "technical_skills": True,
                "current_responsibilities": True,
                "work_experience": True,
                "declaration": True,
            },
        )
        recent_history = [{"role": m.role, "content": m.content} for m in history[-4:]]

        return (
            "You are an NTT DATA CV builder assistant. "
            "Use the user's latest message and conversation history to update the CV schema. "
            "Return only structured updates for fields that changed and ask one concise next question.\n\n"
            f"Current CV schema JSON:\n{json.dumps(schema_payload, ensure_ascii=True)}\n\n"
            f"Recent conversation history JSON:\n{json.dumps(recent_history, ensure_ascii=True)}\n\n"
            f"Latest user message:\n{message}"
        )

_prompt_service = PromptService()

def get_prompt_service() -> PromptService:
    return _prompt_service
