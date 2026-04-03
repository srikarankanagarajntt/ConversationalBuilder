from app.models.cv_schema import CvSchema

class CvSchemaService:
    def merge_partial_update(self, schema: CvSchema, updates: dict) -> CvSchema:
        header = updates.get("header", {})
        if isinstance(header, dict):
            if "fullName" in header:
                schema.header.full_name = header["fullName"]
            if "jobTitle" in header:
                schema.header.job_title = header["jobTitle"]

        if "professionalSummary" in updates and isinstance(updates["professionalSummary"], list):
            schema.professional_summary = updates["professionalSummary"]

        return schema

    def find_missing_fields(self, schema: CvSchema) -> list[str]:
        return schema.missing_required_fields()

_cv_schema_service = CvSchemaService()

def get_cv_schema_service() -> CvSchemaService:
    return _cv_schema_service
