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
        description="Professional single-column layout for work. Export as PDF.",
        previewImageUrl="/static/templates/ntt-classic.png",
    ),
    TemplateOption(
        templateId="ntt-one-pager",
        templateName="NTT DATA One Pager",
        description="Compact one-page summary format. Export as PPT.",
        previewImageUrl="/static/templates/ntt-one-pager.png",
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
