"""Test file for Technical Skills Service - demonstrates intelligent skill categorization."""
import json
from app.services.technical_skills_service import TechnicalSkillsService


def test_java_backend_developer():
    """Test skill categorization for Java/Backend developer."""
    service = TechnicalSkillsService()
    
    summary = "5 years as java developer with experience in Spring Boot and microservices"
    skills = ["Java", "Spring Framework"]
    
    result = service.categorize_skills(summary, skills)
    
    print("\n" + "="*70)
    print("TEST 1: Java Backend Developer")
    print("="*70)
    print(f"Input Summary: {summary}")
    print(f"Input Skills: {skills}")
    print(f"\nDetected Role: java_backend")
    
    print("\nPrimary Skills:")
    for i, skill in enumerate(result['primary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    print("\nSecondary Skills:")
    for i, skill in enumerate(result['secondary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    # Assertions
    assert len(result['primary']) == 7, "Java backend should have 7 primary skills"
    assert len(result['secondary']) == 7, "Java backend should have 7 secondary skills"
    assert result['primary'][0]['skillName'] == 'Java (Core Java, Java 8/11/17)'
    assert result['primary'][1]['skillName'] == 'Spring Framework (Spring Boot, Spring MVC, Spring Data JPA)'
    print("\n✓ Test passed!")


def test_angular_frontend_developer():
    """Test skill categorization for Angular/Frontend developer."""
    service = TechnicalSkillsService()
    
    summary = "5 years of experience as an Angular developer"
    skills = ["Angular", "TypeScript"]
    
    result = service.categorize_skills(summary, skills)
    
    print("\n" + "="*70)
    print("TEST 2: Angular Frontend Developer")
    print("="*70)
    print(f"Input Summary: {summary}")
    print(f"Input Skills: {skills}")
    print(f"\nDetected Role: angular_frontend")
    
    print("\nPrimary Skills:")
    for i, skill in enumerate(result['primary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    print("\nSecondary Skills:")
    for i, skill in enumerate(result['secondary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    # Assertions
    assert len(result['primary']) == 7, "Angular frontend should have 7 primary skills"
    assert len(result['secondary']) == 7, "Angular frontend should have 7 secondary skills"
    assert result['primary'][0]['skillName'] == 'Angular (v10+ or latest)'
    assert result['primary'][1]['skillName'] == 'TypeScript'
    print("\n✓ Test passed!")


def test_fullstack_developer():
    """Test skill categorization for Full-stack developer."""
    service = TechnicalSkillsService()
    
    summary = "5 years fullstack developer with Java backend and Angular frontend"
    skills = ["Java", "Angular", "DevOps"]
    
    result = service.categorize_skills(summary, skills)
    
    print("\n" + "="*70)
    print("TEST 3: Full-Stack Developer")
    print("="*70)
    print(f"Input Summary: {summary}")
    print(f"Input Skills: {skills}")
    print(f"\nDetected Role: fullstack")
    
    print("\nPrimary Skills:")
    for i, skill in enumerate(result['primary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    print("\nSecondary Skills:")
    for i, skill in enumerate(result['secondary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    # Assertions
    assert len(result['primary']) == 7, "Full-stack should have 7 primary skills"
    assert len(result['secondary']) == 7, "Full-stack should have 7 secondary skills"
    assert result['primary'][0]['skillName'] == 'Java (Spring Boot, Microservices)'
    assert result['primary'][1]['skillName'] == 'Angular (v10+)'
    print("\n✓ Test passed!")


def test_undetected_role_fallback():
    """Test fallback when role cannot be detected."""
    service = TechnicalSkillsService()
    
    summary = "Some experience with development"
    skills = ["Python", "Django", "PostgreSQL"]
    
    result = service.categorize_skills(summary, skills)
    
    print("\n" + "="*70)
    print("TEST 4: Undetected Role (Fallback)")
    print("="*70)
    print(f"Input Summary: {summary}")
    print(f"Input Skills: {skills}")
    print(f"\nDetected Role: None (fallback to user skills categorization)")
    
    print("\nPrimary Skills (first half):")
    for i, skill in enumerate(result['primary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    print("\nSecondary Skills (second half):")
    for i, skill in enumerate(result['secondary'], 1):
        print(f"  {i}. {skill['skillName']} ({skill['proficiency']})")
    
    # Should fall back to simple categorization
    assert len(result['primary']) > 0, "Should have at least one primary skill"
    assert result['primary'][0]['skillName'] == 'Python'
    print("\n✓ Test passed!")


if __name__ == "__main__":
    test_java_backend_developer()
    test_angular_frontend_developer()
    test_fullstack_developer()
    test_undetected_role_fallback()
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED!")
    print("="*70)
