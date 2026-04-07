import base64
from pathlib import Path

from app.core.constants import SUPPORTED_TEMPLATES
from app.models.requests import SelectTemplateRequest
from app.models.responses import TemplateOptionsResponse, TemplateOption, TemplateSelectionResponse
from app.services.state_service import get_state_service


class TemplateService:
    TEMPLATE_FILE_MAP = {
        "simple": "NTT template - Resume.docx",
    }

    @staticmethod
    def _get_template_base64(file_name: str) -> str | None:
        file_path = Path(__file__).resolve().parents[2] / "template" / file_name
        if not file_path.exists():
            return None
        content = file_path.read_bytes()
        return base64.b64encode(content).decode("ascii")

    def get_template_options(self) -> TemplateOptionsResponse:
        options: list[TemplateOption] = []
        for template_id in SUPPORTED_TEMPLATES:
            file_name = self.TEMPLATE_FILE_MAP.get(template_id)
            template_base64 = self._get_template_base64(file_name) if file_name else None
            options.append(
                TemplateOption(
                    template_id=template_id,
                    template_name=template_id.title(),
                    description=f"{template_id.title()} layout",
                    template_file_name=file_name,
                    template_base64=template_base64,
                )
            )
        return TemplateOptionsResponse(options=options)

    def select_template(self, request: SelectTemplateRequest) -> TemplateSelectionResponse:
        session = get_state_service().get_session(request.session_id)
        session.selected_template = request.template_id
        session.cv_schema.meta.template_version = request.template_id
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
