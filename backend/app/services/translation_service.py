"""Translation service — translates CV content to different languages using LLM."""
from __future__ import annotations

import asyncio
import threading
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
        Translate entire CV content to target language in one batch.

        Args:
            cv: CV schema to translate
            target_language: Language code (e.g., 'en', 'de')
            
        Returns:
            Translated CV schema (schema structure unchanged, only values translated)
        """
        if target_language == "en":
            # No translation needed for English
            return cv
        
        if target_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {target_language}. Supported: {list(self.SUPPORTED_LANGUAGES.keys())}")
        
        # Create a copy to avoid modifying original
        translated_cv = CvSchema.model_validate(cv.model_dump())
        
        # Extract all text values with their paths
        text_map = self._extract_cv_text_values(cv)

        # If no text to translate, return original
        if not text_map:
            return translated_cv

        # Translate all text values in one batch
        translated_texts = self._translate_batch_sync(text_map, target_language)

        # Map translated values back to CV schema
        self._apply_translated_values(translated_cv, translated_texts, text_map)

        return translated_cv

    def _extract_cv_text_values(self, cv: CvSchema) -> Dict[str, str]:
        """
        Extract all text values from CV schema with their paths.

        Returns:
            Dict mapping unique keys to text values
        """
        text_map = {}
        key_counter = 0

        # Personal info
        if cv.personalInfo:
            if cv.personalInfo.summary and cv.personalInfo.summary.strip():
                key = f"personalInfo_summary"
                text_map[key] = cv.personalInfo.summary

        # Professional Summary
        if cv.professionalSummary:
            for idx, summary_item in enumerate(cv.professionalSummary):
                if summary_item and summary_item.strip():
                    key = f"professionalSummary_{idx}"
                    text_map[key] = summary_item

        # Skills
        if cv.skills:
            for idx, skill in enumerate(cv.skills):
                if skill and skill.strip():
                    key = f"skills_{idx}"
                    text_map[key] = skill

        # Experience
        if cv.experience:
            for exp_idx, exp in enumerate(cv.experience):
                if exp.title and exp.title.strip():
                    text_map[f"experience_{exp_idx}_title"] = exp.title
                if exp.company and exp.company.strip():
                    text_map[f"experience_{exp_idx}_company"] = exp.company
                if exp.achievements:
                    for ach_idx, ach in enumerate(exp.achievements):
                        if ach and ach.strip():
                            text_map[f"experience_{exp_idx}_achievements_{ach_idx}"] = ach

        # Education
        if cv.education:
            for edu_idx, edu in enumerate(cv.education):
                if edu.degree and edu.degree.strip():
                    text_map[f"education_{edu_idx}_degree"] = edu.degree
                if edu.field and edu.field.strip():
                    text_map[f"education_{edu_idx}_field"] = edu.field
                if edu.institution and edu.institution.strip():
                    text_map[f"education_{edu_idx}_institution"] = edu.institution

        # Projects
        if cv.projects:
            for proj_idx, proj in enumerate(cv.projects):
                if proj.name and proj.name.strip():
                    text_map[f"projects_{proj_idx}_name"] = proj.name
                if proj.description and proj.description.strip():
                    text_map[f"projects_{proj_idx}_description"] = proj.description
                if proj.technologies:
                    for tech_idx, tech in enumerate(proj.technologies):
                        if tech and tech.strip():
                            text_map[f"projects_{proj_idx}_technologies_{tech_idx}"] = tech

        # Certifications
        if cv.certifications:
            for cert_idx, cert in enumerate(cv.certifications):
                if cert.name and cert.name.strip():
                    text_map[f"certifications_{cert_idx}_name"] = cert.name
                if cert.issuer and cert.issuer.strip():
                    text_map[f"certifications_{cert_idx}_issuer"] = cert.issuer

        return text_map

    def _translate_batch_sync(self, text_map: Dict[str, str], target_language: str) -> Dict[str, str]:
        """
        Translate all text values in a single batch operation.

        Args:
            text_map: Dict mapping keys to text values
            target_language: Target language code

        Returns:
            Dict mapping same keys to translated values
        """
        if not text_map:
            return {}

        try:
            # Create a formatted list of all texts to translate
            texts_to_translate = "\n".join([f"{i+1}. {text}" for i, text in enumerate(text_map.values())])

            # Translate in one LLM call
            try:
                asyncio.get_running_loop()
                translated_text = self._run_coroutine_in_thread(
                    self._translate_batch_async(texts_to_translate, target_language)
                )
            except RuntimeError:
                translated_text = asyncio.run(
                    self._translate_batch_async(texts_to_translate, target_language)
                )

            # Parse translated text back to original structure
            translated_lines = translated_text.strip().split("\n")
            translated_values = {}

            keys = list(text_map.keys())
            for i, key in enumerate(keys):
                if i < len(translated_lines):
                    # Extract text after number prefix (e.g., "1. translated text")
                    line = translated_lines[i].strip()
                    # Remove number prefix if present
                    if line and line[0].isdigit() and "." in line[:3]:
                        translated_values[key] = line[line.index(".") + 1:].strip()
                    else:
                        translated_values[key] = line
                else:
                    # Fallback to original if parsing fails
                    translated_values[key] = text_map[key]

            return translated_values
        except Exception as e:
            print(f"Batch translation error: {e}")
            # Return original texts on error
            return text_map

    async def _translate_batch_async(self, batch_text: str, target_language: str) -> str:
        """
        Async method to translate all texts in a batch in one LLM call.

        Args:
            batch_text: Numbered list of all texts to translate
            target_language: Target language code

        Returns:
            Translated batch text with same numbering
        """
        target_lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)

        try:
            response = await self.llm.chat([
                {
                    "role": "system",
                    "content": f"You are a professional translator. You will receive a numbered list of texts in English. "
                              f"Translate each text to {target_lang_name}. "
                              f"Return the translations as a numbered list with the same numbering format. "
                              f"Keep the exact same numbering (1., 2., 3., etc.). "
                              f"Return ONLY the numbered list, nothing else. "
                              f"Maintain professional tone and accuracy. "
                              f"Do not add any explanations or additional text."
                },
                {
                    "role": "user",
                    "content": batch_text
                }
            ])

            translated = str(response).strip()

            # Ensure proper UTF-8 encoding
            try:
                translated.encode('utf-8')
            except UnicodeEncodeError as e:
                print(f"Encoding error in batch translation: {e}, returning original")
                return batch_text

            return translated
        except Exception as e:
            print(f"Batch translation error: {e}")
            return batch_text

    def _apply_translated_values(self, translated_cv: CvSchema, translated_texts: Dict[str, str], text_map: Dict[str, str]) -> None:
        """
        Apply translated values back to CV schema while preserving structure.

        Args:
            translated_cv: CV schema to update (modified in place)
            translated_texts: Dict mapping keys to translated values
            text_map: Original text map (for keys)
        """
        for key, translated_value in translated_texts.items():
            self._set_value_by_key(translated_cv, key, translated_value)

    def _set_value_by_key(self, cv: CvSchema, key: str, value: str) -> None:
        """
        Set a value in CV schema using a dotted key path.

        Args:
            cv: CV schema to modify
            key: Key path (e.g., 'experience_0_title')
            value: Value to set
        """
        parts = key.split("_")

        if parts[0] == "personalInfo":
            if cv.personalInfo and len(parts) > 1:
                if parts[1] == "summary":
                    cv.personalInfo.summary = value

        elif parts[0] == "professionalSummary":
            if cv.professionalSummary and len(parts) > 1:
                idx = int(parts[1])
                if idx < len(cv.professionalSummary):
                    cv.professionalSummary[idx] = value

        elif parts[0] == "skills":
            if cv.skills and len(parts) > 1:
                idx = int(parts[1])
                if idx < len(cv.skills):
                    cv.skills[idx] = value

        elif parts[0] == "experience":
            if cv.experience and len(parts) > 2:
                exp_idx = int(parts[1])
                if exp_idx < len(cv.experience):
                    exp = cv.experience[exp_idx]
                    if parts[2] == "title":
                        exp.title = value
                    elif parts[2] == "company":
                        exp.company = value
                    elif parts[2] == "achievements" and len(parts) > 3:
                        ach_idx = int(parts[3])
                        if exp.achievements and ach_idx < len(exp.achievements):
                            exp.achievements[ach_idx] = value

        elif parts[0] == "education":
            if cv.education and len(parts) > 2:
                edu_idx = int(parts[1])
                if edu_idx < len(cv.education):
                    edu = cv.education[edu_idx]
                    if parts[2] == "degree":
                        edu.degree = value
                    elif parts[2] == "field":
                        edu.field = value
                    elif parts[2] == "institution":
                        edu.institution = value

        elif parts[0] == "projects":
            if cv.projects and len(parts) > 2:
                proj_idx = int(parts[1])
                if proj_idx < len(cv.projects):
                    proj = cv.projects[proj_idx]
                    if parts[2] == "name":
                        proj.name = value
                    elif parts[2] == "description":
                        proj.description = value
                    elif parts[2] == "technologies" and len(parts) > 3:
                        tech_idx = int(parts[3])
                        if proj.technologies and tech_idx < len(proj.technologies):
                            proj.technologies[tech_idx] = value

        elif parts[0] == "certifications":
            if cv.certifications and len(parts) > 2:
                cert_idx = int(parts[1])
                if cert_idx < len(cv.certifications):
                    cert = cv.certifications[cert_idx]
                    if parts[2] == "name":
                        cert.name = value
                    elif parts[2] == "issuer":
                        cert.issuer = value

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
            # Check if there's already a running event loop
            try:
                asyncio.get_running_loop()
                # If we get here, there's a running loop - run in thread
                return self._run_coroutine_in_thread(self._translate_text_async(text, target_language, source_language))
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                return asyncio.run(self._translate_text_async(text, target_language, source_language))
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def _run_coroutine_in_thread(self, coroutine):
        """Run an async coroutine in a separate thread to avoid event loop conflicts."""
        result: Dict[str, Any] = {}
        error: Dict[str, Exception] = {}

        def _runner():
            try:
                result["value"] = asyncio.run(coroutine)
            except Exception as exc:
                error["value"] = exc

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        thread.join()

        if "value" in error:
            raise error["value"]
        return result.get("value", "")

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
