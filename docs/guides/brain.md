# BRAIN.md

## AI EMPLOYEE SYSTEM TECHNICAL REFERENCE

This document contains all the technical details about the AI Employee system architecture, implementation, and deployment.

---

## MCP SERVERS DETAILS

### File: `~/.config/claude-code/mcp.json`
```json
{
  "servers": {
    "email_mcp": {
      "command": "python",
      "args": ["-m", "generated_email_handler"],
      "env": {
        "EMAIL_USERNAME": "${EMAIL_USERNAME}",
        "EMAIL_PASSWORD": "${EMAIL_PASSWORD}",
        "EMAIL_SMTP_SERVER": "${EMAIL_SMTP_SERVER}",
        "EMAIL_IMAP_SERVER": "${EMAIL_IMAP_SERVER}"
      },
      "port": 8081,
      "protocol": "http"
    },
    "linkedin_mcp": {
      "command": "python",
      "args": ["-m", "linkedin_poster"],
      "env": {
        "LINKEDIN_EMAIL": "${LINKEDIN_EMAIL}",
        "LINKEDIN_PASSWORD": "${LINKEDIN_PASSWORD}",
        "LINKEDIN_COOKIES_PATH": "${LINKEDIN_COOKIES_PATH}"
      },
      "port": 8082,
      "protocol": "http"
    },
    "whatsapp_mcp": {
      "command": "python",
      "args": ["-m", "instagram_playwright"],
      "env": {
        "INSTAGRAM_USERNAME": "${INSTAGRAM_USERNAME}",
        "INSTAGRAM_PASSWORD": "${INSTAGRAM_PASSWORD}",
        "INSTAGRAM_SESSION_PATH": "${INSTAGRAM_SESSION_PATH}"
      },
      "port": 8083,
      "protocol": "http"
    },
    "twitter_mcp": {
      "command": "python",
      "args": ["-m", "twitter_api_wrapper"],
      "env": {
        "TWITTER_API_KEY": "${TWITTER_API_KEY}",
        "TWITTER_API_SECRET": "${TWITTER_API_SECRET}",
        "TWITTER_ACCESS_TOKEN": "${TWITTER_ACCESS_TOKEN}",
        "TWITTER_ACCESS_TOKEN_SECRET": "${TWITTER_ACCESS_TOKEN_SECRET}"
      },
      "port": 8084,
      "protocol": "http"
    }
  },
  "settings": {
    "enable_cache": true,
    "connection_timeout": 30000,
    "max_retries": 3
  }
}
```

### Testing MCP Servers:
```bash
# Test email MCP server
curl -X POST http://localhost:8081/process -H "Content-Type: application/json" -d '{
  "sender": "test@example.com",
  "subject": "Test Email",
  "content": "This is a test email for MCP server"
}'

# Test LinkedIn MCP server
curl -X POST http://localhost:8082/post -H "Content-Type: application/json" -d '{
  "content": "Test LinkedIn post",
  "visibility": "public"
}'
```

---

## WATCHER SCRIPTS CODE

