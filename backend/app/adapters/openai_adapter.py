"""OpenAI adapter isolates SDK specifics from service layer."""
from __future__ import annotations

from typing import Dict, List

from openai import AsyncOpenAI

from app.core.config import settings


class OpenAIAdapter:
    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat_completion(self, messages: List[Dict[str, str]], response_format: str = "text") -> str:
        kwargs = {
            "model": settings.openai_model,
            "messages": messages,
            "temperature": settings.openai_temperature,
            "max_tokens": settings.openai_max_tokens,
        }

        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}

        response = await self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return content or ""
