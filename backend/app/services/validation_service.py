"""Validation service — checks completeness and field correctness."""
from __future__ import annotations

import re
from typing import List

from app.models.cv_schema import CvSchema
from app.core.exceptions import CvSchemaValidationError


class ValidationService:
    def validate(self, cv: CvSchema) -> None:
        """Raise CvSchemaValidationError if hard constraints are violated."""
        errors = []
        email = cv.personalInfo.email
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            errors.append("personalInfo.email has an invalid format")
        if errors:
            raise CvSchemaValidationError("; ".join(errors))

    def get_missing_fields(self, cv: CvSchema) -> List[str]:
        """Return a list of field paths that are empty or missing."""
        missing: List[str] = []
        pi = cv.personalInfo
        for field in ("fullName", "email", "phone", "location", "summary"):
            if not getattr(pi, field, ""):
                missing.append(f"personalInfo.{field}")
        if not cv.skills:
            missing.append("skills")
        if not cv.experience:
            missing.append("experience")
        if not cv.education:
            missing.append("education")
        return missing

    def completeness_score(self, cv: CvSchema) -> int:
        """Return a 0-100 score representing how complete the CV is."""
        total_fields = 8  # personalInfo fields + skills + experience + education
        missing = self.get_missing_fields(cv)
        filled = total_fields - len(missing)
        return max(0, min(100, int(filled / total_fields * 100)))
