from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.requests import UpdatePreviewRequest
from app.models.responses import PreviewResponse
from app.services.preview_service import PreviewService, get_preview_service

router = APIRouter()

@router.get("/{session_id}", response_model=PreviewResponse)
async def get_preview(
    session_id: str,
    user=Depends(get_current_user),
    preview_service: PreviewService = Depends(get_preview_service),
) -> PreviewResponse:
    return preview_service.get_preview(session_id)

@router.put("/{session_id}", response_model=PreviewResponse)
async def update_preview(
    session_id: str,
    request: UpdatePreviewRequest,
    user=Depends(get_current_user),
    preview_service: PreviewService = Depends(get_preview_service),
) -> PreviewResponse:
    return preview_service.update_preview(session_id, request)
