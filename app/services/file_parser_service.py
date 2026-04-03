from fastapi import UploadFile
from app.models.responses import UploadCvResponse
from app.services.state_service import get_state_service
from app.services.cv_schema_service import get_cv_schema_service

class FileParserService:
    async def parse_cv_upload(self, session_id: str, upload: UploadFile) -> UploadCvResponse:
        extracted_data = {
            "header": {"fullName": "Mock Candidate", "jobTitle": "System Integration Specialist"},
            "professionalSummary": ["Mock extracted summary from uploaded resume."],
        }
        state_service = get_state_service()
        session = state_service.get_session(session_id)
        session.cv_schema = get_cv_schema_service().merge_partial_update(session.cv_schema, extracted_data)
        state_service.update_session(session)
        missing_fields = get_cv_schema_service().find_missing_fields(session.cv_schema)
        return UploadCvResponse(session_id=session_id, extracted_data=extracted_data, missing_fields=missing_fields)

_file_parser_service = FileParserService()

def get_file_parser_service() -> FileParserService:
    return _file_parser_service
