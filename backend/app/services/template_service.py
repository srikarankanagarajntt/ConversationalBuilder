"""Template service — manages available CV templates."""
from __future__ import annotations

from typing import List

from fastapi import HTTPException, status
from app.models.responses import TemplateOption

# Static template catalogue — replace with DB/S3 lookup in production
TEMPLATES: List[TemplateOption] = [
    TemplateOption(
        templateId="ntt-classic",
        templateName="NTT DATA Classic",
        description="Clean, professional single-column layout aligned with NTT DATA branding.",
        previewImageUrl="/static/templates/ntt-classic.png",
    ),
    TemplateOption(
        templateId="ntt-modern",
        templateName="NTT DATA Modern",
        description="Two-column modern layout with accent colour and skills highlights.",
        previewImageUrl="/static/templates/ntt-modern.png",
    ),
    TemplateOption(
        templateId="minimal",
        templateName="Minimal",
        description="Minimalist white template suitable for all roles.",
        previewImageUrl="/static/templates/minimal.png",
    ),
]


class TemplateService:
    def get_templates(self) -> List[TemplateOption]:
        return TEMPLATES

    def get_template_by_id(self, template_id: str) -> TemplateOption:
        for t in TEMPLATES:
            if t.templateId == template_id:
                return t
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found.",
        )
