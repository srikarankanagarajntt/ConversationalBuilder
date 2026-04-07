"""Whisper adapter for speech-to-text transcription."""
from __future__ import annotations

import inspect
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

    async def synthesize(self, text: str, voice: str | None = None, audio_format: str | None = None) -> bytes:
        speech_response = await self._client.audio.speech.create(
            model=settings.tts_model,
            voice=voice or settings.tts_voice,
            input=text,
            response_format=audio_format or settings.tts_format,
        )

        if hasattr(speech_response, "content") and isinstance(speech_response.content, (bytes, bytearray)):
            return bytes(speech_response.content)

        if hasattr(speech_response, "read"):
            data = speech_response.read()
            if inspect.isawaitable(data):
                data = await data
            if isinstance(data, (bytes, bytearray)):
                return bytes(data)

        if isinstance(speech_response, (bytes, bytearray)):
            return bytes(speech_response)

        return bytes(str(speech_response), "utf-8")
