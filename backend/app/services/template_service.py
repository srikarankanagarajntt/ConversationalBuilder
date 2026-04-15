"""Template service — manages available CV templates."""
from __future__ import annotations

import base64
import os
import json
from typing import List
from pathlib import Path

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

# Supported template file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.html', '.htm'}


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


def _load_mock_data() -> dict:
    """Load mock CV data from cv_schema.json"""
    try:
        mock_data_path = os.path.join(MOCK_DATA_DIR, "cv_schema.json")
        with open(mock_data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _discover_templates() -> List[TemplateOption]:
    """Dynamically discover template files in the template directory."""
    templates = []

    if not os.path.exists(TEMPLATE_DIR):
        return templates

    # Scan template directory for supported file types
    for file_path in sorted(Path(TEMPLATE_DIR).iterdir()):
        # Skip directories and mock_data
        if file_path.is_dir() or file_path.name == "mock_data":
            continue

        # Check if file has supported extension
        file_ext = file_path.suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            continue

        # Extract filename (with extension) - use as templateId
        file_name = file_path.name
        template_id = file_name  # Use filename directly as ID

        # Get file type without dot
        file_type = file_ext.lstrip('.')

        # Create human-readable template name
        template_name = file_name.rsplit('.', 1)[0]  # Remove extension
        template_name = template_name.replace('_', ' ').replace('-', ' ').title()

        # Create TemplateOption
        template = TemplateOption(
            templateId=template_id,
            templateName=template_name,
            description=f"{template_name} - {file_type.upper()} format",
            fileType=file_type,
            fileBase64=""  # Will be loaded on demand
        )

        templates.append(template)

    return templates


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
        """Initialize templates by discovering files from template directory."""
        self._templates_loaded = False
        self._templates: List[TemplateOption] = []
        self._mock_data = _load_mock_data()
        self._load_template_files()

    def _load_template_files(self):
        """Discover and load template files from template directory."""
        if self._templates_loaded:
            return

        # Discover templates from directory
        self._templates = _discover_templates()

        # Load base64 content for each discovered template
        for template in self._templates:
            file_path = os.path.join(TEMPLATE_DIR, f"{template.templateName.replace(' ', '_')}.{template.fileType}")

            # Try exact filename match
            if not os.path.exists(file_path):
                # Try case-insensitive search
                for file in Path(TEMPLATE_DIR).iterdir():
                    if file.is_file() and file.suffix.lower() == f".{template.fileType}":
                        # Match by ID
                        if template.templateId.lower() in file.name.lower().replace(' ', '-'):
                            file_path = str(file)
                            break

            if os.path.exists(file_path):
                template.fileBase64 = _load_file_as_base64(file_path)
            else:
                # Try to find by template ID
                for file in Path(TEMPLATE_DIR).iterdir():
                    if file.is_file() and file.suffix.lower() == f".{template.fileType}":
                        template.fileBase64 = _load_file_as_base64(str(file))
                        break

        self._templates_loaded = True

    def get_templates(self) -> List[TemplateOption]:
        """Return available CV template options with base64 encoded files."""
        self._load_template_files()
        return self._templates

    def get_template_by_id(self, template_id: str) -> TemplateOption:
        """Get a template by ID."""
        self._load_template_files()
        for t in self._templates:
            if t.templateId == template_id:
                return t
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found.",
        )

    def get_mock_cv_data(self) -> dict:
        """Get the mock CV data for testing/preview purposes."""
        return self._mock_data