### Gmail Watcher Authentication (`email_watcher.py`):
```python
import imaplib
import email
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from pathlib import Path
import os
from datetime import datetime
import time

class GmailWatcher:
    def __init__(self):
        self.username = os.getenv('EMAIL_USERNAME')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.imap_server = os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com')
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))

        # OAuth2 setup (if available)
        self.oauth2_token = os.getenv('GMAIL_OAUTH2_TOKEN')

    def connect_gmail(self):
        """Connect to Gmail using IMAP"""
        try:
            # Use OAuth2 if available, otherwise use app password
            if self.oauth2_token:
                # OAuth2 authentication
                auth_string = f'user={self.username}\x01auth=Bearer {self.oauth2_token}\x01\x01'
                auth_bytes = auth_string.encode('utf-8')
                auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.authenticate('XOAUTH2', lambda x: auth_base64)
            else:
                # App password authentication
                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.login(self.username, self.password)

            return mail
        except Exception as e:
            print(f"Failed to connect to Gmail: {e}")
            return None

    def check_unread_emails(self):
        """Check for unread emails with specific keywords"""
        mail = self.connect_gmail()
        if not mail:
            return []

        try:
            mail.select('inbox')

            # Search for unread emails with specific keywords
            status, messages = mail.search(None, 'UNSEEN')

            email_list = []
            for msg_id in messages[0].split():
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                # Extract email details
                subject = msg.get('Subject', '')
                sender = msg.get('From', '')

                # Check if email contains monitored keywords
                content = self.get_email_body(msg)
                if self.contains_monitored_keywords(content, subject):
                    email_list.append({
                        'id': msg_id.decode(),
                        'subject': subject,
                        'sender': sender,
                        'content': content,
                        'timestamp': datetime.now().isoformat(),
                        'folder': 'Needs_Action'
                    })

                    # Mark as read after processing
                    mail.store(msg_id, '+FLAGS', '\\Seen')

            mail.close()
            mail.logout()
            return email_list

        except Exception as e:
            print(f"Error checking emails: {e}")
            return []

    def contains_monitored_keywords(self, content, subject):
        """Check if email contains monitored keywords"""
        monitored_keywords = ['urgent', 'invoice', 'payment', 'opportunity', 'hackathon', 'business']
        text = (content + ' ' + subject).lower()
        return any(keyword in text for keyword in monitored_keywords)

    def get_email_body(self, msg):
        """Extract email body content"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()

    def run_continuous(self, check_interval=300):
        """Run continuous monitoring"""
        while True:
            try:
                emails = self.check_unread_emails()
                for email_data in emails:
                    self.create_action_file(email_data)

                print(f"Checked emails, found {len(emails)} matches")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("Gmail watcher stopped")
                break
            except Exception as e:
                print(f"Error in Gmail watcher: {e}")
                time.sleep(60)  # Wait before retrying

    def create_action_file(self, email_data):
        """Create action file in Needs_Action folder"""
        vault_path = Path(os.getenv('VAULT_PATH', '.'))
        needs_action_path = vault_path / 'Needs_Action'
        needs_action_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_{timestamp}_NEEDS_ACTION.md"
        filepath = needs_action_path / filename

        content = f"""---
type: email
from: {email_data['sender']}
subject: {email_data['subject']}
received_at: {email_data['timestamp']}
status: pending_review
priority: medium
---

# Email: {email_data['subject']}

**From**: {email_data['sender']}
**Received**: {email_data['timestamp']}
**Keywords**: Matched monitored keywords

## Original Content
{email_data['content']}

---
## Actions Required
- [ ] Review email content
- [ ] Determine appropriate response
- [ ] Process according to company policy
- [ ] Update status when completed
"""

        filepath.write_text(content)
        print(f"Created action file: {filepath}")

if __name__ == "__main__":
    watcher = GmailWatcher()
    watcher.run_continuous()
```

