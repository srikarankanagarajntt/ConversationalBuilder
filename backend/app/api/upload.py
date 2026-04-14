"""Upload endpoint — CV file ingestion and structured extraction."""
from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.responses import UploadCvResponse
from app.models.cv_schema import CvSchema, PersonalInfo, ExperienceEntry
from app.services.file_parser_service import FileParserService
from app.services.cv_schema_service import CvSchemaService
from app.services.llm_service import LLMService
from app.services.state_service import StateService
from app.services.validation_service import ValidationService

router = APIRouter()
state_service = StateService()
cv_schema_service = CvSchemaService()
validation_service = ValidationService()
file_parser_service = FileParserService()
llm_service = LLMService()


@router.post("/cv", response_model=UploadCvResponse)
async def upload_cv(
    sessionId: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a CV file and extract information."""
    # File type validation
    allowed_extensions = ['.pdf', '.docx']
    file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": f"Only PDF and DOCX files are allowed. Received: {file_extension}",
                    "details": [
                        {
                            "field": "file",
                            "issue": f"Unsupported file type: {file_extension}"
                        }
                    ]
                }
            }
        )

    raw_bytes = await file.read()
    content_type = file.content_type or ""

    # Extract text
    try:
        raw_text = await file_parser_service.extract_text(raw_bytes, content_type)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "FILE_PARSE_ERROR",
                    "message": f"Failed to parse file: {str(e)}",
                    "details": []
                }
            }
        )

    # Use LLM to extract and populate canonical CV schema from raw text
    try:
        extracted_data = await llm_service.extract_cv_data(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "CV_EXTRACTION_ERROR",
                    "message": f"Failed to extract CV data: {str(e)}",
                    "details": []
                }
            }
        )

    # Get session
    session = state_service.get_session(sessionId)

    # Map extracted data to canonical CvSchema
    updated_cv = _map_to_cv_schema(session.cvDraft, extracted_data)

    # Get missing fields
    missing_fields = validation_service.get_missing_fields(updated_cv)

    # Update session
    state_service.update_cv(sessionId, updated_cv)

    return UploadCvResponse(
        sessionId=sessionId,
        cvDraft=updated_cv,
        missingFields=missing_fields,
    )


def _map_to_cv_schema(base_cv: CvSchema, extracted_data: dict) -> CvSchema:
    """
    Map extracted LLM data to canonical CvSchema.
    """
    # Create personal info from header
    header = extracted_data.get("header", {})
    personal_info = PersonalInfo(
        fullName=header.get("fullName", ""),
        email=header.get("email", ""),
        phone=header.get("phone", ""),
        summary="\n".join(extracted_data.get("professionalSummary", []))
    )

    # Extract work experience
    work_experiences = []
    for exp in extracted_data.get("workExperience", []):
        work_experiences.append(
            ExperienceEntry(
                company=exp.get("employer", ""),
                title=exp.get("position", ""),
                achievements=[exp.get("project_description", "")] if exp.get("project_description") else []
            )
        )

    # Extract skills
    skills = []
    technical_skills = extracted_data.get("technicalSkills", {})
    for skill in technical_skills.get("primary", []):
        skills.append(skill.get("skill_name", ""))
    for skill in technical_skills.get("secondary", []):
        skills.append(skill.get("skill_name", ""))

    # Normalize technical skills to camelCase
    normalized_technical_skills = {}
    for key in ["primary", "secondary"]:
        if key in technical_skills:
            normalized_technical_skills[key] = [
                {
                    "skillName": skill.get("skill_name", ""),
                    "proficiency": skill.get("proficiency", "")
                }
                for skill in technical_skills[key]
            ]

    # Normalize work experience to camelCase
    normalized_work_experience = [
        {
            "employer": exp.get("employer", ""),
            "position": exp.get("position", ""),
            "projectDescription": exp.get("project_description", "")
        }
        for exp in extracted_data.get("workExperience", [])
    ]

    # Update and return CV schema
    base_cv.personalInfo = personal_info
    base_cv.experience = work_experiences
    base_cv.skills = skills
    base_cv.header = header
    base_cv.professionalSummary = extracted_data.get("professionalSummary", [])
    base_cv.technicalSkills = normalized_technical_skills
    base_cv.workExperience = normalized_work_experience

    return base_cv

