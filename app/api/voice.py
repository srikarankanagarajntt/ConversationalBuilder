from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.security import get_current_user
from app.models.responses import VoiceTranscriptionResponse, ConversationMessageResponse
from app.services.speech_service import SpeechService, get_speech_service
from app.services.conversation_service import ConversationService, get_conversation_service
from app.services.session_validator import validate_session_exists
from app.models.requests import ConversationMessageRequest

router = APIRouter()

@router.post("/transcribe", response_model=VoiceTranscriptionResponse, tags=["Voice"])
async def transcribe_audio(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    user=Depends(get_current_user),
    speech_service: SpeechService = Depends(get_speech_service),
) -> VoiceTranscriptionResponse:
    """
    Transcribe audio file to text.
    
    Requires: Valid session_id from /api/conversation/session endpoint
    
    Args:
        session_id: Your session ID (from /session endpoint)
        audio_file: Audio file to transcribe
    
    Returns:
        Transcribed text
    """
    # Validate session exists before processing
    validate_session_exists(session_id)
    return await speech_service.transcribe(session_id=session_id, audio_file=audio_file)

@router.post("/message", response_model=ConversationMessageResponse, tags=["Voice"])
async def transcribe_and_continue(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    user=Depends(get_current_user),
    speech_service: SpeechService = Depends(get_speech_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationMessageResponse:
    """
    Transcribe audio and continue conversation in one call.
    
    Requires: Valid session_id from /api/conversation/session endpoint
    
    Args:
        session_id: Your session ID (from /session endpoint)
        audio_file: Audio file to transcribe
    
    Returns:
        Assistant response based on transcribed audio
    """
    # Validate session exists before processing
    validate_session_exists(session_id)
    transcript = await speech_service.transcribe(session_id=session_id, audio_file=audio_file)
    request = ConversationMessageRequest(session_id=session_id, message=transcript.transcript)
    return await conversation_service.handle_message(request)
