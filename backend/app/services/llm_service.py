"""LLM Service — wraps the OpenAI adapter for all AI calls."""
from __future__ import annotations

from typing import Any, Dict, List

from app.adapters.openai_adapter import OpenAIAdapter
from app.core.exceptions import LLMServiceError


class LLMService:
    def __init__(self):
        self._adapter = OpenAIAdapter()

    async def chat(
        self,
        messages: List[Dict[str, str]],
        response_format: str = "text",
    ) -> str:
        """
        Send a list of chat messages to GPT-4.1 and return the reply text.

        :param messages: List of {"role": ..., "content": ...} dicts.
        :param response_format: "text" or "json_object"
        """
        try:
            return await self._adapter.chat_completion(messages, response_format=response_format)
        except Exception as exc:
            raise LLMServiceError(f"GPT call failed: {exc}") from exc

    async def extract_cv_data(self, raw_text: str) -> Dict[str, Any]:
        """
        Use GPT-4.1 to extract structured CV fields from raw text.
        Returns a dict that maps to the CvSchema shape.
        """
        from app.services.prompt_service import PromptService

        prompt_service = PromptService()
        messages = prompt_service.build_extraction_prompt(raw_text)
        raw_json = await self.chat(messages, response_format="json_object")

        import json
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            raise LLMServiceError("LLM returned invalid JSON during CV extraction.")

    async def generate_follow_up_question(
        self, cv_json: str, missing_fields: List[str]
    ) -> str:
        """Generate the next conversational question for missing CV fields."""
        from app.services.prompt_service import PromptService

        prompt_service = PromptService()
        messages = prompt_service.build_follow_up_prompt(cv_json, missing_fields)
        return await self.chat(messages)
