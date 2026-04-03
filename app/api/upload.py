from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.security import get_current_user
from app.models.responses import UploadCvResponse
from app.services.file_parser_service import FileParserService, get_file_parser_service

router = APIRouter()

@router.post("/cv", response_model=UploadCvResponse)
async def upload_cv(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    parser_service: FileParserService = Depends(get_file_parser_service),
) -> UploadCvResponse:
    return await parser_service.parse_cv_upload(session_id=session_id, upload=file)
