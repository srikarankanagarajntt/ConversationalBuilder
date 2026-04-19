"""Export service — generates PDF, DOCX, and JSON output files."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import uuid
from typing import Any, Dict, Tuple

from fastapi import HTTPException, status

from app.models.cv_schema import CvSchema
from app.services.translation_service import TranslationService

# In-memory job store — keyed by job_id
_jobs: Dict[str, Dict[str, Any]] = {}

# Temporary output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "exports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Master template path
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "template")
MASTER_TEMPLATE = os.path.join(TEMPLATE_DIR, "NTT_DATA_Master_Templates.docx")


class ExportService:
    def __init__(self):
        self.translation_service = TranslationService()
    
    async def create_export_job(self, cv: CvSchema, fmt: str, template_id: str = "ntt-classic", language: str = "en") -> Dict[str, Any]:
        """Generate the file synchronously (POC) and store the job record."""
        job_id = str(uuid.uuid4())
        file_id = str(uuid.uuid4())
        
        # Translate CV if needed
        if language and language != "en":
            try:
                cv = self.translation_service.translate_cv(cv, language)
            except Exception as e:
                # Log but continue with original CV if translation fails
                print(f"Translation failed: {e}")

        try:
            if fmt == "json":
                file_path = self._export_json(cv, file_id)
                media_type = "application/json"
                filename = f"{cv.personalInfo.fullName}_cv.json"
            elif fmt == "docx":
                file_path = self._export_docx(cv, file_id, template_id)
                media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                filename = f"{cv.personalInfo.fullName}_cv.docx"
            elif fmt == "pdf":
                file_path = self._export_pdf(cv, file_id, template_id)
                media_type = "application/pdf"
                filename = f"{cv.personalInfo.fullName}_cv.pdf"
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Export failed: {str(e)}"
            )

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
        """Export CV as JSON."""
        path = os.path.join(OUTPUT_DIR, f"{file_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cv.model_dump(), f, indent=2)
        return path

    def _export_docx(self, cv: CvSchema, file_id: str, template_id: str = "ntt-classic") -> str:
        """Export CV as DOCX using template rendering."""
        try:
            # Render from template
            rendered_docx_path = self._render_docx_from_template(cv, template_id)

            # Verify the rendered file exists and has content
            if not os.path.exists(rendered_docx_path):
                raise FileNotFoundError(f"Rendered DOCX file not created: {rendered_docx_path}")

            file_size = os.path.getsize(rendered_docx_path)
            if file_size == 0:
                raise ValueError("Rendered DOCX file is empty")

            # Copy to output directory
            output_path = os.path.join(OUTPUT_DIR, f"{file_id}.docx")
            with open(rendered_docx_path, "rb") as src:
                content = src.read()
                if not content:
                    raise ValueError("Failed to read rendered DOCX file")
                with open(output_path, "wb") as dst:
                    dst.write(content)

            # Verify the output file
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Output DOCX file not created: {output_path}")

            output_size = os.path.getsize(output_path)
            if output_size == 0:
                raise ValueError("Output DOCX file is empty")

            # Cleanup temporary file
            if os.path.exists(rendered_docx_path):
                try:
                    os.remove(rendered_docx_path)
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up temporary file {rendered_docx_path}: {cleanup_error}")

            return output_path
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"DOCX rendering failed: {str(e)}"
            )

    def _export_pdf(self, cv: CvSchema, file_id: str, template_id: str = "ntt-classic") -> str:
        """Export CV as PDF (via DOCX rendering + conversion)."""
        try:
            # First render DOCX
            docx_path = self._render_docx_from_template(cv, template_id)

            # Then convert to PDF
            pdf_path = os.path.join(OUTPUT_DIR, f"{file_id}.pdf")
            self._convert_docx_to_pdf(docx_path, pdf_path)

            # Cleanup temporary DOCX
            if os.path.exists(docx_path):
                os.remove(docx_path)

            return pdf_path
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDF conversion failed: {str(e)}"
            )

    def _render_docx_from_template(self, cv: CvSchema, template_id: str) -> str:
        """Render DOCX from master template with Jinja2 placeholders."""
        try:
            from docxtpl import DocxTemplate
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="docxtpl library not installed. Run: pip install docxtpl"
            )

        # Check if master template exists
        if not os.path.exists(MASTER_TEMPLATE):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Master template not found: {MASTER_TEMPLATE}"
            )

        try:
            # Load template
            doc = DocxTemplate(MASTER_TEMPLATE)

            # Prepare context for Jinja2 rendering
            context = self._prepare_template_context(cv)
            
            # Ensure all strings in context are properly encoded for DOCX
            context = self._sanitize_context_for_docx(context)

            # Render template
            doc.render(context)

            # Save to temporary file
            temp_file = os.path.join(tempfile.gettempdir(), f"rendered_{uuid.uuid4()}.docx")
            doc.save(temp_file)

            return temp_file
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"DOCX rendering failed: {str(e)}"
            )

    def _sanitize_context_for_docx(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize context values to ensure proper DOCX encoding."""
        sanitized = {}
        for key, value in context.items():
            if isinstance(value, str):
                # Ensure UTF-8 encoding and remove any null characters
                try:
                    # Clean up any problematic characters
                    cleaned = value.replace('\x00', '').replace('\r\n', '\n')
                    # Ensure it can be encoded to UTF-8
                    cleaned.encode('utf-8')
                    sanitized[key] = cleaned
                except (UnicodeEncodeError, AttributeError):
                    # Fallback to removing problematic chars
                    sanitized[key] = value.encode('utf-8', errors='ignore').decode('utf-8')
            elif isinstance(value, list):
                # Recursively sanitize list items
                sanitized[key] = [
                    self._sanitize_context_for_docx(item) if isinstance(item, dict)
                    else (item.encode('utf-8', errors='ignore').decode('utf-8') if isinstance(item, str) else item)
                    for item in value
                ]
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = self._sanitize_context_for_docx(value)
            else:
                sanitized[key] = value
        return sanitized

    def _prepare_template_context(self, cv: CvSchema) -> Dict[str, Any]:
        """Prepare CV data for Jinja2 template rendering."""
        return {
            # Personal Info
            "fullName": cv.personalInfo.fullName or "",
            "jobTitle": cv.header.get("jobTitle") or "",
            "email": cv.personalInfo.email or "",
            "phone": cv.personalInfo.phone or "",
            "location": cv.personalInfo.location or "",
            "summary": cv.personalInfo.summary or "",

            # Skills
            "skills": cv.skills or [],

            # Experience
            "experience": [
                {
                    "company": exp.company,
                    "title": exp.title,
                    "role": exp.role,
                    "startDate": exp.startDate,
                    "endDate": exp.endDate,
                    "location": exp.location,
                    "projectName": exp.projectName,
                    "projectInformation": exp.projectInformation,
                    "clients": exp.clients,
                    "technology": exp.technology or [],
                    "description": exp.description,
                    "achievements": exp.achievements or []
                }
                for exp in cv.experience
            ] if cv.experience else [],

            # Education
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field": edu.field,
                    "startDate": edu.startDate,
                    "endDate": edu.endDate
                }
                for edu in cv.education
            ] if cv.education else [],

            # Projects
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description,
                    "technologies": proj.technologies or [],
                    "url": proj.url
                }
                for proj in cv.projects
            ] if cv.projects else [],

            # Certifications
            "certifications": [
                {
                    "name": cert.name,
                    "issuer": cert.issuer,
                    "date": cert.date
                }
                for cert in cv.certifications
            ] if cv.certifications else [],

            # Languages
            "languages": cv.languages or [],

            # Technical Skills with proficiency
            "technicalSkills": {
                "primary": cv.technicalSkills.get("primary", []) if cv.technicalSkills else [],
                "secondary": cv.technicalSkills.get("secondary", []) if cv.technicalSkills else []
            },

            # Professional Summary
            "professionalSummary": cv.professionalSummary or [],

            # Header info
            "header": cv.header or {}
        }

    def _convert_docx_to_pdf(self, docx_path: str, pdf_path: str) -> None:
        """Convert DOCX to PDF using available tools."""
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")

        # Try docx2pdf first (Windows/macOS with Word installed)
        if self._try_docx2pdf_conversion(docx_path, pdf_path):
            return

        # Fallback to LibreOffice
        if self._try_libreoffice_conversion(docx_path, pdf_path):
            return

        # All methods failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF conversion failed: docx2pdf or LibreOffice required"
        )

    def _try_docx2pdf_conversion(self, docx_path: str, pdf_path: str) -> bool:
        """Try to convert using docx2pdf library."""
        try:
            from docx2pdf import convert
            convert(docx_path, pdf_path)
            return os.path.exists(pdf_path)
        except ImportError:
            return False
        except Exception as e:
            print(f"docx2pdf conversion failed: {e}")
            return False

    def _try_libreoffice_conversion(self, docx_path: str, pdf_path: str) -> bool:
        """Try to convert using LibreOffice headless conversion."""
        try:
            output_dir = os.path.dirname(pdf_path)

            # Build command for LibreOffice
            cmd = [
                "soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                docx_path
            ]

            # Run conversion
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )

            # Check if conversion succeeded
            if result.returncode == 0 and os.path.exists(pdf_path):
                return True

            return False
        except FileNotFoundError:
            # LibreOffice not installed
            return False
        except subprocess.TimeoutExpired:
            print("LibreOffice conversion timed out")
            return False
        except Exception as e:
            print(f"LibreOffice conversion error: {e}")
            return False

