from uuid import uuid4
from app.models.requests import ExportRequest
from app.models.responses import ExportResponse, ExportStatusResponse
from app.adapters.document_adapter import get_document_adapter
from app.adapters.storage_adapter import get_storage_adapter
from app.services.state_service import get_state_service

class ExportService:
    def __init__(self) -> None:
        self._jobs: dict[str, ExportStatusResponse] = {}

    def export(self, request: ExportRequest) -> ExportResponse:
        session = get_state_service().get_session(request.session_id)
        content = get_document_adapter().generate_document(
            schema=session.cv_schema.model_dump(by_alias=True),
            template_id=session.selected_template or "professional",
            format=request.format,
        )
        file_name = f"{request.session_id}.{request.format}"
        download_url = get_storage_adapter().store_generated_file(file_name, content)
        job_id = str(uuid4())
        self._jobs[job_id] = ExportStatusResponse(job_id=job_id, status="completed", download_url=download_url)
        return ExportResponse(job_id=job_id, file_name=file_name, download_url=download_url)

    def get_status(self, job_id: str) -> ExportStatusResponse:
        return self._jobs[job_id]

_export_service = ExportService()

def get_export_service() -> ExportService:
    return _export_service
