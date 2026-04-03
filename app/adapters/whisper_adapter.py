from fastapi import UploadFile

class WhisperAdapter:
    async def transcribe(self, audio_file: UploadFile) -> str:
        return f"Mock transcript generated from {audio_file.filename}"

_whisper_adapter = WhisperAdapter()

def get_whisper_adapter() -> WhisperAdapter:
    return _whisper_adapter
