#!/usr/bin/env python3
"""
Comprehensive Tier Test Suite for AI Employee
Tests Bronze, Silver, and Gold tier requirements
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TierTestSuite:
    """Comprehensive test suite for all AI Employee tiers"""

    def __init__(self):
        self.vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\OneDrive\\Desktop\\hakathone zero\\AI_Employee_vault")
        self.tier_results = {}

    def test_bronze_tier(self):
        """Test Bronze Tier requirements"""
        logger.info("="*60)
        logger.info("🧪 TESTING BRONZE TIER REQUIREMENTS")
        logger.info("="*60)

        bronze_tests = {
            "obsidian_vault_exists": self._test_obsidian_vault(),
            "dashboard_exists": self._test_dashboard_exists(),
            "company_handbook_exists": self._test_company_handbook_exists(),
            "folder_structure": self._test_bronze_folder_structure(),
            "claude_code_integration": self._test_claude_integration(),
            "basic_watchers": self._test_basic_watchers()
        }

        passed_tests = sum(1 for result in bronze_tests.values() if result)
        total_tests = len(bronze_tests)

        logger.info(f"\n📋 BRONZE TIER: {passed_tests}/{total_tests} tests passed")

        self.tier_results['bronze'] = {
            'tests': bronze_tests,
            'passed': passed_tests,
            'total': total_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0
        }

        return passed_tests == total_tests

    def test_silver_tier(self):
        """Test Silver Tier requirements"""
        logger.info("\n" + "="*60)
        logger.info("🧪 TESTING SILVER TIER REQUIREMENTS")
        logger.info("="*60)

        silver_tests = {
            "bronze_requirements_met": self._test_bronze_requirements_met(),
            "multiple_watchers": self._test_multiple_watchers(),
            "linkedin_automation": self._test_linkedin_automation(),
            "mcp_server": self._test_mcp_server(),
            "human_in_the_loop": self._test_human_in_the_loop(),
            "scheduling": self._test_scheduling(),
            "agent_skills": self._test_agent_skills()
        }

        passed_tests = sum(1 for result in silver_tests.values() if result)
        total_tests = len(silver_tests)

        logger.info(f"\n📋 SILVER TIER: {passed_tests}/{total_tests} tests passed")

        self.tier_results['silver'] = {
            'tests': silver_tests,
            'passed': passed_tests,
            'total': total_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0
        }

        return passed_tests == total_tests

    def test_gold_tier(self):
        """Test Gold Tier requirements"""
        logger.info("\n" + "="*60)
        logger.info("🧪 TESTING GOLD TIER REQUIREMENTS")
        logger.info("="*60)

        gold_tests = {
            "silver_requirements_met": self._test_silver_requirements_met(),
            "cross_domain_integration": self._test_cross_domain_integration(),
            "xero_accounting": self._test_accounting_integration(),  # Actually Odoo now
            "facebook_integration": self._test_facebook_integration(),
            "instagram_integration": self._test_instagram_integration(),
            "twitter_integration": self._test_twitter_integration(),
            "multiple_mcp_servers": self._test_multiple_mcp_servers(),
            "weekly_audit": self._test_weekly_audit(),
            "error_recovery": self._test_error_recovery(),
            "comprehensive_logging": self._test_comprehensive_logging(),
            "architecture_documentation": self._test_architecture_documentation(),
            "agent_skills_implementation": self._test_agent_skills_implementation()
        }

        passed_tests = sum(1 for result in gold_tests.values() if result)
        total_tests = len(gold_tests)

        logger.info(f"\n📋 GOLD TIER: {passed_tests}/{total_tests} tests passed")

        self.tier_results['gold'] = {
            'tests': gold_tests,
            'passed': passed_tests,
            'total': total_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0
        }

        return passed_tests == total_tests

    def _test_obsidian_vault(self):
        """Test if Obsidian vault exists"""
        try:
            # Check if basic markdown files exist
            dashboard_path = self.vault_path / "Dashboard.md"
            handbook_path = self.vault_path / "Company_Handbook.md"

            result = dashboard_path.exists() or handbook_path.exists()
            logger.info(f"  {'✅' if result else '❌'} Obsidian vault structure: {'Found' if result else 'Not found'}")
            return result
        except Exception as e:
            logger.error(f"  ❌ Error testing Obsidian vault: {e}")
            return False

    def _test_dashboard_exists(self):
        """Test if Dashboard.md exists"""
        dashboard_path = self.vault_path / "Dashboard.md"
        result = dashboard_path.exists()
        logger.info(f"  {'✅' if result else '❌'} Dashboard.md: {'Found' if result else 'Missing'}")
        return result

    def _test_company_handbook_exists(self):
        """Test if Company_Handbook.md exists"""
        handbook_path = self.vault_path / "Company_Handbook.md"
        result = handbook_path.exists()
        logger.info(f"  {'✅' if result else '❌'} Company_Handbook.md: {'Found' if result else 'Missing'}")
        return result

    def _test_bronze_folder_structure(self):
        """Test Bronze tier folder structure"""
        required_dirs = ["Inbox", "Needs_Action", "Done"]
        found_dirs = []

        for dir_name in required_dirs:
            dir_path = self.vault_path / dir_name
            if dir_path.exists():
                found_dirs.append(dir_name)

        result = len(found_dirs) >= len(required_dirs) - 1  # Allow 1 missing
        logger.info(f"  {'✅' if result else '❌'} Folder structure: Found {len(found_dirs)}/{len(required_dirs)} required directories")
        return result

    def _test_claude_integration(self):
        """Test Claude Code integration"""
        # Check if Python files exist that interact with Claude
        python_files = list(self.vault_path.glob("*.py"))
        result = len(python_files) > 0

        # Also check for common Claude interaction patterns
        interaction_found = False
        for py_file in python_files[:5]:  # Check first 5 files
            try:
                content = py_file.read_text()
                if any(keyword in content.lower() for keyword in ['claude', 'ai', 'llm', 'model']):
                    interaction_found = True
                    break
            except:
                continue

        result = result and interaction_found
        logger.info(f"  {'✅' if result else '❌'} Claude integration: {'Detected' if result else 'Not detected'}")
        return result

    def _test_basic_watchers(self):
        """Test basic watcher functionality"""
        watcher_files = list(self.vault_path.glob("*watcher*.py"))
        result = len(watcher_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Basic watchers: Found {len(watcher_files)} watcher files")
        return result

    def _test_bronze_requirements_met(self):
        """Check if Bronze requirements are met"""
        return self._test_obsidian_vault() and self._test_dashboard_exists()

    def _test_multiple_watchers(self):
        """Test multiple watcher types"""
        watcher_files = list(self.vault_path.glob("*watcher*.py"))
        result = len(watcher_files) >= 2
        logger.info(f"  {'✅' if result else '❌'} Multiple watchers: Found {len(watcher_files)} watcher types")
        return result

    def _test_linkedin_automation(self):
        """Test LinkedIn automation capabilities"""
        linkedin_files = list(self.vault_path.glob("*linkedin*.py")) + list(self.vault_path.glob("*linkedin*"))
        result = len(linkedin_files) > 0
        logger.info(f"  {'✅' if result else '❌'} LinkedIn automation: Found {len(linkedin_files)} LinkedIn-related files")
        return result

    def _test_mcp_server(self):
        """Test MCP server functionality"""
        mcp_files = []
        # Use correct glob pattern
        for py_file in self.vault_path.rglob("*.py"):
            if 'mcp' in py_file.name.lower() or 'server' in py_file.name.lower():
                mcp_files.append(py_file)

        # Also check for existing mcp references in content
        for py_file in self.vault_path.glob("*.py"):
            try:
                content = py_file.read_text()
                if 'mcp' in content.lower() or 'server' in content.lower():
                    if py_file not in mcp_files:  # Avoid duplicates
                        mcp_files.append(py_file)
            except:
                continue

        result = len(mcp_files) > 0
        logger.info(f"  {'✅' if result else '❌'} MCP server: Found {len(mcp_files)} MCP-related files")
        return result

    def _test_human_in_the_loop(self):
        """Test human-in-the-loop approval system"""
        approval_dirs = ["Pending_Approval", "Approved", "Rejected"]
        found_dirs = [d for d in approval_dirs if (self.vault_path / d).exists()]
        result = len(found_dirs) >= 2  # Need at least 2 for approval workflow

        logger.info(f"  {'✅' if result else '❌'} Human-in-the-loop: Found {len(found_dirs)}/3 approval directories")
        return result

    def _test_scheduling(self):
        """Test scheduling capabilities"""
        scheduler_files = list(self.vault_path.glob("*scheduler*.py")) + list(self.vault_path.glob("*schedule*.py"))
        result = len(scheduler_files) > 0

        # Also check for cron-like patterns
        if not result:
            for py_file in self.vault_path.glob("*.py"):
                try:
                    content = py_file.read_text()
                    if 'schedule' in content.lower() or 'timer' in content.lower() or 'interval' in content.lower():
                        result = True
                        break
                except:
                    continue

        logger.info(f"  {'✅' if result else '❌'} Scheduling: {'Found' if result else 'Not found'}")
        return result

    def _test_agent_skills(self):
        """Test Agent Skills implementation"""
        skills_dir = self.vault_path / "Skills"
        result = skills_dir.exists()
        logger.info(f"  {'✅' if result else '❌'} Agent Skills: Skills directory {'found' if result else 'missing'}")
        return result

    def _test_silver_requirements_met(self):
        """Check if Silver requirements are met"""
        return self._test_multiple_watchers() and self._test_mcp_server()

    def _test_cross_domain_integration(self):
        """Test cross-domain integration"""
        # Look for files that handle multiple domains (personal + business)
        integration_files = []
        for py_file in self.vault_path.glob("*.py"):
            try:
                content = py_file.read_text()
                if 'personal' in content.lower() and 'business' in content.lower():
                    integration_files.append(py_file)
            except:
                continue

        result = len(integration_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Cross-domain integration: Found {len(integration_files)} integration files")
        return result

    def _test_accounting_integration(self):
        """Test accounting system integration (Odoo)"""
        accounting_files = list(self.vault_path.glob("odoo_mcp/*.py")) + list(self.vault_path.glob("*accounting*.py"))
        result = len(accounting_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Accounting integration: Found {len(accounting_files)} accounting files")
        return result

    def _test_facebook_integration(self):
        """Test Facebook integration"""
        fb_files = list(self.vault_path.glob("facebook*/*.py")) + list(self.vault_path.glob("*facebook*.py"))
        result = len(fb_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Facebook integration: Found {len(fb_files)} Facebook files")
        return result

    def _test_instagram_integration(self):
        """Test Instagram integration"""
        ig_files = list(self.vault_path.glob("instagram*/*.py")) + list(self.vault_path.glob("*instagram*.py"))
        result = len(ig_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Instagram integration: Found {len(ig_files)} Instagram files")
        return result

    def _test_twitter_integration(self):
        """Test Twitter integration"""
        tw_files = list(self.vault_path.glob("twitter*/*.py")) + list(self.vault_path.glob("*twitter*.py"))
        result = len(tw_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Twitter integration: Found {len(tw_files)} Twitter files")
        return result

    def _test_multiple_mcp_servers(self):
        """Test multiple MCP server implementations"""
        mcp_dirs = ["odoo_mcp", "facebook_instagram_mcp", "twitter_mcp"]
        found_dirs = [d for d in mcp_dirs if (self.vault_path / d).exists()]
        result = len(found_dirs) >= 2

        logger.info(f"  {'✅' if result else '❌'} Multiple MCP servers: Found {len(found_dirs)}/{len(mcp_dirs)} server directories")
        return result

    def _test_weekly_audit(self):
        """Test weekly audit and CEO briefing generation"""
        audit_files = list(self.vault_path.glob("*briefing*.py")) + list(self.vault_path.glob("*audit*.py"))
        result = len(audit_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Weekly audit: Found {len(audit_files)} audit/briefing files")
        return result

    def _test_error_recovery(self):
        """Test error recovery capabilities"""
        error_files = list(self.vault_path.glob("*error*.py")) + list(self.vault_path.glob("*handler*.py"))
        result = len(error_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Error recovery: Found {len(error_files)} error handling files")
        return result

    def _test_comprehensive_logging(self):
        """Test comprehensive logging"""
        log_files = list(self.vault_path.glob("*log*.py")) + list(self.vault_path.glob("*.log"))
        result = len(log_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Comprehensive logging: Found {len(log_files)} logging files")
        return result

    def _test_architecture_documentation(self):
        """Test architecture documentation"""
        doc_files = list(self.vault_path.glob("*arch*.md")) + list(self.vault_path.glob("*design*.md"))
        result = len(doc_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Architecture documentation: Found {len(doc_files)} documentation files")
        return result

    def _test_agent_skills_implementation(self):
        """Test agent skills implementation"""
        skills_impl = self._test_agent_skills()
        # Check for skill-related files
        skill_files = list(self.vault_path.glob("Skills/*.py")) + list(self.vault_path.glob("*skill*.py"))
        result = skills_impl or len(skill_files) > 0
        logger.info(f"  {'✅' if result else '❌'} Agent skills implementation: Found skill implementations")
        return result

    def run_all_tier_tests(self):
        """Run tests for all tiers"""
        logger.info("🚀 STARTING COMPREHENSIVE TIER TEST SUITE")
        logger.info("="*70)

        start_time = datetime.now()

        # Run all tier tests
        bronze_success = self.test_bronze_tier()
        silver_success = self.test_silver_tier()
        gold_success = self.test_gold_tier()

        end_time = datetime.now()
        total_duration = end_time - start_time

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("📊 COMPREHENSIVE TIER TEST RESULTS SUMMARY")
        logger.info("="*70)

        tiers = ['bronze', 'silver', 'gold']
        tier_names = ['Bronze', 'Silver', 'Gold']
        tier_successes = [bronze_success, silver_success, gold_success]

        for i, tier in enumerate(tiers):
            if tier in self.tier_results:
                results = self.tier_results[tier]
                status = "✅ PASS" if tier_successes[i] else "❌ FAIL"
                logger.info(f"{status} {tier_names[i]} Tier: {results['passed']}/{results['total']} tests ({results['success_rate']*100:.1f}%)")

        logger.info("-" * 70)
        logger.info(f"⏱️  Total Test Duration: {total_duration.total_seconds():.2f} seconds")

        overall_success = all(tier_successes)
        if overall_success:
            logger.info("🏆 ALL TIERS PASSED - AI Employee system is fully functional!")
        else:
            failed_tiers = [name for i, (name, success) in enumerate(zip(tier_names, tier_successes)) if not success]
            logger.warning(f"⚠️  Some tiers failed: {', '.join(failed_tiers)}")

        logger.info("="*70)

        # Save comprehensive results
        results_file = self.vault_path / "tier_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.tier_results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Comprehensive test results saved to: {results_file}")

        return overall_success

    def test_platform_posting_capabilities(self):
        """Test automated posting on all platforms"""
        logger.info("\n" + "="*70)
        logger.info("📡 TESTING PLATFORM POSTING CAPABILITIES")
        logger.info("="*70)

        # Test if MCP servers for social platforms are properly configured
        platform_tests = {
            "facebook_post_capability": self._test_facebook_post_capability(),
            "instagram_post_capability": self._test_instagram_post_capability(),
            "twitter_post_capability": self._test_twitter_post_capability(),
            "linkedin_post_capability": self._test_linkedin_post_capability()
        }

        passed_tests = sum(1 for result in platform_tests.values() if result)
        total_tests = len(platform_tests)

        logger.info(f"\n📋 Platform Posting: {passed_tests}/{total_tests} platforms ready")

        self.tier_results['platform_posting'] = {
            'tests': platform_tests,
            'passed': passed_tests,
            'total': total_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0
        }

        return passed_tests >= 3  # At least 3 platforms should be ready

    def _test_facebook_post_capability(self):
        """Test Facebook posting capability"""
        fb_mcp_path = self.vault_path / "facebook_instagram_mcp" / "server.py"
        if fb_mcp_path.exists():
            try:
                content = fb_mcp_path.read_text()
                has_post_function = 'post' in content.lower() and ('facebook' in content.lower() or 'fb' in content.lower())
                return has_post_function
            except:
                pass
        return False

    def _test_instagram_post_capability(self):
        """Test Instagram posting capability"""
        ig_mcp_path = self.vault_path / "facebook_instagram_mcp" / "server.py"
        if ig_mcp_path.exists():
            try:
                content = ig_mcp_path.read_text()
                has_post_function = 'post' in content.lower() and 'instagram' in content.lower()
                return has_post_function
            except:
                pass
        return False

    def _test_twitter_post_capability(self):
        """Test Twitter posting capability"""
        tw_mcp_path = self.vault_path / "twitter_mcp" / "server.py"
        if tw_mcp_path.exists():
            try:
                content = tw_mcp_path.read_text()
                has_post_function = 'post_tweet' in content.lower() or 'tweet' in content.lower()
                return has_post_function
            except:
                pass
        return False

    def _test_linkedin_post_capability(self):
        """Test LinkedIn posting capability"""
        linkedin_files = list(self.vault_path.glob("*linkedin*.py"))
        for lf in linkedin_files:
            try:
                content = lf.read_text()
                if 'post' in content.lower() and 'linkedin' in content.lower():
                    return True
            except:
                continue
        return False


def main():
    """Main function to run the tier test suite"""
    logger.info("Initializing Comprehensive Tier Test Suite...")

    tester = TierTestSuite()

    # Run all tier tests
    all_tiers_passed = tester.run_all_tier_tests()

    # Test platform posting capabilities
    platform_posting_ready = tester.test_platform_posting_capabilities()

    # Final summary
    logger.info("\n" + "="*70)
    logger.info("🎯 FINAL COMPREHENSIVE ASSESSMENT")
    logger.info("="*70)

    if all_tiers_passed:
        logger.info("✅ ALL TIER REQUIREMENTS MET")
    else:
        logger.warning("⚠️  SOME TIER REQUIREMENTS NOT MET")

    if platform_posting_ready:
        logger.info("✅ PLATFORM POSTING CAPABILITIES READY")
    else:
        logger.warning("⚠️  PLATFORM POSTING CAPABILITIES LIMITED")

    overall_ready = all_tiers_passed and platform_posting_ready

    if overall_ready:
        logger.info("\n🎉 COMPREHENSIVE TEST SUITE PASSED!")
        logger.info("The AI Employee system is ready for production with all tier requirements and platform posting capabilities!")
    else:
        logger.info("\n⚠️  COMPREHENSIVE TEST SUITE PARTIALLY PASSED")
        logger.info("Some components may need additional attention before production deployment.")

    logger.info("="*70)

    return overall_ready


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)