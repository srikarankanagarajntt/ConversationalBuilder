from app.models.requests import ConversationMessageRequest
from app.models.responses import ConversationMessageResponse
from app.models.session import ConversationMessage
from app.services.state_service import get_state_service
from app.services.prompt_service import get_prompt_service
from app.services.llm_service import get_llm_service
from app.services.cv_schema_service import get_cv_schema_service
from app.services.validation_service import get_validation_service

class ConversationService:
    async def handle_message(self, request: ConversationMessageRequest) -> ConversationMessageResponse:
        state_service = get_state_service()
        prompt_service = get_prompt_service()
        llm_service = get_llm_service()
        cv_schema_service = get_cv_schema_service()
        validation_service = get_validation_service()

        session = state_service.get_session(request.session_id)
        session.conversation_history.append(ConversationMessage(role="user", content=request.message))

        prompt = prompt_service.build_conversation_prompt(
            schema=session.cv_schema,
            history=session.conversation_history,
            message=request.message,
        )
        llm_output = await llm_service.continue_conversation(prompt)

        updates = llm_output.get("updates", {})
        assistant_message = llm_output.get("assistant_message", "Please continue.")
        session.cv_schema = cv_schema_service.merge_partial_update(session.cv_schema, updates)
        missing_fields = validation_service.find_missing_fields(session.cv_schema)

        session.conversation_history.append(ConversationMessage(role="assistant", content=assistant_message))
        state_service.update_session(session)

        return ConversationMessageResponse(
            assistant_message=assistant_message,
            updated_fields=updates,
            missing_fields=missing_fields,
            next_step="continue_conversation",
        )

_conversation_service = ConversationService()

def get_conversation_service() -> ConversationService:
    return _conversation_service
