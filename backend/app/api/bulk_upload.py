"""Bulk upload endpoint — handle multiple CV file uploads."""
from __future__ import annotations

import asyncio
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from typing import List
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.models.responses import UploadCvResponse
from app.models.cv_schema import CvSchema, PersonalInfo, ExperienceEntry, EducationEntry, CertificationEntry
from app.services.file_parser_service import FileParserService
from app.services.cv_schema_service import CvSchemaService
from app.services.llm_service import LLMService
from app.services.state_service import StateService
from app.services.validation_service import ValidationService
from app.services.technical_skills_service import TechnicalSkillsService
from app.services.bulk_service import BulkService

router = APIRouter()

file_parser_service = FileParserService()
cv_schema_service = CvSchemaService()
llm_service = LLMService()
state_service = StateService()
validation_service = ValidationService()
technical_skills_service = TechnicalSkillsService()
bulk_service = BulkService()


class BaseResponseModel(BaseModel):
    """Base model with camelCase serialization."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class BulkCvItemResponse(BaseResponseModel):
    """Single CV item in bulk upload response."""
    sessionId: str
    cvDraft: CvSchema
    missingFields: List[str] = []


class BulkUploadResponse(BaseResponseModel):
    """Response for bulk upload."""
    bulkId: str
    fileCount: int
    failedCount: int
    status: str = "received"
    cVs: List[BulkCvItemResponse] = []
    errors: List[dict] = []


@router.post("/bulk-cv")
async def upload_bulk_cv(
    sessionId: str = Form(...),
    files: List[UploadFile] = File(...),
) -> BulkUploadResponse:
    """Upload multiple CV files for bulk processing.
    
    Args:
        sessionId: Session ID
        files: List of CV files to upload
        
    Returns:
        List of parsed CV objects with missing fields and bulk job ID
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "NO_FILES_PROVIDED",
                    "message": "At least one file must be provided",
                }
            }
        )
    
    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "TOO_MANY_FILES",
                    "message": "Maximum 50 files allowed per bulk upload",
                }
            }
        )
    
    # Parse all files in parallel
    cv_list: List[CvSchema] = []
    errors: List[dict] = []
    
    # Process files concurrently
    tasks = [_parse_single_file(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append({
                "fileIndex": idx,
                "filename": files[idx].filename,
                "error": str(result)
            })
        elif result is not None:
            cv_list.append(result)
    
    if not cv_list:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "FILE_PARSE_ERROR",
                    "message": "Failed to parse any files",
                    "errors": errors
                }
            }
        )
    
    # Create bulk job to store CVs for later processing
    bulk_job = bulk_service.create_bulk_job(cv_list)
    
    # Build response with array of CV objects
    cv_responses: List[BulkCvItemResponse] = []
    for cv in cv_list:
        missing_fields = validation_service.get_missing_fields(cv)
        cv_responses.append(
            BulkCvItemResponse(
                sessionId=sessionId,
                cvDraft=cv,
                missingFields=missing_fields
            )
        )
    
    return BulkUploadResponse(
        bulkId=bulk_job["bulkId"],
        fileCount=len(cv_list),
        failedCount=len(errors),
        status="received",
        cVs=cv_responses,
        errors=errors
    )


async def _parse_single_file(file: UploadFile) -> CvSchema | None:
    """Parse a single CV file.
    
    Args:
        file: Uploaded file
        
    Returns:
        Parsed CV schema or None if error
    """
    # File type validation
    allowed_extensions = ['.pdf', '.docx']
    file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_extension not in allowed_extensions:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    raw_bytes = await file.read()
    content_type = file.content_type or ""
    
    # Enforce max 10 pages for PDF
    if file_extension == ".pdf":
        try:
            import io
            import PyPDF2
            
            reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
            page_count = len(reader.pages)
            if page_count > 10:
                raise ValueError(f"PDF contains {page_count} pages (max 10 allowed)")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Unable to validate PDF page count: {str(e)}")
    
    # Extract text
    try:
        raw_text = await file_parser_service.extract_text(raw_bytes, content_type)
    except Exception as e:
        raise ValueError(f"Failed to parse file: {str(e)}")
    
    # Extract CV data using LLM (same as regular upload)
    try:
        extracted_data = await llm_service.extract_cv_data(raw_text)
    except Exception as e:
        raise ValueError(f"Failed to extract CV data: {str(e)}")
    
    # Map to CvSchema (same as regular upload)
    try:
        cv_schema = await _map_to_cv_schema(CvSchema(), extracted_data, technical_skills_service)
    except Exception as e:
        raise ValueError(f"Failed to map CV schema: {str(e)}")
    
    return cv_schema


