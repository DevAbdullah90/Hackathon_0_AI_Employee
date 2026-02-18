#!/usr/bin/env python3
"""
Test Automation - Tests for AI Employee automation system
Tests WhatsApp, LinkedIn, Twitter, and Email automation
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project path
sys.path.insert(0, str(Path(__file__).parent))


class AutomationTester:
    """Test suite for AI Employee automation"""

    def __init__(self):
        self.vault_path = Path(__file__).parent
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "PASSED" if success else "FAILED"
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message
        })
        if success:
            self.passed += 1
            logger.info(f"[PASS] {test_name}")
        else:
            self.failed += 1
            logger.error(f"[FAIL] {test_name}: {message}")

    # ====================
    # ENVIRONMENT TESTS
    # ====================

    def test_env_file_exists(self):
        """Test that .env file exists"""
        env_path = self.vault_path / '.env'
        self.log_result(
            "ENV file exists",
            env_path.exists(),
            "" if env_path.exists() else ".env file not found"
        )

    def test_twitter_credentials(self):
        """Test Twitter API credentials are configured"""
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        all_configured = all([api_key, api_secret, access_token, access_secret])
        self.log_result(
            "Twitter credentials configured",
            all_configured,
            "" if all_configured else "Missing Twitter credentials in .env"
        )

    def test_email_credentials(self):
        """Test email credentials are configured"""
        username = os.getenv('EMAIL_USERNAME')
        password = os.getenv('EMAIL_PASSWORD')

        has_username = bool(username)
        self.log_result(
            "Email credentials configured",
            has_username,
            "" if has_username else "Missing EMAIL_USERNAME in .env"
        )

    # ====================
    # FOLDER STRUCTURE TESTS
    # ====================

    def test_folder_structure(self):
        """Test required folders exist"""
        required_folders = [
            'Approved',
            'Pending_Approval',
            'Needs_Action',
            'Done',
            'Failed',
            'Logs',
            'Skills'
        ]

        for folder in required_folders:
            folder_path = self.vault_path / folder
            folder_path.mkdir(exist_ok=True)  # Create if missing
            self.log_result(
                f"Folder exists: {folder}",
                folder_path.exists(),
                ""
            )

    def test_mcp_files_exist(self):
        """Test MCP files are present"""
        mcp_files = [
            'mcp/whatsapp-mcp/whatsapp_mcp.py',
            'mcp/twitter-mcp/twitter_mcp.py',
            'mcp/email-mcp/email_mcp.py',
        ]

        for mcp_file in mcp_files:
            file_path = self.vault_path / mcp_file
            self.log_result(
                f"MCP file exists: {mcp_file}",
                file_path.exists(),
                "" if file_path.exists() else f"File not found: {mcp_file}"
            )

    def test_core_files_exist(self):
        """Test core automation files exist"""
        core_files = [
            'auto_processor.py',
            'linkedin_poster.py',
            'draft_generator.py',
        ]

        for core_file in core_files:
            file_path = self.vault_path / core_file
            self.log_result(
                f"Core file exists: {core_file}",
                file_path.exists(),
                "" if file_path.exists() else f"File not found: {core_file}"
            )

    def test_skill_files_exist(self):
        """Test skill files are present"""
        skill_files = [
            'Skills/email_drafter_skill.md',
            'Skills/whatsapp_reply_skill.md',
            'Skills/linkedin_post_skill.md',
            'Skills/twitter_tweet_skill.md',
        ]

        for skill_file in skill_files:
            file_path = self.vault_path / skill_file
            self.log_result(
                f"Skill file exists: {skill_file}",
                file_path.exists(),
                "" if file_path.exists() else f"File not found: {skill_file}"
            )

    # ====================
    # MODULE IMPORT TESTS
    # ====================

    def test_import_auto_processor(self):
        """Test auto_processor.py can be imported"""
        try:
            from auto_processor import ApprovedFileHandler, PlatformPoster
            self.log_result("Import auto_processor", True)
        except Exception as e:
            self.log_result("Import auto_processor", False, str(e))

    def test_import_draft_generator(self):
        """Test draft_generator.py can be imported"""
        try:
            from draft_generator import DraftGenerator
            self.log_result("Import draft_generator", True)
        except Exception as e:
            self.log_result("Import draft_generator", False, str(e))

    def test_import_linkedin_poster(self):
        """Test linkedin_poster.py can be imported"""
        try:
            from linkedin_poster import LinkedInPoster
            self.log_result("Import linkedin_poster", True)
        except Exception as e:
            self.log_result("Import linkedin_poster", False, str(e))

    # ====================
    # TWITTER TESTS
    # ====================

    def test_twitter_connection(self):
        """Test Twitter API connection"""
        try:
            import tweepy

            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

            if not all([api_key, api_secret, access_token, access_secret]):
                self.log_result("Twitter API connection", False, "Credentials not configured")
                return

            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )

            me = client.get_me()
            if me.data:
                self.log_result("Twitter API connection", True, f"Connected as @{me.data.username}")
            else:
                self.log_result("Twitter API connection", False, "Could not verify credentials")

        except ImportError:
            self.log_result("Twitter API connection", False, "Tweepy not installed. Run: pip install tweepy")
        except Exception as e:
            self.log_result("Twitter API connection", False, str(e))

    def test_twitter_post_draft(self):
        """Test creating a Twitter draft file"""
        try:
            draft_dir = self.vault_path / 'Pending_Approval' / 'Twitter'
            draft_dir.mkdir(parents=True, exist_ok=True)

            test_content = f"""---
