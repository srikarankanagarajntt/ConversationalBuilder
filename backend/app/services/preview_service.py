"""Preview service — assembles preview-ready CV model."""
from __future__ import annotations

from app.models.cv_schema import CvSchema


class PreviewService:
    def build_preview(self, cv: CvSchema) -> dict:
        """
        Return a dict enriched with display-friendly fields for the Angular
        preview component.  Extend this to apply template-specific ordering.
        """
        return cv.model_dump()
