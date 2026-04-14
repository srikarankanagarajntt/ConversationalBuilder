"""Export service — generates PDF, DOCX, and JSON output files."""
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, Tuple

from fastapi import HTTPException, status

from app.models.cv_schema import CvSchema

# In-memory job store — keyed by job_id
_jobs: Dict[str, Dict[str, Any]] = {}

# Temporary output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "exports")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class ExportService:
    async def create_export_job(self, cv: CvSchema, fmt: str, template_id: str = "ntt-classic") -> Dict[str, Any]:
        """Generate the file synchronously (POC) and store the job record."""
        job_id = str(uuid.uuid4())
        file_id = str(uuid.uuid4())

        if fmt == "json":
            file_path = self._export_json(cv, file_id)
            media_type = "application/json"
            filename = "cv.json"
        elif fmt == "docx":
            file_path = self._export_docx(cv, file_id, template_id)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = "cv.docx"
        elif fmt == "pdf":
            file_path = self._export_pdf(cv, file_id)
            media_type = "application/pdf"
            filename = "cv.pdf"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown format: {fmt}")

        job = {
            "jobId": job_id,
            "fileId": file_id,
            "format": fmt,
            "status": "ready",
            "filePath": file_path,
            "mediaType": media_type,
            "filename": filename,
            "downloadUrl": f"/api/download/{file_id}",
        }
        _jobs[job_id] = job
        _jobs[file_id] = job  # also indexed by file_id for downloads
        return job

    def get_job(self, job_id: str) -> Dict[str, Any]:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")
        return job

    def get_file_path(self, file_id: str) -> Tuple[str, str, str]:
        job = _jobs.get(file_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return job["filePath"], job["mediaType"], job["filename"]

    # ── Format generators ─────────────────────────────────────────────────────

    def _export_json(self, cv: CvSchema, file_id: str) -> str:
        path = os.path.join(OUTPUT_DIR, f"{file_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cv.model_dump(), f, indent=2)
        return path

    def _export_docx(self, cv: CvSchema, file_id: str, template_id: str = "ntt-classic") -> str:
        from app.services.template_processor import TemplateProcessor

        processor = TemplateProcessor()
        doc = processor.process_template(cv, template_id)

        path = os.path.join(OUTPUT_DIR, f"{file_id}.docx")
        doc.save(path)
        return path

    def _export_pdf(self, cv: CvSchema, file_id: str) -> str:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        path = os.path.join(OUTPUT_DIR, f"{file_id}.pdf")
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(cv.personalInfo.fullName or "Curriculum Vitae", styles["Title"]))
        story.append(Paragraph(cv.personalInfo.email, styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(cv.personalInfo.summary, styles["Normal"]))

        if cv.experience:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Experience", styles["Heading1"]))
            for exp in cv.experience:
                story.append(Paragraph(f"<b>{exp.title}</b> — {exp.company}", styles["Heading2"]))
                for ach in exp.achievements:
                    story.append(Paragraph(f"• {ach}", styles["Normal"]))

        if cv.skills:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Skills", styles["Heading1"]))
            story.append(Paragraph(", ".join(cv.skills), styles["Normal"]))

        doc.build(story)
        return path
