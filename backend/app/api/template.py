"""Template selection endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.models.requests import TemplateSelectRequest
from app.models.responses import TemplateListResponse, SessionResponse
from app.services.template_service import TemplateService
from app.services.state_service import StateService

router = APIRouter()
state_service = StateService()
template_service = TemplateService()


@router.get("/template/options", response_model=TemplateListResponse)
async def list_templates():
    """Return available CV template options."""
    templates = template_service.get_templates()
    return TemplateListResponse(templates=templates)


@router.post("/template/select", response_model=SessionResponse)
async def select_template(
    body: TemplateSelectRequest,
):
    """Bind a template to the current session's CV draft."""
    session = state_service.get_session(body.sessionId)
    template = template_service.get_template_by_id(body.templateId)
    session.cvDraft.template.templateId = template.templateId
    session.cvDraft.template.templateName = template.templateName
    state_service.update_cv(body.sessionId, session.cvDraft)
    return SessionResponse(sessionId=session.sessionId, createdAt=session.createdAt)
