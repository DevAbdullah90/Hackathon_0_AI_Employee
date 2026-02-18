#!/usr/bin/env python3
"""
Gold Tier System Test Script
Tests all modules for proper functionality
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    tests = {
        'audit_logger': False,
        'error_handler': False,
        'social_content_generator': False,
        'ceo_briefing_generator': False,
        'workflow_orchestrator': False
    }

    for module_name in tests:
        try:
            if module_name == 'audit_logger':
                from audit_logger import AuditLogger
            elif module_name == 'error_handler':
                from error_handler import ErrorRecoverySystem
            elif module_name == 'social_content_generator':
                from social_content_generator import SocialContentGenerator
            elif module_name == 'ceo_briefing_generator':
                from ceo_briefing_generator import CEOBriefingGenerator
            elif module_name == 'workflow_orchestrator':
                from workflow_orchestrator import WorkflowOrchestrator

            tests[module_name] = True
            print(f"  ✓ {module_name} - OK")

        except Exception as e:
            tests[module_name] = False
            print(f"  [FAIL] {module_name} - {e}")

    return all(tests.values())

def test_audit_logger():
    """Test audit logger functionality"""
    print("\nTesting AuditLogger...")
    try:
        from audit_logger import AuditLogger
        logger = AuditLogger()
        logger.log_action('test_action', 'test_actor', {'test': 'data'})
        print("  ✓ AuditLogger works")
        return True
    except Exception as e:
        print(f"  ✗ AuditLogger failed: {e}")
        traceback.print_exc()
        return False

def test_social_generator():
    """Test social content generator"""
    print("\nTesting SocialContentGenerator...")
    try:
        from social_content_generator import SocialContentGenerator
        generator = SocialContentGenerator()

        twitter = generator.generate_twitter_post('general')
        assert 'content' in twitter and len(twitter['content']) <= 280

        facebook = generator.generate_facebook_post('general')
        assert 'content' in facebook

        instagram = generator.generate_instagram_post('general')
        assert 'content' in instagram

        print("  ✓ SocialContentGenerator works")
        return True
    except Exception as e:
        print(f"  ✗ SocialContentGenerator failed: {e}")
        traceback.print_exc()
        return False

def test_ceo_briefing():
    """Test CEO briefing generator"""
    print("\nTesting CEOBriefingGenerator...")
    try:
        from ceo_briefing_generator import CEOBriefingGenerator
        generator = CEOBriefingGenerator()
        report = generator.generate_briefing()
        assert len(report) > 0
        print("  ✓ CEOBriefingGenerator works")
        return True
    except Exception as e:
        print(f"  ✗ CEOBriefingGenerator failed: {e}")
        traceback.print_exc()
        return False

def create_test_files():
    """Create test files if they don't exist"""
    print("\nCreating test data...")

    # Create necessary directories
    dirs = ['Reports', 'Audit_Logs', 'Social_Media_Posts', 'Needs_Action']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  [OK] Created {dir_name} directory")

    # Create Company_Handbook if it doesn't exist
    handbook = Path("Company_Handbook.md")
    if not handbook.exists():
        handbook.write_text("""# Company Handbook

#### Company Name: AI Employee Solutions
#### Primary Business Goal: Automate business operations using AI agents

#### Values:
- Innovation
- Efficiency
- Customer Success
- Continuous Improvement
""")
        print("  ✓ Created Company_Handbook.md")

    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("GOLD TIER SYSTEM TEST")
    print("=" * 60)

    # Create test files first
    create_test_files()

    # Run tests
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Audit Logger", test_audit_logger()))
    results.append(("Social Generator", test_social_generator()))
    results.append(("CEO Briefing", test_ceo_briefing()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name:.<40} {status}")

    print("-" * 60)
    print(f"Total: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Gold Tier system is ready.")
        sys.exit(0)
    else:
        print(f"\n[ERROR] {total - passed} test(s) failed. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
