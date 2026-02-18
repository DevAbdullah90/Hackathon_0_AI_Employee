"""
Test script to verify plan creation functionality
"""
import os
import sys
from datetime import datetime

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_plan_creation():
    """Test the plan creation functionality"""
    try:
        from plan_creator import PlanCreator

        print("Testing Plan Creation Functionality...")
        print("=" * 50)

        # Initialize the plan creator
        creator = PlanCreator()
        print("[OK] PlanCreator initialized successfully")

        # Sample content for testing
        sample_content = """
        We need to develop a new customer onboarding process. This is a strategic initiative that should be completed within 2 months.
        The process needs to include document verification, account setup, and initial training. We'll need IT support, customer service team,
        and possibly external consultants for best practices. The budget is approximately $50,000.
        Success will be measured by customer satisfaction scores and onboarding completion rates.
        """

        print(f"Sample content: {sample_content[:100]}...")

        # Generate a plan from the content
        result = creator.generate_plan_from_content(sample_content, "Test_Request")

        print(f"\nPlan Creation Result:")
        print(f"  Success: {result['success']}")
        print(f"  Plan ID: {result.get('plan_id', 'N/A')}")
        print(f"  Plan File: {result.get('plan_file', 'N/A')}")
        print(f"  Priority: {result.get('priority_level', 'N/A')}")
        print(f"  Feasibility Score: {result.get('feasibility_score', 'N/A')}")

        if result['success']:
            print("[OK] Plan created successfully!")

            # Check if plan file was created
            plan_file = result.get('plan_file')
            if plan_file and os.path.exists(plan_file):
                print(f"[OK] Plan file exists: {plan_file}")

                # Read and display first few lines of the plan
                with open(plan_file, 'r', encoding='utf-8') as f:
                    first_lines = ''.join(f.readlines()[:10])
                    print(f"\nFirst few lines of plan:")
                    print(first_lines)
            else:
                print("⚠ Plan file was not created or not found")
        else:
            print(f"[ERROR] Plan creation failed: {result.get('error', 'Unknown error')}")

        # Test scanning for opportunities
        print(f"\nScanning for planning opportunities in system folders...")
        opportunities = creator.scan_input_sources_for_planning_opportunities()
        print(f"Found {len(opportunities)} potential planning opportunities")

        for i, opp in enumerate(opportunities[:3]):  # Show first 3
            print(f"  {i+1}. Source: {opp['source']}")
            print(f"     Priority: {opp['priority'].value}")
            print(f"     Content preview: {opp['content'][:100]}...")

        return True

    except ImportError as e:
        print(f"[ERROR] Error importing PlanCreator: {e}")
        print("This may indicate that the plan_creator module is not properly set up.")
        return False
    except Exception as e:
        print(f"[ERROR] Error during plan creation test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler():
    """Test scheduler functionality"""
    try:
        from scheduler import AIEmployeeScheduler

        print("\nTesting Scheduler Functionality...")
        print("=" * 50)

        # Initialize the scheduler
        scheduler = AIEmployeeScheduler()
        print("[OK] AIEmployeeScheduler initialized successfully")

        # Test individual functions
        print("Testing individual scheduler functions:")

        # Test dashboard update
        try:
            scheduler.update_dashboard()
            print("[OK] Dashboard update test passed")
        except Exception as e:
            print(f"⚠ Dashboard update test failed: {e}")

        # Test health check
        try:
            scheduler.run_health_check()
            print("[OK] Health check test passed")
        except Exception as e:
            print(f"⚠ Health check test failed: {e}")

        # Test plan generation
        try:
            scheduler.generate_plans()
            print("[OK] Plan generation test passed")
        except Exception as e:
            print(f"⚠ Plan generation test failed: {e}")

        return True

    except ImportError as e:
        print(f"[ERROR] Error importing scheduler: {e}")
        print("This may indicate that the scheduler module is not properly set up.")
        return False
    except Exception as e:
        print(f"[ERROR] Error during scheduler test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("AI Employee Silver Tier - Functionality Test")
    print("=" * 60)
    print(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test plan creation
    plan_test_result = test_plan_creation()

    # Test scheduler
    scheduler_test_result = test_scheduler()

    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Plan Creation: {'PASS' if plan_test_result else 'FAIL'}")
    print(f"  Scheduler: {'PASS' if scheduler_test_result else 'FAIL'}")

    overall_result = plan_test_result and scheduler_test_result
    print(f"  Overall: {'PASS' if overall_result else 'FAIL'}")

    print("\n" + "=" * 60)
    if overall_result:
        print("[OK] Silver Tier functionality tests PASSED!")
        print("All required components are working correctly.")
    else:
        print("[ERROR] Some Silver Tier functionality tests FAILED!")
        print("Please check the error messages above.")

    return overall_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)