"""Translation service — translates CV content to different languages using LLM."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional
from app.models.cv_schema import CvSchema
from app.services.llm_service import LLMService


class TranslationService:
    """Service for translating CV content to different languages."""
    
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "de": "German",
        "fr": "French",
        "es": "Spanish",
        "ta": "Tamil",
        "te": "Telugu",
        "hi": "Hindi",
        "kn": "Kannada",
        "ml": "Malayalam",
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
            translated_cv.personalInfo.summary = self._translate_text_sync(
                cv.personalInfo.summary,
                target_language
            )
        
        # Translate skills
        if cv.skills:
            translated_cv.skills = [
                self._translate_text_sync(skill, target_language)
                for skill in cv.skills
            ]
        
        # Translate experience
        if cv.experience:
            for exp in translated_cv.experience:
                exp.title = self._translate_text_sync(exp.title, target_language)
                exp.company = self._translate_text_sync(exp.company, target_language)
                exp.achievements = [
                    self._translate_text_sync(ach, target_language)
                    for ach in (exp.achievements or [])
                ]
        
        # Translate education
        if cv.education:
            for edu in translated_cv.education:
                edu.degree = self._translate_text_sync(edu.degree, target_language)
                edu.field = self._translate_text_sync(edu.field, target_language)
                edu.institution = self._translate_text_sync(edu.institution, target_language)
        
        # Translate projects
        if cv.projects:
            for proj in translated_cv.projects:
                proj.name = self._translate_text_sync(proj.name, target_language)
                proj.description = self._translate_text_sync(proj.description, target_language)
                proj.technologies = [
                    self._translate_text_sync(tech, target_language)
                    for tech in (proj.technologies or [])
                ]
        
        # Translate certifications
        if cv.certifications:
            for cert in translated_cv.certifications:
                cert.name = self._translate_text_sync(cert.name, target_language)
                cert.issuer = self._translate_text_sync(cert.issuer, target_language)
        
        return translated_cv
    
    def _translate_text_sync(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """
        Synchronous wrapper for text translation (used for CV content).
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Optional source language code (if known)
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        try:
            # Run async translation in event loop
            return asyncio.run(self._translate_text_async(text, target_language, source_language))
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    async def _translate_text_async(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """
        Async translation method (used for voice transcripts).
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Optional source language code (if known)
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        target_lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        source_lang_info = ""
        if source_language:
            source_lang_name = self.SUPPORTED_LANGUAGES.get(source_language, source_language)
            source_lang_info = f" from {source_lang_name}"
        
        try:
            response = await self.llm.chat([
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text to {target_lang_name}{source_lang_info}. "
                              "Maintain professional tone and formatting. Return only the translated text, nothing else. "
                              "Avoid any markdown formatting or special characters except standard punctuation. "
                              "For transcripts, ensure the meaning and accuracy are preserved."
                },
                {
                    "role": "user",
                    "content": text
                }
            ])
            
            # Ensure proper UTF-8 encoding and sanitize
            translated = str(response).strip()
            
            # Ensure the string is properly encoded
            try:
                translated.encode('utf-8')
            except UnicodeEncodeError as e:
                print(f"Encoding error in translation: {e}, returning original text")
                return text
            
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    async def detect_language_async(self, text: str) -> str:
        """
        Async language detection.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code (e.g., 'en', 'ta', 'hi')
        """
        if not text or not text.strip():
            return "en"
        
        try:
            response = await self.llm.chat([
                {
                    "role": "system",
                    "content": "You are a language detection expert. Detect the language of the given text and respond with ONLY the two-letter language code (e.g., 'en' for English, 'ta' for Tamil, 'hi' for Hindi, 'fr' for French, 'es' for Spanish, 'de' for German, 'te' for Telugu, 'kn' for Kannada, 'ml' for Malayalam). Respond with only the code, nothing else."
                },
                {
                    "role": "user",
                    "content": text
                }
            ])
            
            detected_lang = str(response).strip().lower()
            
            # Validate it's a known language code
            if detected_lang in self.SUPPORTED_LANGUAGES:
                return detected_lang
            
            # Return 'en' as default if detection fails
            print(f"Language detection returned unknown code: {detected_lang}, defaulting to 'en'")
            return "en"
        except Exception as e:
            print(f"Language detection error: {e}")
            return "en"
    
    async def translate_transcript_to_english_async(self, text: str) -> str:
        """
        Async translate transcript to English if it's in a different language.
        
        Args:
            text: Transcript to translate
            
        Returns:
            English translation of the transcript
        """
        if not text or not text.strip():
            return text
        
        try:
            print(f"Detecting language for transcript: {text[:100]}...")
            
            # Detect the language of the transcript
            detected_lang = await self.detect_language_async(text)
            print(f"Detected language: {detected_lang}")
            
            # If already in English, return as-is
            if detected_lang == "en":
                print("Transcript is already in English, no translation needed")
                return text
            
            # Translate to English
            print(f"Translating from {detected_lang} to English...")
            translated = await self._translate_text_async(text, "en", source_language=detected_lang)
            print(f"Translation complete. Result: {translated[:100]}...")
            
            return translated
        except Exception as e:
            print(f"Transcript translation error: {e}")
            return text
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.SUPPORTED_LANGUAGES.copy()
