from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.requests import SelectTemplateRequest
from app.models.responses import TemplateOptionsResponse, TemplateSelectionResponse
from app.models.export_manifest import ExportManifest
from app.services.template_service import TemplateService, get_template_service

router = APIRouter()

@router.get("/options", response_model=TemplateOptionsResponse)
async def get_template_options(
    user=Depends(get_current_user),
    template_service: TemplateService = Depends(get_template_service),
) -> TemplateOptionsResponse:
    return template_service.get_template_options()

@router.post("/select", response_model=TemplateSelectionResponse)
async def select_template(
    request: SelectTemplateRequest,
    user=Depends(get_current_user),
    template_service: TemplateService = Depends(get_template_service),
) -> TemplateSelectionResponse:
    return template_service.select_template(request)

@router.get("/manifest/{session_id}", response_model=ExportManifest)
async def get_template_manifest(
    session_id: str,
    include_content: bool = False,
    user=Depends(get_current_user),
    template_service: TemplateService = Depends(get_template_service),
) -> ExportManifest:
    """
    Retrieve the export manifest for the session's selected template, including
    the master DOCX/PPTX file names and available outputs. Optionally include
    base64-encoded master files via include_content=true.
    """
    return template_service.get_export_manifest(session_id, include_content)
