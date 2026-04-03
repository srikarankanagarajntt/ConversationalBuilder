"""Canonical CV schema — single source of truth for all flows."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    fullName: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    summary: str = ""


class ExperienceEntry(BaseModel):
    company: str = ""
    title: str = ""
    startDate: str = ""
    endDate: str = ""
    achievements: List[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    startDate: str = ""
    endDate: str = ""


class ProjectEntry(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    url: str = ""


class CertificationEntry(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""


class TemplateInfo(BaseModel):
    templateId: str = ""
    templateName: str = ""


class CvSchema(BaseModel):
    sessionId: str = ""
    personalInfo: PersonalInfo = Field(default_factory=PersonalInfo)
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    template: TemplateInfo = Field(default_factory=TemplateInfo)
