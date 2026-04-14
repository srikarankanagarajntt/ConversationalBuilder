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

        # Check header fields
        if not cv.header.get("fullName"):
            missing.append("header.fullName")
        if not cv.header.get("jobTitle"):
            missing.append("header.jobTitle")
        if not cv.header.get("email"):
            missing.append("header.email")

        # Check professional summary
        if not cv.professionalSummary:
            missing.append("professionalSummary")

        # Check technical skills
        if not cv.technicalSkills.get("primary"):
            missing.append("technicalSkills.primary")

        # Check work experience
        if not cv.workExperience:
            missing.append("workExperience")

        # Check declaration.place (assuming it's not present, add if needed)
        # For now, skip

        return missing

    def completeness_score(self, cv: CvSchema) -> int:
        """Return a 0-100 score representing how complete the CV is."""
        total_fields = 8  # personalInfo fields + skills + experience + education
        missing = self.get_missing_fields(cv)
        filled = total_fields - len(missing)
        return max(0, min(100, int(filled / total_fields * 100)))
