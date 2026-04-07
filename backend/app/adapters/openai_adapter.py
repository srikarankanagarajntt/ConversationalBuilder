"""OpenAI adapter isolates SDK specifics from service layer."""
from __future__ import annotations

import ssl
from typing import Dict, List

import httpx
from openai import AsyncOpenAI

from app.core.config import settings


class OpenAIAdapter:
    def __init__(self):
        cert_path = r"C:\Sri\NTTdata\AI\code\backend\certs\ca-root.crt"
        ssl_context = ssl.create_default_context(cafile=cert_path)
        http_client = httpx.AsyncClient(
            verify=ssl_context,
            timeout=30.0,
        )
        self._client = AsyncOpenAI(api_key=settings.openai_api_key,
                                   http_client=http_client,)

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
