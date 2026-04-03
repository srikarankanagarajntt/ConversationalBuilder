from app.core.constants import SUPPORTED_TEMPLATES
from app.models.requests import SelectTemplateRequest
from app.models.responses import TemplateOptionsResponse, TemplateOption, TemplateSelectionResponse
from app.services.state_service import get_state_service

class TemplateService:
    def get_template_options(self) -> TemplateOptionsResponse:
        options = [TemplateOption(template_id=t, template_name=t.title(), description=f"{t.title()} layout") for t in SUPPORTED_TEMPLATES]
        return TemplateOptionsResponse(options=options)

    def select_template(self, request: SelectTemplateRequest) -> TemplateSelectionResponse:
        session = get_state_service().get_session(request.session_id)
        session.selected_template = request.template_id
        session.cv_schema.template.template_id = request.template_id
        session.cv_schema.template.template_name = request.template_id.title()
        get_state_service().update_session(session)
        return TemplateSelectionResponse(
            session_id=request.session_id,
            template_id=request.template_id,
            template_name=request.template_id.title(),
            message="Template selected successfully.",
        )

_template_service = TemplateService()

def get_template_service() -> TemplateService:
    return _template_service
