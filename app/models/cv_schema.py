from __future__ import annotations
from datetime import datetime, date
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Location(BaseModel):
    company_name: str = ""
    address_line_1: str = ""
    address_line_2: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = ""

class ContactInfo(BaseModel):
    phone_number: str = ""
    email_id: EmailStr | None = None
    official_email_id: EmailStr | None = None

class PersonalInfo(BaseModel):
    nationality: str = ""

class Header(BaseModel):
    full_name: str = ""
    portal_id: str = ""
    headline: str = ""
    job_title: str = ""
    location: Location = Field(default_factory=Location)
    contact: ContactInfo = Field(default_factory=ContactInfo)
    personal: PersonalInfo = Field(default_factory=PersonalInfo)

class SkillItem(BaseModel):
    skill_name: str
    category: str = ""
    proficiency: Literal["beginner", "intermediate", "advanced", "expert"] | None = None

class TechnicalSkills(BaseModel):
    primary: list[SkillItem] = Field(default_factory=list)
    secondary: list[SkillItem] = Field(default_factory=list)

class EmploymentPeriod(BaseModel):
    start: date | None = None
    end: date | None = None
    display_text: str = ""

class WorkExperienceItem(BaseModel):
    employer: str = ""
    employment_period: EmploymentPeriod = Field(default_factory=EmploymentPeriod)
    position: str = ""
    project_title: str = ""
    client: str = ""
    technology: list[str] = Field(default_factory=list)
    project_description: str = ""
    responsibilities: list[str] = Field(default_factory=list)

class PersonalDetails(BaseModel):
    languages_known: list[str] = Field(default_factory=list)
    permanent_address: str = ""

class Declaration(BaseModel):
    statement: str = ""
    place: str = ""
    signature_name: str = ""

class Meta(BaseModel):
    template_version: str = ""
    source_type: Literal["chat", "voice", "upload", "mixed"] = "chat"
    language: str = "en"
    last_updated: datetime | None = None

class CvSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    meta: Meta = Field(default_factory=Meta)
    header: Header = Field(default_factory=Header)
    professional_summary: list[str] = Field(default_factory=list, alias="professionalSummary")
    technical_skills: TechnicalSkills = Field(default_factory=TechnicalSkills, alias="technicalSkills")
    current_responsibilities: list[str] = Field(default_factory=list, alias="currentResponsibilities")
    work_experience: list[WorkExperienceItem] = Field(default_factory=list, alias="workExperience")
    personal_details: PersonalDetails = Field(default_factory=PersonalDetails, alias="personalDetails")
    declaration: Declaration = Field(default_factory=Declaration)

    def missing_required_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.header.full_name.strip():
            missing.append("header.fullName")
        if not self.header.job_title.strip():
            missing.append("header.jobTitle")
        if not (self.header.contact.email_id or self.header.contact.official_email_id):
            missing.append("header.contact.emailId|officialEmailId")
        if not self.professional_summary:
            missing.append("professionalSummary")
        if not self.technical_skills.primary:
            missing.append("technicalSkills.primary")
        if not self.work_experience:
            missing.append("workExperience")
        if not self.declaration.place.strip():
            missing.append("declaration.place")
        return missing
