#!/usr/bin/env python3
"""
Quick verification script to test the language export API endpoint.
"""

import json
from app.models.requests import ExportRequest


def test_export_request_validation():
    """Test that ExportRequest properly validates language parameter."""
    
    print("\n" + "="*70)
    print("EXPORT REQUEST VALIDATION TEST")
    print("="*70 + "\n")
    
    # Test 1: Valid English request
    print("Test 1: Valid English export request")
    try:
        req = ExportRequest(
            sessionId="test-session",
            format="pdf",
            templateId="ntt-classic",
            language="en"
        )
        print(f"✓ Created: {req.model_dump()}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 2: Valid German request
    print("\nTest 2: Valid German export request")
    try:
        req = ExportRequest(
            sessionId="test-session",
            format="docx",
            templateId="ntt-classic",
            language="de"
        )
        print(f"✓ Created: {req.model_dump()}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 3: Default language (should be 'en')
    print("\nTest 3: Default language parameter")
    try:
        req = ExportRequest(
            sessionId="test-session",
            format="pptx",
            templateId="ntt-classic"
        )
        assert req.language == "en", f"Expected 'en', got '{req.language}'"
        print(f"✓ Default language is 'en': {req.language}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 4: Invalid language (should fail validation)
    print("\nTest 4: Invalid language parameter (should be rejected)")
    try:
        req = ExportRequest(
            sessionId="test-session",
            format="pdf",
            templateId="ntt-classic",
            language="invalid"
        )
        print(f"✗ Should have failed validation but got: {req.model_dump()}")
    except Exception as e:
        print(f"✓ Properly rejected invalid language: {str(e)[:100]}")
    
    # Test 5: All format types with German
    print("\nTest 5: All format types with German language")
    formats = ["pdf", "docx", "pptx", "json"]
    for fmt in formats:
        try:
            req = ExportRequest(
                sessionId="test-session",
                format=fmt,
                templateId="ntt-classic",
                language="de"
            )
            print(f"✓ {fmt.upper()}: Valid request")
        except Exception as e:
            print(f"✗ {fmt.upper()}: {e}")
    
    # Test 6: Export request structure
    print("\nTest 6: Export request JSON structure")
    try:
        req = ExportRequest(
            sessionId="user-12345",
            format="pdf",
            templateId="ntt-classic",
            language="de"
        )
        json_data = json.dumps(req.model_dump(), indent=2)
        print("✓ Request structure:")
        print(json_data)
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n" + "="*70)
    print("VALIDATION TEST COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_export_request_validation()
