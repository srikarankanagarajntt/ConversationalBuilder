from fastapi import UploadFile
from app.adapters.whisper_adapter import get_whisper_adapter
from app.models.responses import VoiceTranscriptionResponse

class SpeechService:
    async def transcribe(self, session_id: str, audio_file: UploadFile) -> VoiceTranscriptionResponse:
        transcript = await get_whisper_adapter().transcribe(audio_file)
        return VoiceTranscriptionResponse(
            session_id=session_id,
            transcript=transcript,
            detected_language="en",
        )

_speech_service = SpeechService()

def get_speech_service() -> SpeechService:
    return _speech_service
