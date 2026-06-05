import time
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.state_service import StateService

router = APIRouter()
state_service = StateService()

# Use proper cross-platform path handling
IMAGE_UPLOAD_DIR = Path(os.path.expanduser("~/temp/images"))
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}

# Create directory if it doesn't exist
IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/profile-picture/upload")
async def upload_profile_picture(
        sessionId: str = Form(...),
        file: UploadFile = File(...)
):
    """Upload profile picture (max 10 MB) and save to CV"""
    try:
        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds 10 MB limit. Got {len(content) / 1024 / 1024:.2f} MB"
            )

        # Validate file extension
        fileExt = os.path.splitext(file.filename)[1].lower()
        if fileExt not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {fileExt}. Allowed: {ALLOWED_EXTENSIONS}"
            )

        # Generate filename
        fileName = f"{sessionId}_{int(time.time())}{fileExt}"
        filePath = IMAGE_UPLOAD_DIR / fileName

        # Save file
        with open(filePath, "wb") as f:
            f.write(content)

        # Verify file was saved
        if not filePath.exists():
            raise HTTPException(
                status_code=500,
                detail="File was not saved successfully"
            )

        # Return normalized file path (forward slashes for consistency)
        normalizedPath = str(filePath).replace("\\", "/")

        # Update CV with profile picture URL
        session = state_service.get_session(sessionId)
        session.cvDraft.personalInfo.profilePictureUrl = normalizedPath
        state_service.update_cv(sessionId, session.cvDraft)

        return {
            "sessionId": sessionId,
            "profilePictureUrl": normalizedPath,
            "fileName": fileName,
            "fileSize": len(content),
            "savedAt": str(filePath),
            "cvDraft": session.cvDraft
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
