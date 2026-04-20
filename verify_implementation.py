#!/usr/bin/env python3
"""
Verification Checklist - Technical Skills Enrichment System
Run this script to verify all components are properly installed and working
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_imports():
    """Verify all imports work correctly."""
    print("\n" + "="*70)
    print("CHECKING IMPORTS")
    print("="*70)
    
    try:
        from app.services.technical_skills_service import TechnicalSkillsService
        print("[PASS] TechnicalSkillsService imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import TechnicalSkillsService: {e}")
        return False
    
    try:
        from app.services.conversation_service import ConversationService
        print("[PASS] ConversationService imported successfully (with TechnicalSkillsService)")
    except ImportError as e:
        print(f"[FAIL] Failed to import ConversationService: {e}")
        return False
    
    try:
        from app.services.prompt_service import PromptService
        print("[PASS] PromptService imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import PromptService: {e}")
        return False
    
    return True


def check_service_instantiation():
    """Verify service can be instantiated."""
    print("\n" + "="*70)
    print("CHECKING SERVICE INSTANTIATION")
    print("="*70)
    
    try:
        from app.services.technical_skills_service import TechnicalSkillsService
        service = TechnicalSkillsService()
        print("[PASS] TechnicalSkillsService instantiated successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to instantiate TechnicalSkillsService: {e}")
        return False


def check_role_detection():
    """Verify role detection works."""
    print("\n" + "="*70)
    print("CHECKING ROLE DETECTION")
    print("="*70)
    
    from app.services.technical_skills_service import TechnicalSkillsService
    service = TechnicalSkillsService()
    
    test_cases = [
        ("5 years java developer", ["java", "spring framework"], "java_backend"),
        ("5 years angular developer", ["angular", "typescript"], "angular_frontend"),
        ("5 years fullstack developer", ["java", "angular", "devops"], "fullstack"),
    ]
    
    all_passed = True
    for summary, skills, expected in test_cases:
        detected = service._detect_role(summary, skills)
        if detected == expected:
            print(f"[PASS] Detected '{expected}' from summary: '{summary}'")
        else:
            print(f"[FAIL] Expected '{expected}' but got '{detected}' for summary: '{summary}'")
            all_passed = False
    
    return all_passed


def check_skill_categorization():
    """Verify skill categorization works."""
    print("\n" + "="*70)
    print("CHECKING SKILL CATEGORIZATION")
    print("="*70)
    
    from app.services.technical_skills_service import TechnicalSkillsService
    service = TechnicalSkillsService()
    
    test_cases = [
        ("java developer", ["java", "spring"], 7, 7, "java_backend"),
        ("angular developer", ["angular", "typescript"], 7, 7, "angular_frontend"),
        ("fullstack", ["java", "angular"], 7, 7, "fullstack"),
    ]
    
    all_passed = True
    for summary, skills, exp_primary, exp_secondary, role in test_cases:
        result = service.categorize_skills(summary, skills)
        primary_count = len(result['primary'])
        secondary_count = len(result['secondary'])
        
        if primary_count == exp_primary and secondary_count == exp_secondary:
            print(f"[PASS] {role}: {primary_count} primary + {secondary_count} secondary skills")
        else:
            print(f"[FAIL] {role}: Expected {exp_primary}+{exp_secondary}, got {primary_count}+{secondary_count}")
            all_passed = False
    
    return all_passed


def check_skill_structure():
    """Verify skills have correct structure."""
    print("\n" + "="*70)
    print("CHECKING SKILL STRUCTURE")
    print("="*70)
    
    from app.services.technical_skills_service import TechnicalSkillsService
    service = TechnicalSkillsService()
    
    result = service.categorize_skills("java developer", ["java", "spring"])
    
    if not result['primary']:
        print("[FAIL] No primary skills found")
        return False
    
    skill = result['primary'][0]
    required_fields = ['skillName', 'proficiency']
    
    if all(field in skill for field in required_fields):
        print(f"[PASS] Skill structure correct: {skill}")
    else:
        print(f"[FAIL] Skill structure incomplete: {skill}")
        return False
    
    return True


def check_files_exist():
    """Verify all required files exist."""
    print("\n" + "="*70)
    print("CHECKING FILE EXISTENCE")
    print("="*70)
    
    required_files = [
        "backend/app/services/technical_skills_service.py",
        "backend/tests/test_technical_skills_service.py",
        "backend/TECHNICAL_SKILLS_ENRICHMENT.md",
        "SYSTEM_PROMPTS_UPDATE_SUMMARY.md",
        "SKILLS_MAPPING_QUICK_REFERENCE.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"[PASS] {file_path}")
        else:
            print(f"[FAIL] {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_prompt_update():
    """Verify system prompt has been updated."""
    print("\n" + "="*70)
    print("CHECKING SYSTEM PROMPT UPDATE")
    print("="*70)
    
    try:
        from app.services.prompt_service import SYSTEM_PROMPT
        if "TECHNICAL SKILLS CATEGORIZATION" in SYSTEM_PROMPT:
            print("[PASS] System prompt updated with TECHNICAL SKILLS CATEGORIZATION section")
            return True
        else:
            print("[FAIL] System prompt not updated with skill categorization guidance")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking system prompt: {e}")
        return False


def run_all_checks():
    """Run all verification checks."""
    print("\n")
    print("*" * 70)
    print("TECHNICAL SKILLS ENRICHMENT SYSTEM - VERIFICATION CHECKLIST")
    print("*" * 70)
    
    checks = [
        ("Imports", check_imports),
        ("Service Instantiation", check_service_instantiation),
        ("Role Detection", check_role_detection),
        ("Skill Categorization", check_skill_categorization),
        ("Skill Structure", check_skill_structure),
        ("Files Exist", check_files_exist),
        ("Prompt Update", check_prompt_update),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n[ERROR] {check_name} check failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {check_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "*" * 70)
        print("ALL CHECKS PASSED - SYSTEM IS READY!")
        print("*" * 70)
        return 0
    else:
        print("\n" + "*" * 70)
        print("SOME CHECKS FAILED - PLEASE REVIEW ABOVE")
        print("*" * 70)
        return 1


if __name__ == "__main__":
    exit_code = run_all_checks()
    sys.exit(exit_code)