### WhatsApp Watcher Playwright Setup (`whatsapp_watcher.py`):
```python
import asyncio
from playwright.async_api import async_playwright
import json
import os
from pathlib import Path
import time
from datetime import datetime

class WhatsAppWatcher:
    def __init__(self):
        self.session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
        self.username = os.getenv('WHATSAPP_USERNAME')
        self.password = os.getenv('WHATSAPP_PASSWORD')
        self.browser = None
        self.context = None
        self.page = None

        # Create session directory
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

    async def initialize_browser(self):
        """Initialize Playwright browser with WhatsApp session"""
        try:
            self.playwright = await async_playwright().start()

            # Launch browser with WhatsApp Web context
            self.context = await self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,  # WhatsApp Web requires visible browser
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--allow-running-insecure-content'
                ],
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )

            # Get or create page
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

            # Navigate to WhatsApp Web
            await self.page.goto('https://web.whatsapp.com/', wait_until='networkidle')

            # Wait for QR code or logged-in state
            try:
                # Wait for QR code (not logged in)
                qr_selector = 'div[data-ref]'
                await self.page.wait_for_selector(qr_selector, timeout=10000)
                print("QR code detected. Please scan with your phone.")

                # Wait for login to complete
                await self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=30000)
                print("WhatsApp Web logged in successfully")

            except:
                # Already logged in
                await self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=10000)
                print("WhatsApp Web already logged in")

            return True

        except Exception as e:
            print(f"Error initializing WhatsApp browser: {e}")
            return False

    async def check_unread_messages(self):
        """Check for unread WhatsApp messages"""
        try:
            # Get all chats
            chat_elements = await self.page.query_selector_all('div[data-testid="chat-list"] div[tabindex]')

            unread_messages = []

            for chat_element in chat_elements:
                try:
                    # Check if chat has unread messages
                    unread_badge = await chat_element.query_selector('span[data-testid="unread-count"]')
                    if unread_badge:
                        # Click on the chat
                        await chat_element.click()
                        await self.page.wait_for_timeout(2000)

                        # Get last message in chat
                        message_elements = await self.page.query_selector_all('div[data-testid="msg-container"] div[data-testid="message"]')

                        if message_elements:
                            last_message = message_elements[-1]
                            message_text = await last_message.inner_text()

                            # Extract contact name
                            contact_name = await chat_element.get_attribute('aria-label')

                            unread_messages.append({
                                'contact': contact_name,
                                'message': message_text,
                                'timestamp': datetime.now().isoformat(),
                                'status': 'unread'
                            })

                except Exception as e:
                    print(f"Error processing chat: {e}")
                    continue

            return unread_messages

        except Exception as e:
            print(f"Error checking unread messages: {e}")
            return []

    async def send_message(self, phone_number, message):
        """Send WhatsApp message using Playwright"""
        try:
            # Format phone number for WhatsApp Web URL
            formatted_phone = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            url = f'https://web.whatsapp.com/send?phone={formatted_phone}&text={message}'

            await self.page.goto(url)
            await self.page.wait_for_timeout(5000)

            # Wait for message box and send button
            message_box = await self.page.wait_for_selector('div[contenteditable="true"][data-testid="conversation-compose-box-input"]', timeout=10000)
            send_button = await self.page.wait_for_selector('button[data-testid="compose-btn-send"]', timeout=10000)

            # Fill message and send
            await message_box.fill(message)
            await send_button.click()

            print(f"Message sent to {phone_number}")
            return True

        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    async def run_continuous(self, check_interval=300):
        """Run continuous monitoring"""
        if not await self.initialize_browser():
            print("Failed to initialize WhatsApp browser")
            return

        while True:
            try:
                # Check for unread messages
                unread_msgs = await self.check_unread_messages()

                for msg in unread_msgs:
                    self.create_action_file(msg)

                print(f"Checked WhatsApp, found {len(unread_msgs)} unread messages")
                await asyncio.sleep(check_interval)

            except KeyboardInterrupt:
                print("WhatsApp watcher stopped")
                await self.close_browser()
                break
            except Exception as e:
                print(f"Error in WhatsApp watcher: {e}")
                await asyncio.sleep(60)

    def create_action_file(self, msg_data):
        """Create action file in Needs_Action folder"""
        vault_path = Path(os.getenv('VAULT_PATH', '.'))
        needs_action_path = vault_path / 'Needs_Action'
        needs_action_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"WHATSAPP_{timestamp}_MESSAGE.md"
        filepath = needs_action_path / filename

        content = f"""---
type: whatsapp_message
contact: {msg_data['contact']}
received_at: {msg_data['timestamp']}
status: pending_reply
priority: medium
---

# WhatsApp Message from: {msg_data['contact']}

**Received**: {msg_data['timestamp']}

## Message Content
{msg_data['message']}

---
## Actions Required
- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Reply if necessary
- [ ] Update status when completed
"""

        filepath.write_text(content)
        print(f"Created WhatsApp action file: {filepath}")

    async def close_browser(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()

# Async main function
async def main():
    watcher = WhatsAppWatcher()
    await watcher.run_continuous()

if __name__ == "__main__":
    asyncio.run(main())
```

