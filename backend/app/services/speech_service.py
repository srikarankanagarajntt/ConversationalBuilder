"""Speech service — transcribes audio via Whisper adapter."""
from __future__ import annotations

from app.adapters.whisper_adapter import WhisperAdapter


class SpeechService:
    def __init__(self):
        self._adapter = WhisperAdapter()

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """Return text transcript from raw audio bytes."""
        return await self._adapter.transcribe(audio_bytes, filename=filename)

    async def synthesize(self, text: str, voice: str | None = None, audio_format: str | None = None) -> bytes:
        """Return synthesized speech bytes for the provided text."""
        return await self._adapter.synthesize(text=text, voice=voice, audio_format=audio_format)
