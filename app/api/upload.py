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
    """
    Upload a CV file (PDF or DOCX) and extract information.

    This endpoint:
    - Validates that only PDF and DOCX files are accepted
    - Extracts text and structured data from the uploaded file
    - Parses the CV into the canonical CvSchema format
    - Updates the user's session with extracted data
    - Returns the extracted data and list of missing required fields

    Args:
        session_id: The user's session ID
        file: The CV file to upload (PDF or DOCX)
        user: Current authenticated user
        parser_service: File parsing service

    Returns:
        UploadCvResponse with extracted data, session_id, and missing fields

    Raises:
        AppException (400): If file format is not PDF or DOCX
        AppException (400): If file parsing fails
    """
    return await parser_service.parse_cv_upload(session_id=session_id, upload=file)