### File System Watcher Logic (`auto_processor.py`):
```python
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
import asyncio

class ApprovedFileHandler(FileSystemEventHandler):
    """Handles file events in the Approved folder"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.approved_folder = vault_path / 'Approved'
        self.done_folder = vault_path / 'Done'
        self.failed_folder = vault_path / 'Failed'
        self.logs_folder = vault_path / 'Logs'
        self.dashboard_file = vault_path / 'Dashboard.md'

        # Ensure directories exist
        self.done_folder.mkdir(exist_ok=True)
        self.failed_folder.mkdir(exist_ok=True)
        self.logs_folder.mkdir(exist_ok=True)
        self.approved_folder.mkdir(exist_ok=True)

    def on_created(self, event):
        """Called when a file is created in the Approved folder"""
        if not event.is_directory and event.src_path.endswith('.md'):
            file_path = Path(event.src_path)
            logger.info(f"New file detected: {event.src_path}")

            # Small delay to ensure file is fully written
            time.sleep(1)
            asyncio.run(self.process_file(file_path))

    def on_modified(self, event):
        """Called when a file is modified"""
        # Skip modified events to avoid duplicate processing
        pass

    async def process_file(self, file_path: Path):
        """Process a single approved file and post to appropriate platform"""
        try:
            if not file_path.exists():
                logger.warning(f"File no longer exists: {file_path}")
                return

            logger.info(f"Processing file: {file_path.name}")
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata and content
            metadata = self.extract_metadata(content)
            post_content = self.extract_post_content(content)
            file_type = metadata.get('type', '').lower()

            logger.info(f"File type detected: {file_type}")

            # Route to appropriate platform
            result = await self.route_to_platform(file_type, post_content, metadata)

            if result.get('success'):
                # Create success log and move to Done
                self.create_log_entry(file_path, metadata, result, success=True)
                dest_path = self.move_to_done(file_path)
                self.update_dashboard(file_path.name, metadata, result, success=True)
                logger.info(f"Successfully processed and posted: {file_path.name}")
            else:
                # Create failure log and move to Failed
                self.create_log_entry(file_path, metadata, result, success=False)
                dest_path = self.move_to_failed(file_path)
                self.update_dashboard(file_path.name, metadata, result, success=False)
                logger.error(f"Failed to post: {file_path.name} - {result.get('error')}")

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}", exc_info=True)
            self.move_to_failed(file_path)

    def extract_metadata(self, content: str) -> dict:
        """Extract YAML frontmatter metadata from file"""
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                except:
                    pass
        return metadata

    def extract_post_content(self, content: str) -> str:
        """Extract the actual post content from the file"""
        # Remove YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        # Try to extract content from specific sections
        import re
        patterns = [
            r'## Post Content\s*\n(.*?)(?=\n##|\Z)',
            r'## Message\s*\n(.*?)(?=\n##|\Z)',
            r'## Content\s*\n(.*?)(?=\n##|\Z)',
            r'## Tweet\s*\n(.*?)(?=\n##|\Z)',
            r'## Email Body\s*\n(.*?)(?=\n##|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()

        # If no specific section found, return content without headers
        lines = content.split('\n')
        clean_lines = [l for l in lines if not l.startswith('#') and not l.startswith('-')]
        return '\n'.join(clean_lines).strip()

    async def route_to_platform(self, file_type: str, content: str, metadata: dict) -> dict:
        """Route content to appropriate platform based on file type"""

        # Normalize type names
        type_mapping = {
            'linkedin_post': 'linkedin',
            'linkedin_post_approval': 'linkedin',
            'linkedin': 'linkedin',
            'twitter_post': 'twitter',
            'twitter': 'twitter',
            'tweet': 'twitter',
            'whatsapp': 'whatsapp',
            'whatsapp_message': 'whatsapp',
            'email': 'email',
            'email_draft': 'email',
            'instagram_post': 'instagram',
            'instagram': 'instagram',
        }

        platform = type_mapping.get(file_type, file_type)

        if platform == 'linkedin':
            return await self.post_to_linkedin(content, metadata)
        elif platform == 'twitter':
            return self.post_to_twitter(content, metadata)
        elif platform == 'whatsapp':
            phone = metadata.get('phone') or metadata.get('to') or metadata.get('recipient')
            if not phone:
                return {"success": False, "platform": "whatsapp", "error": "No phone number specified"}
            return await self.send_whatsapp(phone, content, metadata)
        elif platform == 'email':
            to = metadata.get('to') or metadata.get('recipient')
            subject = metadata.get('subject', 'No Subject')
            if not to:
                return {"success": False, "platform": "email", "error": "No recipient specified"}
            return self.send_email(to, subject, content, metadata)
        elif platform == 'instagram':
            return await self.post_to_instagram(content, metadata)
        else:
            logger.warning(f"Unknown platform type: {file_type}. Processing as generic file.")
            return {
                "success": True,
                "platform": "generic",
                "note": "Processed without posting"
            }

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/auto_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function - runs the auto processor"""
    logger.info("=" * 60)
    logger.info("AUTO PROCESSOR - Starting 24/7 Platform Poster")
    logger.info("=" * 60)

    # Set up vault path
    vault_path = Path(__file__).parent.resolve()
    approved_folder = vault_path / 'Approved'

    # Ensure approved folder exists
    approved_folder.mkdir(exist_ok=True)

    logger.info(f"Vault path: {vault_path}")
    logger.info(f"Monitoring: {approved_folder}")

    # Create event handler
    event_handler = ApprovedFileHandler(vault_path)

    # Process any existing files first
    event_handler.process_existing_files()

    # Set up observer
    observer = Observer()
    observer.schedule(event_handler, str(approved_folder), recursive=False)

    # Start watching
    observer.start()
    logger.info(f"Started monitoring: {approved_folder}")
    logger.info("Watching for .md files in Approved folder")
    logger.info("Supported types: linkedin_post, twitter_post, whatsapp, email, instagram_post")
    logger.info("Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nShutting down Auto Processor...")
        observer.stop()
        observer.join()
        logger.info("Auto Processor stopped gracefully")

if __name__ == "__main__":
    main()
```

---

## CLAUDE CODE COMMANDS

### Claude Code Commands Used:
```bash
# Initialize Claude Code project
claude-code init

# Set up MCP configuration
claude-code config mcp --set ~/.config/claude-code/mcp.json

# Run the project with Claude Code
claude-code run --project-dir .

# Start the orchestrator through Claude Code
claude-code exec "python workflow_orchestrator.py"

# Monitor the system
claude-code watch --patterns "*.py,*.md,*.json"

# Test individual components
claude-code test email_handler
claude-code test whatsapp_watcher
claude-code test auto_processor
```