async def _map_to_cv_schema(base_cv: CvSchema, extracted_data: dict, technical_skills_service: TechnicalSkillsService) -> CvSchema:
    """
    Map extracted LLM data to canonical CvSchema with intelligent skill generation.
    Uses TechnicalSkillsService to generate 7 primary + 7 secondary skills.
    """
    # Create personal info from header
    header = extracted_data.get("header", {})
    personal_info = PersonalInfo(
        fullName=header.get("fullName", ""),
        email=header.get("email", ""),
        phone=header.get("phone", ""),
        location=header.get("location", ""),
        role=header.get("jobTitle", ""),
        summary="\n".join(extracted_data.get("professionalSummary", []))
    )

    # Extract work experience with consolidated structure
    work_experiences = []
    for exp in extracted_data.get("workExperience", []):
        work_experiences.append(
            ExperienceEntry(
                company=exp.get("employer", ""),
                title=exp.get("position", ""),
                role=exp.get("position", ""),
                startDate=exp.get("startDate", ""),
                endDate=exp.get("endDate", ""),
                location=exp.get("location", ""),
                clients=exp.get("clients", ""),
                projectName=exp.get("projectName", ""),
                projectInformation=exp.get("projectInformation", ""),
                technology=exp.get("technology", []) if isinstance(exp.get("technology", []), list) else [],
                description=exp.get("project_description", ""),
                achievements=exp.get("achievements", []) if isinstance(exp.get("achievements", []), list) else []
            )
        )

    # Extract certifications
    certifications = []
    for cert in extracted_data.get("certifications", []):
        certifications.append(
            CertificationEntry(
                name=cert.get("name", ""),
                issuer=cert.get("issuer", ""),
                date=cert.get("date", "")
            )
        )

    # Extract education
    educations = []
    for edu in extracted_data.get("education", []):
        educations.append(
            EducationEntry(
                institution=edu.get("institution", ""),
                degree=edu.get("degree", ""),
                field=edu.get("field", ""),
                startDate=edu.get("startDate", ""),
                endDate=edu.get("endDate", "")
            )
        )

    # Extract skills from both extracted technical skills and basic skills list
    extracted_skills = []
    technical_skills_raw = extracted_data.get("technicalSkills", {})
    for skill in technical_skills_raw.get("primary", []):
        extracted_skills.append(skill.get("skill_name", ""))
    for skill in technical_skills_raw.get("secondary", []):
        extracted_skills.append(skill.get("skill_name", ""))
    
    # Get professional summary for intelligent skill generation
    professional_summary = "\n".join(extracted_data.get("professionalSummary", []))
    
    # Use TechnicalSkillsService to intelligently generate 7 primary + 7 secondary skills
    # This works for any professional role (preset or custom)
    if professional_summary and extracted_skills:
        technical_skills_generated = await technical_skills_service.categorize_skills_async(
            professional_summary, 
            extracted_skills
        )
        normalized_technical_skills = technical_skills_generated
    else:
        # Fallback to basic normalization if no summary/skills
        normalized_technical_skills = {}
        for key in ["primary", "secondary"]:
            if key in technical_skills_raw:
                normalized_technical_skills[key] = [
                    {
                        "skillName": skill.get("skill_name", ""),
                        "proficiency": skill.get("proficiency", "")
                    }
                    for skill in technical_skills_raw[key]
                ]

    # Extract all skill names for basic skills list
    skills = []
    for skill_dict in normalized_technical_skills.get("primary", []):
        skills.append(skill_dict.get("skillName", ""))
    for skill_dict in normalized_technical_skills.get("secondary", []):
        skills.append(skill_dict.get("skillName", ""))

    # Update and return CV schema
    base_cv.personalInfo = personal_info
    base_cv.experience = work_experiences
    base_cv.education = educations
    base_cv.skills = skills
    base_cv.certifications = certifications
    base_cv.header = header
    base_cv.professionalSummary = extracted_data.get("professionalSummary", [])
    base_cv.technicalSkills = normalized_technical_skills

    return base_cv
