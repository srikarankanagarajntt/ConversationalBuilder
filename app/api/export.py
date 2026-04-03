from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.requests import ExportRequest
from app.models.responses import ExportResponse, ExportStatusResponse
from app.services.export_service import ExportService, get_export_service

router = APIRouter()

@router.post("", response_model=ExportResponse)
async def export_cv(
    request: ExportRequest,
    user=Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
) -> ExportResponse:
    return export_service.export(request)

@router.get("/{job_id}", response_model=ExportStatusResponse)
async def get_export_status(
    job_id: str,
    user=Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
) -> ExportStatusResponse:
    return export_service.get_status(job_id)
