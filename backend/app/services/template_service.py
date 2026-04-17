"""Template service — manages available CV templates."""
from __future__ import annotations

import base64
import os
import json
from typing import List

from fastapi import HTTPException, status
from app.models.responses import TemplateOption


# Template base directory
TEMPLATE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "template"
)

# Mock data directory
MOCK_DATA_DIR = os.path.join(TEMPLATE_DIR, "mock_data")


def _load_file_as_base64(file_path: str) -> str:
    """Load a file and convert to base64."""
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            return base64.b64encode(file_content).decode("utf-8")
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template file not found: {file_path}",
        )


# Static template catalogue with file references
TEMPLATES: List[TemplateOption] = [
    TemplateOption(
        templateId="ntt-data-docx",
        templateName="NTT DATA Resume Template (Professional)",
        description="Professional resume template in Microsoft Word format. Ideal for job applications.",
        fileType="docx",
        fileBase64=""  # Loaded dynamically
    ),
    TemplateOption(
        templateId="java-architect-pptx",
        templateName="NTT DATA Resume Template (Classic)",
        description="Executive resume template in PowerPoint format. Perfect for presentations.",
        fileType="pptx",
        fileBase64=""  # Loaded dynamically
    ),
]


def _load_mock_data() -> dict:
    """Load mock CV data from cv_schema.json"""
    try:
        mock_data_path = os.path.join(MOCK_DATA_DIR, "cv_schema.json")
        with open(mock_data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _get_mock_preview_data() -> dict:
    """Get mock data for template preview"""
    mock_cv = _load_mock_data()
    return {
        "name": mock_cv.get("header", {}).get("fullName", "John Bapist"),
        "title": mock_cv.get("header", {}).get("jobTitle", "Senior Software Engineer"),
        "summary": ", ".join(mock_cv.get("professionalSummary", [])[:2]),
        "experience": mock_cv.get("workExperience", []),
        "skills": mock_cv.get("technicalSkills", {}).get("primary", [])[:5]
    }


class TemplateService:
    def __init__(self):
        """Initialize templates with base64 encoded file content."""
        self._templates_loaded = False
        self._mock_data = _load_mock_data()
        self._mock_preview = _get_mock_preview_data()
        self._load_template_files()

    def _load_template_files(self):
        """Load template files and encode to base64."""
        if self._templates_loaded:
            return

        # Load NTT DATA DOCX template
        ntt_data_path = os.path.join(TEMPLATE_DIR, "NTT_DATA_Resume_Templates.docx")
        TEMPLATES[0].fileBase64 = _load_file_as_base64(ntt_data_path)
        
        # Try to load NTT DATA preview image
        ntt_preview_path = os.path.join(TEMPLATE_DIR, "ntt-data-preview.png")
        if os.path.exists(ntt_preview_path):
            TEMPLATES[0].previewImageBase64 = _load_file_as_base64(ntt_preview_path)

        # Load Java Architect PPTX template
        java_architect_path = os.path.join(TEMPLATE_DIR, "Resume - Java Lead Architect.pptx")
        TEMPLATES[1].fileBase64 = _load_file_as_base64(java_architect_path)
        
        # Try to load Java Architect preview image
        java_preview_path = os.path.join(TEMPLATE_DIR, "java-architect-preview.png")
        if os.path.exists(java_preview_path):
            TEMPLATES[1].previewImageBase64 = _load_file_as_base64(java_preview_path)

        self._templates_loaded = True

    def get_templates(self) -> List[TemplateOption]:
        """Return available CV template options with base64 encoded files and mock data."""
        self._load_template_files()
        return TEMPLATES

    def get_template_by_id(self, template_id: str) -> TemplateOption:
        """Get a template by ID."""
        self._load_template_files()
        for t in TEMPLATES:
            if t.templateId == template_id:
                return t
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found.",
        )

    def get_mock_cv_data(self) -> dict:
        """Get the mock CV data for testing/preview purposes."""
        return self._mock_data

