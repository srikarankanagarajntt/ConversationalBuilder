"""Test language detection and translation for voice transcripts."""
import asyncio
from app.services.translation_service import TranslationService

async def test_translation():
    service = TranslationService()
    
    test_cases = [
        ("Hello, my name is John", "English - should not translate"),
        ("வணக்கம் எனது பெயர் சரிதா", "Tamil - should translate to English"),
        ("Hola, mi nombre es Carlos", "Spanish - should translate to English"),
    ]
    
    print("Testing language detection and translation for voice transcripts\n")
    
    for text, description in test_cases:
        print(f"Test: {description}")
        print(f"Original: {text}")
        
        # Test language detection
        detected_lang = service.detect_language(text)
        print(f"Detected language: {detected_lang}")
        
        # Test translation
        try:
            translated = service.translate_transcript_to_english(text)
            print(f"Translated: {translated}")
        except Exception as e:
            print(f"Translation error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_translation())
