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
                # Special handling for lists of objects (experience, education, certifications, projects)
                # Merge by index rather than replacing entire list
                if key in ["experience", "education", "certifications", "projects"]:
                    # Merge list items by index, preserving existing items not in patch
                    merged_list = list(result[key])  # Start with base list
                    for i, item in enumerate(value):
                        if i < len(merged_list) and isinstance(merged_list[i], dict) and isinstance(item, dict):
                            # Merge the item at this index intelligently
                            merged_list[i] = self._merge_list_item(merged_list[i], item)
                        elif i >= len(merged_list):
                            # Add new items if they don't exist
                            merged_list.append(item)
                    result[key] = merged_list
                else:
                    # For other lists, replace only when the incoming list is non-empty
                    result[key] = value
            elif value not in (None, "", [], {}):
                result[key] = value
        return result

    def _merge_list_item(self, base_item: dict, patch_item: dict) -> dict:
        """
        Merge a single list item (e.g., experience entry) by preserving existing fields
        and only updating fields that are non-empty in the patch.
        Normalizes field types (e.g., converts list clients to string).
        """
        result = dict(base_item)
        for key, value in patch_item.items():
            # Only update if the patch value is not empty
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._deep_merge(result[key], value)
            elif value not in (None, "", [], {}):
                result[key] = value
            # If value is empty/None/empty list, keep the existing value
        
        # Normalize field types for experience entries
        result = self._normalize_experience_entry(result)
        return result

    def _normalize_experience_entry(self, entry: dict) -> dict:
        """Normalize experience entry fields to expected types."""
        # Fields that should be strings but might come as lists
        string_fields = ['clients', 'projectName', 'projectInformation', 'description', 'company', 'title', 'role']
        
        for field in string_fields:
            if field in entry and isinstance(entry[field], list):
                # Convert list to comma-separated string
                entry[field] = ", ".join(str(item).strip() for item in entry[field] if item)
        
        return entry
