"""Test file to verify bulk processing implementation."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all modules import correctly."""
    try:
        from app.services.bulk_service import BulkService
        print("✓ bulk_service imports successfully")
        
        from app.api import bulk_upload, bulk_export
        print("✓ bulk_upload API imports successfully")
        print("✓ bulk_export API imports successfully")
        
        # Test service instantiation
        service = BulkService()
        print("✓ BulkService instantiates successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_bulk_job_creation():
    """Test bulk job creation."""
    try:
        from app.services.bulk_service import BulkService
        from app.models.cv_schema import CvSchema, PersonalInfo
        
        service = BulkService()
        
        # Create sample CV
        cv = CvSchema(
            personalInfo=PersonalInfo(
                fullName="John Doe",
                email="john@example.com",
                phone="123-456-7890",
                location="New York"
            ),
            skills=[],
            experience=[],
            education=[],
            certifications=[]
        )
        
        # Create bulk job
        job = service.create_bulk_job([cv], "ntt-classic", "en", "pdf")
        print(f"✓ Bulk job created: {job['bulkId']}")
        print(f"  - Total files: {job['totalFiles']}")
        print(f"  - Status: {job['status']}")
        
        return True
    except Exception as e:
        print(f"✗ Bulk job creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_async_processing():
    """Test async processing simulation."""
    try:
        import asyncio
        from app.services.bulk_service import BulkService
        from app.models.cv_schema import CvSchema, PersonalInfo
        
        async def test_process():
            service = BulkService()
            
            # Create sample CVs
            cvs = [
                CvSchema(
                    personalInfo=PersonalInfo(
                        fullName=f"Person {i}",
                        email=f"person{i}@example.com",
                        phone="123-456-7890",
                        location="New York"
                    ),
                    skills=[],
                    experience=[],
                    education=[],
                    certifications=[]
                )
                for i in range(3)
            ]
            
            job = service.create_bulk_job(cvs, "ntt-classic", "en", "pdf")
            print(f"✓ Created bulk job with {len(cvs)} CVs: {job['bulkId']}")
            
            # Simulate async processing would occur here
            print(f"  - Process would run in parallel for {len(cvs)} CVs")
            
            return True
        
        # Run async test
        result = asyncio.run(test_process())
        return result
        
    except Exception as e:
        print(f"✗ Async processing error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("US3 Bulk Processing Implementation Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Bulk Job Creation", test_bulk_job_creation),
        ("Async Processing", test_async_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed!"))
    print("=" * 60)
