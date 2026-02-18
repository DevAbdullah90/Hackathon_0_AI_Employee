#!/usr/bin/env python3
"""
Email Watcher
Monitors email for business opportunities and important messages
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# Load env vars
load_dotenv()
# from generated_email_handler import EmailHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailWatcher:
    """Watches email for business opportunities and important messages"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_folder = self.vault_path / 'Logs'
        # self.email_handler = EmailHandler()

        # Initialize email monitoring
        self._initialize_monitoring()

    def _initialize_monitoring(self):
        """Initialize email monitoring system"""
        try:
            # Set up monitoring for email-related activities
            logger.info("Email watcher initialized")
        except Exception as e:
            logger.error(f"Error initializing email watcher: {e}")

    def check_needs_action_emails(self) -> List[Dict[str, Any]]:
        """Check for emails in Needs_Action folder that need processing"""
        emails = []

        try:
            # Look for email files in Needs_Action directory
            if not self.needs_action.exists():
                return emails

            for file in self.needs_action.glob("EMAIL_*.md"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract email information from the markdown file
                    lines = content.split('\n')
                    subject_line = None
                    sender_line = None
                    priority_line = None

                    for line in lines:
                        if line.startswith('**Subject**:'):
                            subject_line = line
                        elif line.startswith('**From**:') or line.startswith('**Sender**:'):
                            sender_line = line
                        elif line.startswith('**Priority**:'):
                            priority_line = line

                    # Extract information from the lines
                    subject = self._extract_value_from_line(subject_line) if subject_line else "Unknown Subject"
                    sender = self._extract_value_from_line(sender_line) if sender_line else "Unknown Sender"
                    priority = self._extract_value_from_line(priority_line) if priority_line else "medium"

                    emails.append({
                        'platform': 'email',
                        'type': 'needs_action_email',
                        'sender': sender,
                        'subject': subject,
                        'timestamp': datetime.now().isoformat(),  # Use current time as approximation
                        'filename': str(file),
                        'priority': priority,
                        'status': 'needs_attention'
                    })
                except Exception as e:
                    logger.error(f"Error reading email file {file}: {e}")

            logger.info(f"Found {len(emails)} emails in Needs_Action folder")

        except Exception as e:
            logger.error(f"Error checking Needs_Action emails: {e}")

        return emails

    def check_new_incoming_emails(self) -> List[Dict[str, Any]]:
        """Check for new incoming emails using IMAP"""
        emails = []

        try:
            logger.info("Checking for new incoming emails...")
            
            username = os.getenv("EMAIL_USERNAME")
            password = os.getenv("EMAIL_PASSWORD")
            imap_server = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
            
            if not username or not password:
                logger.warning("Email credentials not set. Skipping check.")
                return []

            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(username, password)
            mail.select("inbox")
            
            # Search for unseen emails
            status, messages = mail.search(None, "UNSEEN")
            email_ids = messages[0].split()
            
            if not email_ids:
                logger.info("No new emails.")
                return []
                
            logger.info(f"Found {len(email_ids)} new emails. Processing last 10...")
            
            # Process new emails (limit to last 10 to avoid overload)
            recent_email_ids = email_ids[-10:] if len(email_ids) > 10 else email_ids
            
            for e_id in recent_email_ids:
                try:
                    status, msg_data = mail.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Decode subject
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")
                                
                            sender = msg.get("From")
                            
                            # Get body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode()
                                        except:
                                            pass
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode()
                                except:
                                    pass
                                    
                            priority = self._determine_priority(subject + " " + body)
                            
                            emails.append({
                                'platform': 'email',
                                'type': 'incoming_message',
                                'sender': sender,
                                'subject': subject,
                                'body': body[:500] + "..." if len(body) > 500 else body,
                                'timestamp': datetime.now().isoformat(),
                                'priority': priority
                            })
                            
                except Exception as e:
                    logger.error(f"Error processing email {e_id}: {e}")
                    
            mail.close()
            mail.logout()

        except Exception as e:
            logger.error(f"Error checking new incoming emails: {e}")

        return emails

    def search_business_opportunities(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Search for email business opportunities"""
        opportunities = []

        if not keywords:
            keywords = ['opportunity', 'business', 'meeting', 'collaboration',
                       'partnership', 'project', 'consultation', 'service', 'proposal']

        try:
            # Check emails in Needs_Action for business opportunities
            needs_action_emails = self.check_needs_action_emails()

            for email in needs_action_emails:
                subject = email.get('subject', '').lower()
                if any(keyword in subject for keyword in keywords):
                    opportunities.append({
                        'platform': 'email',
                        'type': 'business_opportunity',
                        'search_keyword': 'business opportunity',
                        'sender': email.get('sender'),
                        'subject': email.get('subject'),
                        'timestamp': email.get('timestamp'),
                        'priority': 'high'
                    })

            logger.info(f"Found {len(opportunities)} email business opportunities")

        except Exception as e:
            logger.error(f"Error searching email opportunities: {e}")

        return opportunities

    def _extract_value_from_line(self, line: str) -> str:
        """Extract value from a markdown line like '**Key**: value'"""
        if not line:
            return "Unknown"
        # Split on ': ' and take the second part
        parts = line.split(': ', 1)
        if len(parts) > 1:
            return parts[1].strip()
        return "Unknown"

    def _determine_priority(self, text: str) -> str:
        """Determine priority based on keywords"""
        text = text.lower()

        high_priority_keywords = ['urgent', 'asap', 'payment', 'invoice', 'problem',
                                 'issue', 'error', 'broken', 'help', 'need', 'looking',
                                 'recommend', 'quote', 'price', 'important']
        low_priority_keywords = ['thanks', 'thank you', 'great', 'awesome', 'love', 'hello']

        if any(keyword in text for keyword in high_priority_keywords):
            return 'high'
        elif any(keyword in text for keyword in low_priority_keywords):
            return 'low'
        else:
            return 'medium'

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create action file in Needs_Action folder"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            platform = item['platform']
            message_type = item['type']

            # Create filename with platform prefix
            filename = f"EMAIL_{timestamp}_{message_type.replace(' ', '_').replace('-', '_')}.md"
            filepath = self.needs_action / filename

            content = self._generate_email_content(item)
            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Created email action file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating email action file: {e}")
            return None

    def _generate_email_content(self, item: Dict[str, Any]) -> str:
        """Generate content for email action file"""
        platform = item['platform'].capitalize()
        message_type = item['type'].replace('_', ' ').title()

        content = f"""---
type: communication
platform: {platform}
message_type: {item['type']}
priority: {item['priority']}
received: {item.get('timestamp', datetime.now().isoformat())}
status: pending
---

## {platform} {message_type}

**Platform**: {platform}
**Type**: {message_type}
**Priority**: {item['priority']}
**Received**: {item.get('timestamp', datetime.now().isoformat())}

"""

        if item['type'] == 'needs_action_email':
            content += f"""## Email Details

**Sender**: {item.get('sender')}
**Subject**: {item.get('subject')}
**Status**: Needs Attention

## Suggested Actions
- [ ] Review email content
- [ ] Analyze for business relevance
- [ ] Process according to email handler guidelines
- [ ] Update status when completed
"""

        elif item['type'] == 'business_opportunity':
            content += f"""## Business Opportunity Details

**Sender**: {item.get('sender')}
**Subject**: {item.get('subject')}
**Opportunity Type**: Business Opportunity

## Suggested Actions
- [ ] Review opportunity details
- [ ] Assess business potential
- [ ] Determine follow-up strategy
- [ ] Schedule outreach if appropriate
"""

        elif item['type'] == 'incoming_message':
            content += f"""## Incoming Email Details

**Sender**: {item.get('sender')}
**Subject**: {item.get('subject')}
**Timestamp**: {item.get('timestamp')}

## Suggested Actions
- [ ] Read email in context
- [ ] Apply email handler analysis
- [ ] Process according to company policies
- [ ] Create follow-up task if needed
"""

        return content

    def run_continuous(self, check_interval: int = 300):
        """Run watcher continuously"""
        logger.info(f"Starting Email watcher (interval: {check_interval}s)")

        while True:
            try:
                # Check for email activity
                needs_action_emails = self.check_needs_action_emails()
                for email in needs_action_emails:
                    self.create_action_file(email)

                new_emails = self.check_new_incoming_emails()
                for email in new_emails:
                    self.create_action_file(email)

                # Check for business opportunities periodically
                if datetime.now().minute % 10 == 0:  # Every 10 minutes
                    opportunities = self.search_business_opportunities()
                    for opportunity in opportunities:
                        self.create_action_file(opportunity)

                logger.info("Email check complete, sleeping...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Email watcher stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in Email watcher: {e}")
                time.sleep(60)

    def run_once(self):
        """Run a single check"""
        try:
            logger.info("Running Email check")

            all_items = []

            # Check for emails in Needs_Action
            needs_action_emails = self.check_needs_action_emails()
            all_items.extend(needs_action_emails)

            # Check for new incoming emails
            new_emails = self.check_new_incoming_emails()
            all_items.extend(new_emails)

            # Check for business opportunities occasionally
            last_opportunity_check = self.vault_path / '.last_email_opportunity_check'
            should_check_opportunities = True

            if last_opportunity_check.exists():
                last_time = datetime.fromtimestamp(last_opportunity_check.stat().st_mtime)
                if (datetime.now() - last_time).seconds < 1800:  # Check every 30 min
                    should_check_opportunities = False

            if should_check_opportunities:
                opportunities = self.search_business_opportunities()
                all_items.extend(opportunities)
                last_opportunity_check.touch()

            files_created = []
            for item in all_items:
                filepath = self.create_action_file(item)
                if filepath:
                    files_created.append(str(filepath))

            logger.info(f"Created {len(files_created)} email action files")
            return files_created

        except Exception as e:
            logger.error(f"Error in Email run_once: {e}")
            return []


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Email Watcher')
    parser.add_argument('--vault', type=str, help='Path to vault', default=None)
    parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    vault_path = args.vault or os.getcwd()

    watcher = EmailWatcher(vault_path)

    if args.once:
        result = watcher.run_once()
        print(json.dumps(result, indent=2))
    else:
        watcher.run_continuous()


if __name__ == "__main__":
    main()