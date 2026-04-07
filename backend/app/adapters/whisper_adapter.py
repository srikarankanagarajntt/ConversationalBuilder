"""Whisper adapter for speech-to-text transcription."""
from __future__ import annotations

import io
import ssl

import httpx
from openai import AsyncOpenAI

from app.core.config import settings


class WhisperAdapter:
    def __init__(self):
        cert_path = r"C:\Sri\NTTdata\AI\code\backend\certs\ca-root.crt"
        ssl_context = ssl.create_default_context(cafile=cert_path)
        http_client = httpx.AsyncClient(
            verify=ssl_context,
            timeout=30.0,
        )
        self._client = AsyncOpenAI(api_key=settings.openai_api_key,
                                   http_client=http_client,)

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcript = await self._client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
        )
        return transcript.text
