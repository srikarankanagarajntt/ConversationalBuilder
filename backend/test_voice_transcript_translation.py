"""Verify voice transcript translation is working."""
import asyncio
from app.services.translation_service import TranslationService

async def test_transcript_translation():
    service = TranslationService()
    
    test_cases = [
        ("என் பெயர் ஷ்ரீகரன் நான் ஜாவா டேவலப்பராக ஐந்து வருடம் வேலை செய்கிறேன்", "Tamil", False),  # Should translate
        ("Hello, my name is John. I am a software engineer.", "English", True),  # Should not translate (already English)
    ]
    
    print("Testing voice transcript translation\n")
    print("=" * 80)
    
    for transcript, language, should_stay_same in test_cases:
        print(f"\n{language} Transcript Test:")
        print(f"Original: {transcript[:80]}...")
        
        try:
            # Test language detection
            detected_lang = await service.detect_language_async(transcript)
            print(f"Detected language: {detected_lang}")
            
            # Test translation
            translated = await service.translate_transcript_to_english_async(transcript)
            print(f"Result: {translated[:80]}...")
            
            if should_stay_same:
                status = "✓ PASS" if translated == transcript else "✗ FAIL (should not change)"
            else:
                status = "✓ PASS" if translated != transcript else "✗ FAIL (should translate)"
            
            print(f"Status: {status}")
        except Exception as e:
            print(f"✗ ERROR: {e}")
        
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(test_transcript_translation())