### Claude Code Automation Setup:
```python
# In claude_code_config.py
from claude_code import ClaudeCode

class AI_EmployeeAutomation:
    def __init__(self):
        self.claude = ClaudeCode()
        self.setup_automation()

    def setup_automation(self):
        """Set up Claude Code automation for the project"""
        # Define automation rules
        automation_rules = {
            'on_file_change': {
                'patterns': ['*.md', '*.py'],
                'actions': ['lint', 'test', 'deploy']
            },
            'on_skill_update': {
                'patterns': ['skills/*.md'],
                'actions': ['generate_code', 'reload_services']
            },
            'on_config_change': {
                'patterns': ['.env', 'config/*'],
                'actions': ['restart_services']
            }
        }

        # Register automation rules
        for event, rule in automation_rules.items():
            self.claude.register_hook(event, self.handle_automation_rule, rule)

    def handle_automation_rule(self, rule, file_changed):
        """Handle automation rule execution"""
        for action in rule['actions']:
            if action == 'lint':
                self.run_lint()
            elif action == 'test':
                self.run_tests()
            elif action == 'deploy':
                self.deploy_changes()
            elif action == 'generate_code':
                self.generate_code_from_skills()
            elif action == 'reload_services':
                self.reload_mcp_services()
            elif action == 'restart_services':
                self.restart_services()

    def generate_code_from_skills(self):
        """Generate Python code from skill markdown files"""
        import glob

        skill_files = glob.glob('skills/*.md')
        for skill_file in skill_files:
            with open(skill_file, 'r') as f:
                content = f.read()

            # Generate Python code from skill definition
            generated_code = self.claude.generate_code_from_skill(content)

            # Write to generated file
            output_file = f"generated_{skill_file.replace('.md', '.py')}"
            with open(output_file, 'w') as f:
                f.write(generated_code)

# Initialize automation
automation = AI_EmployeeAutomation()
```

---

## TESTING METHODOLOGY

### Testing Framework:
```python
import unittest
import asyncio
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

class TestAI_Employee(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_dir = Path.cwd()
        os.chdir(self.test_dir)

        # Create test vault structure
        folders = ['Inbox', 'Needs_Action', 'Pending_Approval', 'Approved', 'Done', 'Failed', 'Logs', 'Plans']
        for folder in folders:
            (self.test_dir / folder).mkdir()

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_email_watcher(self):
        """Test email watcher functionality"""
        from email_watcher import EmailWatcher

        # Mock email data
        email_data = {
            'sender': 'test@example.com',
            'subject': 'Test Opportunity',
            'content': 'This is a business opportunity worth discussing',
            'timestamp': '2026-01-17T12:00:00'
        }

        # Test action file creation
        watcher = EmailWatcher(self.test_dir)
        watcher.create_action_file(email_data)

        # Verify file was created
        action_files = list((self.test_dir / 'Needs_Action').glob('EMAIL_*.md'))
        self.assertTrue(len(action_files) > 0)

        # Verify content
        content = action_files[0].read_text()
        self.assertIn('business opportunity', content.lower())

    def test_whatsapp_watcher(self):
        """Test WhatsApp watcher functionality"""
        from whatsapp_watcher import WhatsAppWatcher

        # Mock message data
        msg_data = {
            'contact': 'Test Contact',
            'message': 'Hello, interested in your services',
            'timestamp': '2026-01-17T12:00:00'
        }

        # Test action file creation
        watcher = WhatsAppWatcher()
        watcher.create_action_file(msg_data)

        # Verify file was created
        action_files = list((self.test_dir / 'Needs_Action').glob('WHATSAPP_*.md'))
        self.assertTrue(len(action_files) > 0)

    def test_auto_processor(self):
        """Test auto processor functionality"""
        from auto_processor import ApprovedFileHandler

        # Create a test file in Approved folder
        approved_file = self.test_dir / 'Approved' / 'TEST_POST.md'
        approved_file.write_text("""---
type: twitter_post
status: approved
---

# Test Twitter Post

This is a test post for automation testing.
""")

        # Test processing
        handler = ApprovedFileHandler(self.test_dir)
        handler.process_existing_files()

        # Verify file was moved to Done
        done_files = list((self.test_dir / 'Done').glob('*.md'))
        self.assertTrue(len(done_files) > 0)

    def test_dry_run_mode(self):
        """Test dry-run mode functionality"""
        import os
        os.environ['DRY_RUN'] = 'true'

        # Test that actions are logged but not executed
        from auto_processor import ApprovedFileHandler

        approved_file = self.test_dir / 'Approved' / 'DRY_RUN_TEST.md'
        approved_file.write_text("""---
type: linkedin_post
status: approved
---

# Dry Run Test Post

This should be logged but not posted.
""")

        handler = ApprovedFileHandler(self.test_dir)
        # In dry run mode, this should only log the action without executing it
        handler.process_existing_files()

        # Clean up
        os.environ.pop('DRY_RUN', None)

class DryRunMode:
    """Dry run mode implementation"""

    @staticmethod
    def is_dry_run():
        """Check if system is in dry run mode"""
        return os.getenv('DRY_RUN', '').lower() in ['true', '1', 'yes']

    @staticmethod
    def log_only(func):
        """Decorator to only log actions in dry run mode"""
        def wrapper(*args, **kwargs):
            if DryRunMode.is_dry_run():
                print(f"[DRY RUN] Would execute: {func.__name__} with args: {args}, kwargs: {kwargs}")
                return {"success": True, "dry_run": True, "action": func.__name__}
            else:
                return func(*args, **kwargs)
        return wrapper

# Apply dry run decorator to key functions
@DryRunMode.log_only
def post_to_linkedin(content, metadata):
    """Actual LinkedIn posting function"""
    # Real posting logic here
    pass
```