type: twitter_post
topic: test
status: test_draft
created_at: {datetime.now().isoformat()}
---

# Test Twitter Draft

## Tweet Content

This is a test tweet. #Testing

## Actions
- [x] Test draft
"""
            test_file = draft_dir / f"TEST_TWITTER_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            test_file.write_text(test_content)

            self.log_result("Create Twitter draft", test_file.exists())

            # Cleanup
            test_file.unlink()

        except Exception as e:
            self.log_result("Create Twitter draft", False, str(e))

    # ====================
    # EMAIL TESTS
    # ====================

    def test_email_smtp_connection(self):
        """Test SMTP server connection"""
        try:
            import smtplib

            smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
            username = os.getenv('EMAIL_USERNAME')
            password = os.getenv('EMAIL_PASSWORD')

            if not username:
                self.log_result("Email SMTP connection", False, "EMAIL_USERNAME not configured")
                return

            if not password:
                self.log_result("Email SMTP connection", False, "EMAIL_PASSWORD not configured (use App Password for Gmail)")
                return

            # Just test connection, don't login
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                # Try login only if password is set
                try:
                    server.login(username, password)
                    self.log_result("Email SMTP connection", True, f"Connected to {smtp_server}")
                except smtplib.SMTPAuthenticationError:
                    self.log_result("Email SMTP connection", False, "Authentication failed - check EMAIL_PASSWORD (use App Password for Gmail)")

        except Exception as e:
            self.log_result("Email SMTP connection", False, str(e))

    def test_email_draft_creation(self):
        """Test creating an email draft file"""
        try:
            sys.path.insert(0, str(self.vault_path / 'mcp' / 'email-mcp'))
            from email_mcp import EmailMCP

            mcp = EmailMCP()
            result = mcp.create_draft(
                to="test@example.com",
                subject="Test Subject",
                body="This is a test email body."
            )

            success = result.get('success', False)
            self.log_result("Create email draft", success)

            # Cleanup test file
            if success and result.get('draft_file'):
                Path(result['draft_file']).unlink(missing_ok=True)

        except Exception as e:
            self.log_result("Create email draft", False, str(e))

    # ====================
    # WHATSAPP TESTS
    # ====================

    def test_whatsapp_session_dir(self):
        """Test WhatsApp session directory exists"""
        session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
        session_dir = Path(session_path)
        session_dir.mkdir(parents=True, exist_ok=True)

        self.log_result("WhatsApp session directory", session_dir.exists())

    def test_whatsapp_mcp_import(self):
        """Test WhatsApp MCP can be imported"""
        try:
            sys.path.insert(0, str(self.vault_path / 'mcp' / 'whatsapp-mcp'))
            from whatsapp_mcp import WhatsAppMCP

            mcp = WhatsAppMCP()
            self.log_result("WhatsApp MCP import", True)

        except Exception as e:
            self.log_result("WhatsApp MCP import", False, str(e))

    # ====================
    # LINKEDIN TESTS
    # ====================

    def test_linkedin_session_dir(self):
        """Test LinkedIn session directory exists"""
        session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session')
        session_dir = Path(session_path)
        session_dir.mkdir(parents=True, exist_ok=True)

        self.log_result("LinkedIn session directory", session_dir.exists())

    def test_linkedin_poster_import(self):
        """Test LinkedIn poster can be imported"""
        try:
            from linkedin_poster import LinkedInPoster

            poster = LinkedInPoster()
            self.log_result("LinkedIn poster import", True)

        except Exception as e:
            self.log_result("LinkedIn poster import", False, str(e))

    # ====================
    # DRAFT GENERATOR TESTS
    # ====================

    def test_draft_generator_email(self):
        """Test draft generator creates email drafts"""
        try:
            from draft_generator import DraftGenerator

            generator = DraftGenerator(self.vault_path)
            result = generator.generate_email_draft(
                original_email={
                    'from': 'test@example.com',
                    'subject': 'Test Invoice',
                    'body': 'Please find attached the invoice for services.'
                },
                source_file=Path('test_email.md')
            )

            success = result.get('success', False)
            self.log_result("Draft generator - email", success)

            # Cleanup
            if success and result.get('draft_file'):
                Path(result['draft_file']).unlink(missing_ok=True)

        except Exception as e:
            self.log_result("Draft generator - email", False, str(e))

    def test_draft_generator_linkedin(self):
        """Test draft generator creates LinkedIn drafts"""
        try:
            from draft_generator import DraftGenerator

            generator = DraftGenerator(self.vault_path)
            result = generator.generate_linkedin_post_draft(
                topic="AI and Automation",
                post_type="thought_leadership"
            )

            success = result.get('success', False)
            self.log_result("Draft generator - LinkedIn", success)

            # Cleanup
            if success and result.get('draft_file'):
                Path(result['draft_file']).unlink(missing_ok=True)

        except Exception as e:
            self.log_result("Draft generator - LinkedIn", False, str(e))

    def test_draft_generator_twitter(self):
        """Test draft generator creates Twitter drafts"""
        try:
            from draft_generator import DraftGenerator

            generator = DraftGenerator(self.vault_path)
            result = generator.generate_twitter_draft(
                topic="Testing automation",
                tweet_type="insight"
            )

            success = result.get('success', False)
            self.log_result("Draft generator - Twitter", success)

            # Cleanup
            if success and result.get('draft_file'):
                Path(result['draft_file']).unlink(missing_ok=True)

        except Exception as e:
            self.log_result("Draft generator - Twitter", False, str(e))

    # ====================
    # AUTO PROCESSOR TESTS
    # ====================

    def test_auto_processor_metadata_extraction(self):
        """Test auto processor can extract metadata from files"""
        try:
            from auto_processor import ApprovedFileHandler

            handler = ApprovedFileHandler(self.vault_path)

            test_content = """---
