from app.models.cv_schema import CvSchema
from app.services.cv_schema_service import get_cv_schema_service

class ValidationService:
    def find_missing_fields(self, schema: CvSchema) -> list[str]:
        return get_cv_schema_service().find_missing_fields(schema)

_validation_service = ValidationService()

def get_validation_service() -> ValidationService:
    return _validation_service
