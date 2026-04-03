"""CV schema manipulation — merge updates and build diffs."""
from __future__ import annotations

from typing import Any, Dict

from app.models.cv_schema import CvSchema, PersonalInfo, ExperienceEntry, EducationEntry


class CvSchemaService:
    def merge_partial_update(self, current: CvSchema, patch: Dict[str, Any]) -> CvSchema:
        """
        Merge a partial CV dict (from LLM extraction or user edit) into the current draft.
        Preserves existing values when patch is empty for a field.
        """
        current_dict = current.model_dump()
        merged = self._deep_merge(current_dict, patch)
        return CvSchema(**merged)

    def _deep_merge(self, base: dict, patch: dict) -> dict:
        result = dict(base)
        for key, value in patch.items():
            if key not in result:
                result[key] = value
            elif isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list) and value:
                # For lists, replace only when the incoming list is non-empty
                result[key] = value
            elif value not in (None, "", [], {}):
                result[key] = value
        return result