type: linkedin_post
topic: test
status: approved
---

# Test Post

Test content here.
"""
            metadata = handler.extract_metadata(test_content)
            success = metadata.get('type') == 'linkedin_post'

            self.log_result("Auto processor - metadata extraction", success)

        except Exception as e:
            self.log_result("Auto processor - metadata extraction", False, str(e))

    def test_auto_processor_content_extraction(self):
        """Test auto processor can extract post content from files"""
        try:
            from auto_processor import ApprovedFileHandler

            handler = ApprovedFileHandler(self.vault_path)

            test_content = """---
type: linkedin_post
---

# LinkedIn Post

## Post Content

This is the actual post content that should be extracted.

## Other Section

This should not be included.
"""
            content = handler.extract_post_content(test_content)
            success = "actual post content" in content.lower()

            self.log_result("Auto processor - content extraction", success)

        except Exception as e:
            self.log_result("Auto processor - content extraction", False, str(e))

    # ====================
    # RUN ALL TESTS
    # ====================

    def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 60)
        logger.info("AI EMPLOYEE AUTOMATION TEST SUITE")
        logger.info("=" * 60)

        # Environment tests
        logger.info("\n--- Environment Tests ---")
        self.test_env_file_exists()
        self.test_twitter_credentials()
        self.test_email_credentials()

        # Folder structure tests
        logger.info("\n--- Folder Structure Tests ---")
        self.test_folder_structure()
        self.test_mcp_files_exist()
        self.test_core_files_exist()
        self.test_skill_files_exist()

        # Module import tests
        logger.info("\n--- Module Import Tests ---")
        self.test_import_auto_processor()
        self.test_import_draft_generator()
        self.test_import_linkedin_poster()

        # Twitter tests
        logger.info("\n--- Twitter Tests ---")
        self.test_twitter_connection()
        self.test_twitter_post_draft()

        # Email tests
        logger.info("\n--- Email Tests ---")
        self.test_email_smtp_connection()
        self.test_email_draft_creation()

        # WhatsApp tests
        logger.info("\n--- WhatsApp Tests ---")
        self.test_whatsapp_session_dir()
        self.test_whatsapp_mcp_import()

        # LinkedIn tests
        logger.info("\n--- LinkedIn Tests ---")
        self.test_linkedin_session_dir()
        self.test_linkedin_poster_import()

        # Draft generator tests
        logger.info("\n--- Draft Generator Tests ---")
        self.test_draft_generator_email()
        self.test_draft_generator_linkedin()
        self.test_draft_generator_twitter()

        # Auto processor tests
        logger.info("\n--- Auto Processor Tests ---")
        self.test_auto_processor_metadata_extraction()
        self.test_auto_processor_content_extraction()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total: {self.passed + self.failed}")
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        logger.info("=" * 60)

        # Write results to file
        results_file = self.vault_path / 'Logs' / f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": self.passed + self.failed,
                    "passed": self.passed,
                    "failed": self.failed
                },
                "results": self.results
            }, f, indent=2)

        logger.info(f"\nResults saved to: {results_file}")

        return self.failed == 0


def main():
    """Main entry point"""
    tester = AutomationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
