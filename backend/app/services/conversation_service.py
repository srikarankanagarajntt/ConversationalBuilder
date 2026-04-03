"""Conversation orchestration service."""
from __future__ import annotations

import json
from typing import Any, Dict

from app.models.responses import ConversationResponse
from app.services.state_service import StateService
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.services.cv_schema_service import CvSchemaService
from app.services.validation_service import ValidationService


class ConversationService:
    def __init__(self, state_service: StateService):
        self._state = state_service
        self._llm = LLMService()
        self._prompts = PromptService()
        self._cv_schema = CvSchemaService()
        self._validation = ValidationService()

    async def handle_message(self, session_id: str, user_message: str) -> ConversationResponse:
        """
        Core conversation loop:
        1. Load session state
        2. Build prompt with current CV draft + history
        3. Call GPT-4.1
        4. Parse AI response → extract CV updates
        5. Merge into draft, validate, persist
        6. Return reply + updated draft
        """
        session = self._state.get_session(session_id)

        # Persist user message
        self._state.add_message(session_id, "user", user_message)

        # Build history for the LLM (max last 20 turns to keep tokens manageable)
        history = [
            {"role": m.role, "content": m.content}
            for m in session.conversationHistory[-20:]
        ]

        cv_json = session.cvDraft.model_dump_json(indent=2)
        messages = self._prompts.build_conversation_prompt(history, cv_json, user_message)

        raw_response = await self._llm.chat(messages, response_format="json_object")

        # Parse structured response from GPT
        parsed: Dict[str, Any] = {}
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            # Graceful fallback — treat entire response as plain reply
            parsed = {"reply": raw_response, "cvUpdate": {}, "nextQuestion": None}

        reply_text = parsed.get("reply", "I could not understand that. Please try again.")
        cv_update = parsed.get("cvUpdate", {})
        next_question = parsed.get("nextQuestion")

        # Merge AI-extracted fields into the draft
        if cv_update:
            updated_cv = self._cv_schema.merge_partial_update(session.cvDraft, cv_update)
            self._state.update_cv(session_id, updated_cv)
        else:
            updated_cv = session.cvDraft

        # Validate and compute missing fields
        missing = self._validation.get_missing_fields(updated_cv)
        self._state.update_missing_fields(session_id, missing)

        # Persist assistant reply
        self._state.add_message(session_id, "assistant", reply_text)

        return ConversationResponse(
            sessionId=session_id,
            reply=reply_text,
            cvDraft=updated_cv,
            missingFields=missing,
            nextQuestion=next_question,
        )
