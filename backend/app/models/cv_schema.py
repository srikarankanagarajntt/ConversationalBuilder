"""Canonical CV schema — single source of truth for all flows."""
from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchemaModel(BaseModel):
    """Base model with camelCase serialization."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class PersonalInfo(BaseSchemaModel):
    fullName: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    role: str = ""  # Job title/role of the person


class ExperienceEntry(BaseSchemaModel):
    company: str = ""
    title: str = ""  # Job title
    role: str = ""  # Specific role/position
    startDate: str = ""
    endDate: str = ""
    location: str = ""  # Work location
    clients: str = ""  # Client organization
    projectName: str = ""  # Specific project name
    projectInformation: str = ""  # Detailed project information/description
    technology: List[str] = Field(default_factory=list)  # Technologies used
    description: str = ""  # Overall job description
    achievements: List[str] = Field(default_factory=list)  # Roles and responsibilities (bulleted)


class EducationEntry(BaseSchemaModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    startDate: str = ""
    endDate: str = ""


class ProjectEntry(BaseSchemaModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    url: str = ""


class CertificationEntry(BaseSchemaModel):
    name: str = ""
    issuer: str = ""
    date: str = ""


class TemplateInfo(BaseSchemaModel):
    templateId: str = ""
    templateName: str = ""


class CvSchema(BaseSchemaModel):
    sessionId: str = ""
    personalInfo: PersonalInfo = Field(default_factory=PersonalInfo)
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    template: TemplateInfo = Field(default_factory=TemplateInfo)
    # Additional fields from upload extraction
    header: Dict[str, str] = Field(default_factory=dict)
    professionalSummary: List[str] = Field(default_factory=list)
    technicalSkills: Dict[str, List[Dict[str, str]]] = Field(default_factory=dict)
