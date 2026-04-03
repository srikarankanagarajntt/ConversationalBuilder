from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.security import get_current_user
from app.models.responses import VoiceTranscriptionResponse, ConversationMessageResponse
from app.services.speech_service import SpeechService, get_speech_service
from app.services.conversation_service import ConversationService, get_conversation_service
from app.models.requests import ConversationMessageRequest

router = APIRouter()

@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    user=Depends(get_current_user),
    speech_service: SpeechService = Depends(get_speech_service),
) -> VoiceTranscriptionResponse:
    return await speech_service.transcribe(session_id=session_id, audio_file=audio_file)

@router.post("/message", response_model=ConversationMessageResponse)
async def transcribe_and_continue(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    user=Depends(get_current_user),
    speech_service: SpeechService = Depends(get_speech_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationMessageResponse:
    transcript = await speech_service.transcribe(session_id=session_id, audio_file=audio_file)
    request = ConversationMessageRequest(session_id=session_id, message=transcript.transcript)
    return await conversation_service.handle_message(request)
