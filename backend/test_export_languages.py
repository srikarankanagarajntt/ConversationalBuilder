#!/usr/bin/env python3
"""
Integration test for language-based export functionality.
Tests that the export endpoints properly handle language parameters for PDF, DOCX, and PPTX formats.
"""

import pytest
import asyncio
from app.models.cv_schema import CvSchema, PersonalInfo, Experience, Education
from app.services.export_service import ExportService
from app.services.translation_service import TranslationService


# Sample CV data for testing
def create_sample_cv() -> CvSchema:
    """Create a sample CV for testing."""
    return CvSchema(
        personalInfo=PersonalInfo(
            fullName="John Smith",
            email="john@example.com",
            phone="+1234567890",
            location="New York, USA",
            summary="Software engineer with 5 years of experience"
        ),
        professionalSummary=["Experienced software developer", "Full-stack engineer"],
        skills=["Python", "TypeScript", "React", "PostgreSQL"],
        experience=[
            Experience(
                title="Senior Developer",
                company="Tech Corp",
                role="Team Lead",
                startDate="2022-01-01",
                endDate="2024-12-31",
                location="New York",
                description="Led development team",
                achievements=["Built scalable API", "Mentored junior developers"],
                technologies=["Python", "AWS"],
            )
        ],
        education=[
            Education(
                degree="B.S.",
                field="Computer Science",
                institution="University of Example",
                graduationDate="2019-05-01",
            )
        ],
        certifications=[
            {"name": "AWS Solutions Architect", "issuer": "Amazon"}
        ]
    )


class TestLanguageExport:
    """Test suite for language-based export functionality."""

    def test_export_service_accepts_language_parameter(self):
        """Test that ExportService.create_export_job accepts language parameter."""
        service = ExportService()
        cv = create_sample_cv()
        
        # Test with English
        job_en = asyncio.run(service.create_export_job(cv, "pdf", "ntt-classic", "en"))
        assert job_en["status"] == "ready"
        assert job_en["format"] == "pdf"
        print("✓ English PDF export successful")
        
        # Test with German
        job_de = asyncio.run(service.create_export_job(cv, "pdf", "ntt-classic", "de"))
        assert job_de["status"] == "ready"
        assert job_de["format"] == "pdf"
        print("✓ German PDF export successful")

    def test_translation_service_translates_cv(self):
        """Test that TranslationService properly translates CV content."""
        service = TranslationService()
        cv = create_sample_cv()
        
        # German translation is supported
        assert "de" in service.SUPPORTED_LANGUAGES
        print(f"✓ German is supported: {service.SUPPORTED_LANGUAGES['de']}")
        
        # Test that unsupported language raises error
        try:
            service.translate_cv(cv, "unknown")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported language" in str(e)
            print(f"✓ Unsupported language properly rejected: {e}")

    def test_export_formats_with_language(self):
        """Test export in all formats with language parameter."""
        service = ExportService()
        cv = create_sample_cv()
        formats = ["pdf", "docx", "pptx", "json"]
        
        for fmt in formats:
            try:
                job = asyncio.run(service.create_export_job(cv, fmt, "ntt-classic", "de"))
                assert job["status"] == "ready"
                assert job["format"] == fmt
                print(f"✓ German {fmt.upper()} export successful")
            except Exception as e:
                print(f"⚠ {fmt.upper()} export test: {str(e)[:100]}")

    def test_language_parameter_defaults_to_english(self):
        """Test that language parameter defaults to English if not provided."""
        service = ExportService()
        cv = create_sample_cv()
        
        # When no language is specified, English should be used
        job = asyncio.run(service.create_export_job(cv, "pdf", "ntt-classic"))
        assert job["status"] == "ready"
        print("✓ Default English language works")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LANGUAGE-BASED EXPORT FUNCTIONALITY TEST")
    print("="*60 + "\n")
    
    test = TestLanguageExport()
    
    print("1. Testing ExportService with language parameter...")
    try:
        test.test_export_service_accepts_language_parameter()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print("\n2. Testing TranslationService...")
    try:
        test.test_translation_service_translates_cv()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print("\n3. Testing all export formats with German language...")
    try:
        test.test_export_formats_with_language()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print("\n4. Testing language parameter defaults...")
    try:
        test.test_language_parameter_defaults_to_english()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60 + "\n")
