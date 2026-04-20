"""Voice endpoints — audio transcription and voice-driven conversation."""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.models.responses import ConversationResponse, TranscribeResponse
from app.services.speech_service import SpeechService
from app.services.conversation_service import ConversationService
from app.services.state_service import StateService
from app.services.translation_service import TranslationService

router = APIRouter()
state_service = StateService()
speech_service = SpeechService()
conversation_service = ConversationService(state_service)
translation_service = TranslationService()


@router.post("/voice/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
):
    """Transcribe uploaded audio to text using Whisper, then translate to English if needed."""
    audio_bytes = await file.read()
    transcript = await speech_service.transcribe(audio_bytes, filename=file.filename or "audio.wav")
    
    # Translate to English if the transcript is in a different language
    english_transcript = await translation_service.translate_transcript_to_english_async(transcript)
    
    return TranscribeResponse(transcript=english_transcript)


@router.post("/voice/message", response_model=ConversationResponse)
async def voice_message(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Transcribe audio (and translate to English if needed), then feed into conversation flow."""
    audio_bytes = await file.read()
    
    # Transcribe audio to text
    transcript = await speech_service.transcribe(audio_bytes, filename=file.filename or "audio.wav")
    
    # Translate transcript to English if it's in a different language
    english_transcript = await translation_service.translate_transcript_to_english_async(transcript)
    
    # Feed the English transcript into the conversation
    response = await conversation_service.handle_message(session_id, english_transcript)
    
    # Always return English transcript in the response
    response.transcript = english_transcript
    return response
