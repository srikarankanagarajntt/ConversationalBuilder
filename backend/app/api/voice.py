"""Voice endpoints — audio transcription and voice-driven conversation."""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.models.responses import ConversationResponse, TranscribeResponse
from app.services.speech_service import SpeechService
from app.services.conversation_service import ConversationService
from app.services.state_service import StateService

router = APIRouter()
state_service = StateService()
speech_service = SpeechService()
conversation_service = ConversationService(state_service)


@router.post("/voice/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
):
    """Transcribe uploaded audio to text using Whisper."""
    audio_bytes = await file.read()
    transcript = await speech_service.transcribe(audio_bytes, filename=file.filename or "audio.wav")
    return TranscribeResponse(transcript=transcript)


@router.post("/voice/message", response_model=ConversationResponse)
async def voice_message(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Transcribe audio then feed transcript into the conversation flow."""
    audio_bytes = await file.read()
    transcript = await speech_service.transcribe(audio_bytes, filename=file.filename or "audio.wav")
    response = await conversation_service.handle_message(session_id, transcript)
    response.transcript = transcript
    return response
