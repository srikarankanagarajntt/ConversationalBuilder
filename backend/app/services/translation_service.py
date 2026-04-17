"""Translation service — translates CV content to different languages using LLM."""
from __future__ import annotations

from typing import Any, Dict, Optional
from app.models.cv_schema import CvSchema
from app.services.llm_service import LLMService


class TranslationService:
    """Service for translating CV content to different languages."""
    
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "de": "German",
    }
    
    def __init__(self):
        self.llm = LLMService()
    
    def translate_cv(self, cv: CvSchema, target_language: str = "en") -> CvSchema:
        """
        Translate CV content to target language.
        
        Args:
            cv: CV schema to translate
            target_language: Language code (e.g., 'en', 'de')
            
        Returns:
            Translated CV schema
        """
        if target_language == "en":
            # No translation needed for English
            return cv
        
        if target_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {target_language}. Supported: {list(self.SUPPORTED_LANGUAGES.keys())}")
        
        # Create a copy to avoid modifying original
        translated_cv = CvSchema.model_validate(cv.model_dump())
        
        # Translate personal info
        if cv.personalInfo:
            translated_cv.personalInfo.summary = self._translate_text(
                cv.personalInfo.summary,
                target_language
            )
        
        # Translate skills
        if cv.skills:
            translated_cv.skills = [
                self._translate_text(skill, target_language)
                for skill in cv.skills
            ]
        
        # Translate experience
        if cv.experience:
            for exp in translated_cv.experience:
                exp.title = self._translate_text(exp.title, target_language)
                exp.company = self._translate_text(exp.company, target_language)
                exp.achievements = [
                    self._translate_text(ach, target_language)
                    for ach in (exp.achievements or [])
                ]
        
        # Translate education
        if cv.education:
            for edu in translated_cv.education:
                edu.degree = self._translate_text(edu.degree, target_language)
                edu.field = self._translate_text(edu.field, target_language)
                edu.institution = self._translate_text(edu.institution, target_language)
        
        # Translate projects
        if cv.projects:
            for proj in translated_cv.projects:
                proj.name = self._translate_text(proj.name, target_language)
                proj.description = self._translate_text(proj.description, target_language)
                proj.technologies = [
                    self._translate_text(tech, target_language)
                    for tech in (proj.technologies or [])
                ]
        
        # Translate certifications
        if cv.certifications:
            for cert in translated_cv.certifications:
                cert.name = self._translate_text(cert.name, target_language)
                cert.issuer = self._translate_text(cert.issuer, target_language)
        
        return translated_cv
    
    def _translate_text(self, text: str, target_language: str) -> str:
        """
        Translate a single text string using LLM.
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        target_lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        try:
            response = self.llm.chat([
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text to {target_lang_name}. "
                              "Maintain professional tone and formatting. Return only the translated text, nothing else. "
                              "Avoid any markdown formatting or special characters except standard punctuation."
                },
                {
                    "role": "user",
                    "content": text
                }
            ])
            
            # Ensure proper UTF-8 encoding and sanitize
            translated = str(response).strip()
            
            # Ensure the string is properly encoded for DOCX
            try:
                # This will help catch encoding issues early
                translated.encode('utf-8')
            except UnicodeEncodeError as e:
                print(f"Encoding error in translation: {e}, returning original text")
                return text
            
            return translated
        except Exception as e:
            # If translation fails, return original text
            print(f"Translation error: {e}")
            return text
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.SUPPORTED_LANGUAGES.copy()