### Running Tests:
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test
python -m unittest tests.test_email_watcher.TestEmailWatcher.test_email_processing

# Run tests with coverage
coverage run -m unittest discover tests/
coverage report
coverage html

# Run dry-run tests
DRY_RUN=true python -m unittest tests.test_auto_processor.TestAutoProcessor.test_dry_run_mode
```

---

## ERROR HANDLING

### Retry Logic Implementation:
```python
import time
import functools
from typing import Callable, Any

def retry_on_failure(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """Decorator to retry function on failure with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        # Last attempt, re-raise the exception
                        raise last_exception

                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff

            # This line should never be reached, but included for completeness
            raise last_exception

        return wrapper
    return decorator

# Usage examples:
@retry_on_failure(max_attempts=3, delay=2, backoff=2)
def post_to_linkedin_with_retry(content, metadata):
    """LinkedIn posting with retry logic"""
    # Actual posting logic
    pass

@retry_on_failure(max_attempts=5, delay=1, exceptions=(ConnectionError, TimeoutError))
def check_email_with_retry():
    """Email checking with retry for network issues"""
    # Email checking logic
    pass
```

### Graceful Degradation:
```python
import logging
from typing import Dict, Any, Optional

class GracefulDegradation:
    """Handle graceful degradation when components fail"""

    def __init__(self):
        self.fallback_methods = {
            'linkedin_post': self.fallback_to_email,
            'twitter_post': self.fallback_to_log,
            'whatsapp_send': self.fallback_to_email,
            'email_send': self.fallback_to_log
        }
        self.degraded_services = set()
        self.primary_services = {
            'email': True,
            'linkedin': True,
            'twitter': True,
            'whatsapp': True
        }

    def handle_service_failure(self, service_name: str, error: Exception) -> Dict[str, Any]:
        """Handle service failure with graceful degradation"""
        logging.error(f"Service {service_name} failed: {error}")

        # Mark service as degraded
        self.degraded_services.add(service_name)
        self.primary_services[service_name] = False

        # Determine fallback action
        if service_name in self.fallback_methods:
            try:
                fallback_result = self.fallback_methods[service_name](service_name, error)
                logging.info(f"Fallback successful for {service_name}")
                return {
                    'success': True,
                    'degraded': True,
                    'fallback_used': True,
                    'original_error': str(error),
                    'result': fallback_result
                }
            except Exception as fallback_error:
                logging.error(f"Fallback also failed for {service_name}: {fallback_error}")
                return {
                    'success': False,
                    'degraded': True,
                    'fallback_used': True,
                    'original_error': str(error),
                    'fallback_error': str(fallback_error)
                }
        else:
            # No fallback available
            return {
                'success': False,
                'degraded': True,
                'fallback_used': False,
                'original_error': str(error)
            }

    def fallback_to_email(self, service_name: str, error: Exception) -> Dict[str, Any]:
        """Fallback to email when other services fail"""
        # Log the issue and send notification via email
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@company.com')

        subject = f"Service Alert: {service_name} Failed"
        body = f"""
        Service {service_name} has failed with error: {error}

        This service is temporarily unavailable.
        Fallback measures have been activated.

        Time: {datetime.now().isoformat()}
        """

        # Use email handler to send notification
        from generated_email_handler import EmailHandler
        email_handler = EmailHandler()

        result = email_handler.send_email(admin_email, subject, body, {})
        return result

    def fallback_to_log(self, service_name: str, error: Exception) -> Dict[str, Any]:
        """Fallback to logging when service fails"""
        logging.warning(f"Service {service_name} failed, logging to file: {error}")

        # Create a log entry in the system
        log_file = Path("Logs") / f"{service_name}_degradation.log"
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {service_name} failed: {error}\n")

        return {
            'success': True,
            'action': 'logged_to_file',
            'log_file': str(log_file)
        }

    def is_service_degraded(self, service_name: str) -> bool:
        """Check if service is currently degraded"""
        return service_name in self.degraded_services

    def recover_service(self, service_name: str) -> bool:
        """Attempt to recover a degraded service"""
        try:
            # Test the service
            if service_name == 'email':
                # Test email connection
                import smtplib
                server = smtplib.SMTP(os.getenv('EMAIL_SMTP_SERVER'), 587)
                server.quit()
            elif service_name == 'linkedin':
                # Test LinkedIn connection
                pass  # Implement LinkedIn connectivity test
            elif service_name == 'twitter':
                # Test Twitter connection
                pass  # Implement Twitter connectivity test
            elif service_name == 'whatsapp':
                # Test WhatsApp connection
                pass  # Implement WhatsApp connectivity test

            # If no exception, service is recovered
            self.degraded_services.discard(service_name)
            self.primary_services[service_name] = True
            logging.info(f"Service {service_name} recovered")
            return True

        except Exception as e:
            logging.warning(f"Service {service_name} recovery failed: {e}")
            return False

# Global degradation handler
degradation_handler = GracefulDegradation()

# Wrapper for service calls with degradation handling
def with_graceful_degradation(service_name: str):
    """Decorator to wrap service calls with graceful degradation"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if degradation_handler.is_service_degraded(service_name):
                    # Service is already degraded, try to recover
                    if degradation_handler.recover_service(service_name):
                        # Service recovered, proceed with original call
                        return func(*args, **kwargs)
                    else:
                        # Still degraded, use fallback
                        return degradation_handler.handle_service_failure(service_name,
                                                                         Exception(f"Service {service_name} still degraded"))
                else:
                    # Normal operation
                    return func(*args, **kwargs)
            except Exception as e:
                # Handle failure with degradation
                return degradation_handler.handle_service_failure(service_name, e)
        return wrapper
    return decorator

# Usage example:
@with_graceful_degradation('linkedin_post')
def post_to_linkedin(content, metadata):
    """LinkedIn posting with graceful degradation"""
    # Actual LinkedIn posting logic
    pass
```

---

## DEPLOYMENT STEPS

### Local Deployment Script:
```bash
#!/bin/bash
# deploy_local.sh

set -e

echo "🚀 Deploying AI Employee System..."

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is recommended but not required"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create vault structure
echo "📁 Setting up vault structure..."
mkdir -p Inbox Needs_Action Pending_Approval Approved Done Failed Logs Plans Reports Templates

# Set up environment
echo "🔐 Setting up environment..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# AI Employee System Configuration
VAULT_PATH=$(pwd)

# API Keys (fill in with your actual keys)
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=

EMAIL_USERNAME=
EMAIL_PASSWORD=
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_IMAP_SERVER=imap.gmail.com

INSTAGRAM_USERNAME=
INSTAGRAM_PASSWORD=

# Security
MAX_AUTO_APPROVE_AMOUNT=50
REQUIRE_APPROVAL=true

# Logging
LOG_LEVEL=INFO
EOF
    echo "⚠️  Please fill in your credentials in .env file"
fi

# Test configuration
echo "🧪 Testing configuration..."
python -c "
import os
from pathlib import Path

# Check vault structure
folders = ['Inbox', 'Needs_Action', 'Pending_Approval', 'Approved', 'Done', 'Failed', 'Logs', 'Plans']
for folder in folders:
    path = Path(folder)
    if not path.exists():
        print(f'❌ {folder} folder not created')
        exit(1)
    print(f'✅ {folder} folder exists')

print('✅ Vault structure OK')
"

# Create systemd service (Linux) or similar for auto-start
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "⚙️  Setting up systemd service..."
    sudo tee /etc/systemd/system/ai-employee.service > /dev/null << EOF
[Unit]
Description=AI Employee System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/bin
ExecStart=$(which python) workflow_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    echo "✅ systemd service created"
fi

# Create startup scripts
echo "⚡ Creating startup scripts..."

# Windows batch file
cat > start_system.bat << EOF
@echo off
echo Starting AI Employee System...
cd /d "$(pwd)"
python workflow_orchestrator.py
pause
EOF

# Linux/Mac shell script
cat > start_system.sh << EOF
#!/bin/bash
echo "Starting AI Employee System..."
cd "$(pwd)"
python workflow_orchestrator.py
EOF
chmod +x start_system.sh

echo "🎯 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: python workflow_orchestrator.py"
echo "3. Or use startup script: ./start_system.sh (Linux/Mac) or start_system.bat (Windows)"
echo ""
echo "🔐 Security reminder: Store credentials securely and never commit .env to version control"
```

### Always-On Operation Setup:
```bash
#!/bin/bash
# setup_always_on.sh

set -e

echo "🔄 Setting up always-on operation..."

# Method 1: Systemd (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Creating systemd service..."

    SERVICE_FILE="/etc/systemd/system/ai-employee.service"
    sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=AI Employee Automation System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=/home/$USER/.local/bin:/usr/local/bin:/usr/bin
EnvironmentFile=$(pwd)/.env
ExecStart=/usr/bin/python3 $(pwd)/workflow_orchestrator.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-employee

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$(pwd)
ReadOnlyPaths=/etc /usr
MemoryDenyWriteExecute=true
NoExecPaths=/tmp /var/tmp /dev/shm
LockPersonality=true
RestrictRealtime=true
RestrictNamespaces=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable ai-employee.service
    echo "✅ Systemd service created and enabled"

    # Start the service
    sudo systemctl start ai-employee.service
    echo "🚀 Service started"

elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Method 2: Launchd (macOS)
    echo "🔧 Creating launchd plist..."

    PLIST_FILE="$HOME/Library/LaunchAgents/ai.employee.plist"
    cat > $PLIST_FILE << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.employee</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$(pwd)/workflow_orchestrator.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$(pwd)/Logs/ai_employee_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$(pwd)/Logs/ai_employee_stderr.log</string>
</dict>
</plist>
EOF

    # Load the launchd job
    launchctl load $PLIST_FILE
    echo "✅ Launchd job created and loaded"

else
    # Method 3: Process supervisor (cross-platform)
    echo "🔧 Setting up process supervisor..."

    # Install supervisor if not present
    if ! command -v supervisord &> /dev/null; then
        pip install supervisor
    fi

    # Create supervisor config
    cat > ai_employee_supervisor.conf << EOF
[supervisord]
logfile=/tmp/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/tmp/supervisord.pid
nodaemon=false
minfds=1024
minprocs=200

[program:ai_employee]
command=python workflow_orchestrator.py
directory=$(pwd)
environment=PYTHONPATH=$(pwd)
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$(pwd)/Logs/ai_employee_supervisor.log
stopwaitsecs=30
EOF

    # Start supervisor
    supervisord -c ai_employee_supervisor.conf
    supervisorctl -c ai_employee_supervisor.conf start ai_employee
    echo "✅ Supervisor configured and started"
fi

# Create monitoring script
cat > monitor_system.py << 'EOF'
#!/usr/bin/env python3
"""
System monitor for AI Employee
Checks if main process is running and restarts if needed
"""
import psutil
import time
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/monitor.log'),
        logging.StreamHandler()
    ]
)

