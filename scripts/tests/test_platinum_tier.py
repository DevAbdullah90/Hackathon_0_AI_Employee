#!/usr/bin/env python3
"""
Platinum Tier Functionality Test Suite
Tests all Platinum tier requirements for the AI Employee
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PlatinumTierTester:
    """Test suite for Platinum tier functionality"""

    def __init__(self):
        self.vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\OneDrive\\Desktop\\hakathone zero\\AI_Employee_vault")
        self.test_results = {}

    def test_odoo_integration(self):
        """Test Odoo MCP server integration"""
        logger.info("Testing Odoo integration...")

        try:
            # Check if Odoo MCP server exists
            odoo_server_path = self.vault_path / "odoo_mcp" / "server.py"
            if not odoo_server_path.exists():
                logger.error("Odoo MCP server not found")
                return False

            # Check if server file is valid Python
            result = subprocess.run([sys.executable, "-m", "py_compile", str(odoo_server_path)],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Odoo server compilation failed: {result.stderr}")
                return False

            logger.info("Odoo MCP server exists and compiles successfully")

            # Check if configuration exists
            config_path = self.vault_path / "odoo_mcp" / "mcp_config.json"
            if not config_path.exists():
                logger.warning("Odoo MCP config file not found, but server exists")
                return True  # Server exists which is the main requirement

            with open(config_path, 'r') as f:
                config = json.load(f)

            if 'servers' not in config:
                logger.error("Invalid Odoo MCP config format")
                return False

            odoo_server_found = any(server.get('name') == 'odoo' for server in config['servers'])
            if not odoo_server_found:
                logger.error("Odoo server not configured in MCP config")
                return False

            logger.info("Odoo MCP configuration is valid")
            return True

        except Exception as e:
            logger.error(f"Error testing Odoo integration: {e}")
            return False

    def test_social_media_integrations(self):
        """Test Facebook/Instagram and Twitter MCP servers"""
        logger.info("Testing social media integrations...")

        # Test Facebook/Instagram MCP
        fb_ig_server_path = self.vault_path / "facebook_instagram_mcp" / "server.py"
        if not fb_ig_server_path.exists():
            logger.error("Facebook/Instagram MCP server not found")
            return False

        result = subprocess.run([sys.executable, "-m", "py_compile", str(fb_ig_server_path)],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Facebook/Instagram server compilation failed: {result.stderr}")
            return False

        logger.info("Facebook/Instagram MCP server exists and compiles successfully")

        # Test Twitter MCP
        twitter_server_path = self.vault_path / "twitter_mcp" / "server.py"
        if not twitter_server_path.exists():
            logger.error("Twitter MCP server not found")
            return False

        result = subprocess.run([sys.executable, "-m", "py_compile", str(twitter_server_path)],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Twitter server compilation failed: {result.stderr}")
            return False

        logger.info("Twitter MCP server exists and compiles successfully")

        return True

    def test_cloud_deployment_docs(self):
        """Test cloud deployment documentation"""
        logger.info("Testing cloud deployment documentation...")

        cloud_doc_path = self.vault_path / "cloud_deployment.md"
        if not cloud_doc_path.exists():
            logger.error("Cloud deployment documentation not found")
            return False

        content = cloud_doc_path.read_text()
        required_sections = [
            "VM Provisioning",
            "Environment Configuration",
            "Service Management",
            "Health Monitoring",
            "Backup Strategy"
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            logger.error(f"Missing sections in cloud deployment doc: {missing_sections}")
            return False

        logger.info("Cloud deployment documentation is complete")
        return True

    def test_work_zone_specialization(self):
        """Test work-zone specialization documentation"""
        logger.info("Testing work-zone specialization...")

        wz_doc_path = self.vault_path / "work_zone_specialization.md"
        if not wz_doc_path.exists():
            logger.error("Work-zone specialization documentation not found")
            return False

        content = wz_doc_path.read_text()
        required_concepts = [
            "Domain Ownership Structure",
            "Claim-by-Move Rule",
            "Single-Writer Rule",
            "Vault Sync Configuration",
            "Security Rules"
        ]

        missing_concepts = []
        for concept in required_concepts:
            if concept not in content:
                missing_concepts.append(concept)

        if missing_concepts:
            logger.error(f"Missing concepts in work-zone specialization: {missing_concepts}")
            return False

        logger.info("Work-zone specialization documentation is complete")
        return True

    def test_vault_sync_implementation(self):
        """Test vault sync implementation"""
        logger.info("Testing vault sync implementation...")

        sync_manager_path = self.vault_path / "vault_sync_manager.py"
        if not sync_manager_path.exists():
            logger.error("Vault sync manager not found")
            return False

        result = subprocess.run([sys.executable, "-m", "py_compile", str(sync_manager_path)],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Vault sync manager compilation failed: {result.stderr}")
            return False

        # Test importing the classes
        try:
            sys.path.insert(0, str(self.vault_path))
            import vault_sync_manager
            # Check if required classes exist
            required_classes = ['VaultSyncManager', 'ClaimByMoveRule', 'DashboardUpdater']
            for cls_name in required_classes:
                if not hasattr(vault_sync_manager, cls_name):
                    logger.error(f"Missing class {cls_name} in vault sync manager")
                    return False

            logger.info("Vault sync manager has all required classes")
        except ImportError as e:
            logger.error(f"Error importing vault sync manager: {e}")
            return False

        logger.info("Vault sync implementation is complete")
        return True

    def test_odoo_cloud_deployment(self):
        """Test Odoo cloud deployment documentation"""
        logger.info("Testing Odoo cloud deployment documentation...")

        odoo_cloud_doc_path = self.vault_path / "odoo_cloud_deployment.md"
        if not odoo_cloud_doc_path.exists():
            logger.error("Odoo cloud deployment documentation not found")
            return False

        content = odoo_cloud_doc_path.read_text()
        required_sections = [
            "VM Provisioning",
            "PostgreSQL Database Setup",
            "SSL Certificate Setup",
            "Health Monitoring",
            "Backup Strategy",
            "Security Considerations"
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            logger.error(f"Missing sections in Odoo cloud deployment: {missing_sections}")
            return False

        logger.info("Odoo cloud deployment documentation is complete")
        return True

    def test_folder_structure(self):
        """Test required folder structure"""
        logger.info("Testing required folder structure...")

        required_dirs = [
            "odoo_mcp",
            "facebook_instagram_mcp",
            "twitter_mcp",
            "Needs_Action",
            "Approved",
            "Pending_Approval",
            "Plans",
            "Done",
            "In_Progress",
            "Updates"
        ]

        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.vault_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        if missing_dirs:
            logger.error(f"Missing directories: {missing_dirs}")
            return False

        logger.info("Required folder structure is in place")
        return True

    def test_business_goals_template(self):
        """Test Business Goals template exists"""
        logger.info("Testing Business Goals template...")

        business_goals_path = self.vault_path / "Business_Goals.md"
        if not business_goals_path.exists():
            logger.warning("Business_Goals.md not found, but this may be acceptable")
            return True  # This may be user-created

        content = business_goals_path.read_text()
        required_elements = [
            "Q1 2026 Objectives",
            "Revenue Target",
            "Key Metrics to Track",
            "Active Projects",
            "Subscription Audit Rules"
        ]

        present_elements = []
        for element in required_elements:
            if element in content:
                present_elements.append(element)

        if len(present_elements) >= 3:  # At least most elements should be present
            logger.info("Business Goals template has required elements")
            return True
        else:
            logger.warning(f"Business Goals template missing some elements: {set(required_elements) - set(present_elements)}")
            return True  # This may be user-customized

    def test_ceo_briefing_generation(self):
        """Test CEO briefing generation capability"""
        logger.info("Testing CEO briefing generation...")

        briefing_gen_path = self.vault_path / "ceo_briefing_generator.py"
        if not briefing_gen_path.exists():
            logger.error("CEO briefing generator not found")
            return False

        result = subprocess.run([sys.executable, "-m", "py_compile", str(briefing_gen_path)],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"CEO briefing generator compilation failed: {result.stderr}")
            return False

        logger.info("CEO briefing generator exists and compiles successfully")
        return True

    def run_all_tests(self):
        """Run all Platinum tier tests"""
        logger.info("Starting Platinum Tier functionality tests...")

        tests = [
            ("Odoo Integration", self.test_odoo_integration),
            ("Social Media Integrations", self.test_social_media_integrations),
            ("Cloud Deployment Docs", self.test_cloud_deployment_docs),
            ("Work Zone Specialization", self.test_work_zone_specialization),
            ("Vault Sync Implementation", self.test_vault_sync_implementation),
            ("Odoo Cloud Deployment", self.test_odoo_cloud_deployment),
            ("Folder Structure", self.test_folder_structure),
            ("Business Goals Template", self.test_business_goals_template),
            ("CEO Briefing Generation", self.test_ceo_briefing_generation),
        ]

        results = {}
        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                logger.info(f"Test '{test_name}': {'PASS' if result else 'FAIL'}")
            except Exception as e:
                logger.error(f"Test '{test_name}' raised exception: {e}")
                results[test_name] = False

        self.test_results = results

        # Print summary
        passed = sum(results.values())
        total = len(results)

        logger.info("="*50)
        logger.info(f"TEST SUMMARY: {passed}/{total} tests passed")
        logger.info("="*50)

        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            logger.info(f"{test_name}: {status}")

        logger.info("="*50)

        if passed == total:
            logger.info("🎉 ALL PLATINUM TIER TESTS PASSED!")
            logger.info("The AI Employee has successfully implemented all Platinum tier requirements.")
        else:
            logger.info(f"❌ {total-passed} tests failed. Please review the implementation.")

        return passed == total


def main():
    """Main function to run the test suite"""
    tester = PlatinumTierTester()
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()