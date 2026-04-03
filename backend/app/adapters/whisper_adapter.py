"""Whisper adapter for speech-to-text transcription."""
from __future__ import annotations

import io

from openai import AsyncOpenAI

from app.core.config import settings


class WhisperAdapter:
    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcript = await self._client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
        )
        return transcript.text