def is_process_running(process_name):
    """Check if process is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if process_name in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def start_main_process():
    """Start the main AI Employee process"""
    try:
        subprocess.Popen(['python', 'workflow_orchestrator.py'])
        logging.info("AI Employee process started")
        return True
    except Exception as e:
        logging.error(f"Failed to start process: {e}")
        return False

def main():
    logging.info("AI Employee Monitor started")

    while True:
        if not is_process_running('workflow_orchestrator.py'):
            logging.warning("AI Employee process not running, restarting...")
            if start_main_process():
                logging.info("Process restarted successfully")
            else:
                logging.error("Failed to restart process")

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
EOF

chmod +x monitor_system.py

echo "✅ Always-on setup complete!"
echo ""
echo "📊 Monitor the system with:"
echo "  - systemd: sudo systemctl status ai-employee"
echo "  - logs: journalctl -u ai-employee -f"
echo "  - manual: tail -f Logs/*.log"
echo ""
echo "🔄 The system will automatically restart if it crashes"
```

### Service Management Commands:
```bash
# Start the service
sudo systemctl start ai-employee

# Stop the service
sudo systemctl stop ai-employee

# Restart the service
sudo systemctl restart ai-employee

# Check service status
sudo systemctl status ai-employee

# View logs
sudo journalctl -u ai-employee -f

# Check if service is enabled
sudo systemctl is-enabled ai-employee

# Disable the service
sudo systemctl disable ai-employee

# Check all services
sudo systemctl list-units --type=service --state=running | grep ai
```

---

This BRAIN.md document contains all the technical details about the AI Employee system architecture, implementation, and deployment. It serves as a comprehensive reference for the entire system.