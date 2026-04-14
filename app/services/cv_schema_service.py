from datetime import datetime
from app.models.cv_schema import CvSchema, WorkExperienceItem, SkillItem

class CvSchemaService:
    def merge_partial_update(self, schema: CvSchema, updates: dict) -> CvSchema:
        """
        Merge partial updates into the CV schema.
        Handles various field formats and performs validation.
        """
        # Update header information
        header = updates.get("header", {})
        if isinstance(header, dict):
            full_name = header.get("fullName", header.get("full_name"))
            if isinstance(full_name, str) and full_name.strip():
                schema.header.full_name = full_name.strip()

            job_title = header.get("jobTitle", header.get("job_title"))
            if isinstance(job_title, str) and job_title.strip():
                schema.header.job_title = job_title.strip()

            # Update contact information
            if header.get("email"):
                try:
                    schema.header.contact.email_id = header.get("email")
                except (ValueError, Exception):
                    pass

            if header.get("phone"):
                schema.header.contact.phone_number = header.get("phone")

        # Update professional summary
        professional_summary = updates.get("professionalSummary", updates.get("professional_summary"))
        if isinstance(professional_summary, list):
            schema.professional_summary = [str(item).strip() for item in professional_summary if str(item).strip()]

        # Update technical skills
        technical_skills = updates.get("technicalSkills", updates.get("technical_skills"))
        if isinstance(technical_skills, dict):
            # Handle primary skills
            primary = technical_skills.get("primary", [])
            if isinstance(primary, list):
                schema.technical_skills.primary = [
                    SkillItem(**skill) if isinstance(skill, dict) else SkillItem(skill_name=str(skill))
                    for skill in primary
                ]

            # Handle secondary skills
            secondary = technical_skills.get("secondary", [])
            if isinstance(secondary, list):
                schema.technical_skills.secondary = [
                    SkillItem(**skill) if isinstance(skill, dict) else SkillItem(skill_name=str(skill))
                    for skill in secondary
                ]

        # Update work experience
        work_experience = updates.get("workExperience", updates.get("work_experience"))
        if isinstance(work_experience, list):
            experience_items = []
            for exp in work_experience:
                if isinstance(exp, dict):
                    exp_item = WorkExperienceItem(
                        employer=exp.get("employer", "").strip(),
                        position=exp.get("position", "").strip(),
                        project_title=exp.get("project_title", exp.get("projectTitle", "")).strip(),
                        project_description=exp.get("project_description", exp.get("projectDescription", "")).strip(),
                    )
                    experience_items.append(exp_item)
            if experience_items:
                schema.work_experience = experience_items

        # Update meta information
        schema.meta.source_type = "upload"
        schema.meta.last_updated = datetime.now()

        return schema

    def find_missing_fields(self, schema: CvSchema) -> list[str]:
        """Find missing required fields in the CV schema."""
        return schema.missing_required_fields()

_cv_schema_service = CvSchemaService()

def get_cv_schema_service() -> CvSchemaService:
    return _cv_schema_service
