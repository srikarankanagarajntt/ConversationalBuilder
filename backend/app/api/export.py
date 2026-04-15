"""Export endpoints — generate PDF, DOCX, or JSON CV output."""
from __future__ import annotations

import uuid
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.models.requests import ExportRequest
from app.models.responses import ExportJobResponse
from app.services.export_service import ExportService
from app.services.state_service import StateService

router = APIRouter()
state_service = StateService()
export_service = ExportService()


@router.post("/export", response_model=ExportJobResponse)
async def request_export(
    body: ExportRequest,
):
    """Kick off a CV export job.  Returns a job ID to poll for completion."""
    session = state_service.get_session(body.sessionId)
    job = await export_service.create_export_job(session.cvDraft, body.format, body.templateId)
    return ExportJobResponse(
        jobId=job["jobId"],
        sessionId=body.sessionId,
        format=body.format,
        status=job["status"],
        downloadUrl=job.get("downloadUrl"),
    )


@router.get("/export/{job_id}", response_model=ExportJobResponse)
async def get_export_status(
    job_id: str,
):
    """Poll the export job status."""
    job = export_service.get_job(job_id)
    return ExportJobResponse(**job)


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
):
    """Stream the generated export file to the client."""
    file_path, media_type, filename = export_service.get_file_path(file_id)
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
