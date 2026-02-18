#!/usr/bin/env python3
"""
Draft Generator - AI-powered draft generation for emails, WhatsApp, LinkedIn, and Twitter
Watches Needs_Action folder and generates draft replies/posts for human approval
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Installing watchdog...")
    os.system("pip install watchdog")
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

try:
    import yaml
except ImportError:
    print("Installing pyyaml...")
    os.system("pip install pyyaml")
    import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/draft_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DraftGenerator:
    """Generates draft content for various platforms"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.needs_action_folder = vault_path / 'Needs_Action'
        self.pending_approval_folder = vault_path / 'Pending_Approval'
        self.templates_folder = vault_path / 'Templates'
        self.skills_folder = vault_path / 'Skills'

        # Ensure directories exist
        self.pending_approval_folder.mkdir(exist_ok=True)
        (self.pending_approval_folder / 'Emails').mkdir(exist_ok=True)
        (self.pending_approval_folder / 'WhatsApp').mkdir(exist_ok=True)
        (self.pending_approval_folder / 'LinkedIn').mkdir(exist_ok=True)
        (self.pending_approval_folder / 'Twitter').mkdir(exist_ok=True)

        # Load templates and context
        self._load_company_context()

    def _load_company_context(self):
        """Load company handbook and context for drafts"""
        self.company_context = ""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            self.company_context = handbook_path.read_text(encoding='utf-8')[:2000]

    def generate_email_draft(
        self,
        original_email: Dict[str, Any],
        source_file: Path
    ) -> Dict[str, Any]:
        """
        Generate an email reply draft

        Args:
            original_email: Original email details (from, subject, body)
            source_file: Source file path

        Returns:
            Draft generation result
        """
        try:
            sender = original_email.get('from', 'Unknown')
            subject = original_email.get('subject', 'No Subject')
            body = original_email.get('body', '')

            # Determine email type and generate appropriate response
            email_type = self._classify_email(subject, body)
            draft_body = self._generate_email_response(email_type, sender, subject, body)

            # Create draft file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_filename = f"EMAIL_REPLY_DRAFT_{timestamp}.md"
            draft_path = self.pending_approval_folder / 'Emails' / draft_filename

            draft_content = f"""---
type: email
to: {sender}
subject: Re: {subject}
original_file: {source_file.name}
status: pending_approval
created_at: {datetime.now().isoformat()}
email_type: {email_type}
---

# Email Reply Draft

**To:** {sender}
**Subject:** Re: {subject}

## Original Message Summary
{body[:500]}...

## Draft Reply

{draft_body}

---

## Actions
- [ ] Review and edit draft
- [x] Approve (move to Approved folder to send)
- [ ] Reject

## Notes
- Generated automatically based on email type: {email_type}
- Please review and personalize before approving
"""

            draft_path.write_text(draft_content, encoding='utf-8')
            logger.info(f"Email draft created: {draft_path.name}")

            return {
                "success": True,
                "draft_file": str(draft_path),
                "email_type": email_type
            }

        except Exception as e:
            logger.error(f"Failed to generate email draft: {e}")
            return {"success": False, "error": str(e)}

    def _classify_email(self, subject: str, body: str) -> str:
        """Classify email type for response generation"""
        subject_lower = subject.lower()
        body_lower = body.lower()

        if any(word in subject_lower for word in ['invoice', 'payment', 'bill']):
            return 'invoice'
        elif any(word in subject_lower for word in ['urgent', 'asap', 'immediately']):
            return 'urgent'
        elif any(word in subject_lower for word in ['meeting', 'schedule', 'calendar']):
            return 'meeting'
        elif any(word in subject_lower for word in ['job', 'opportunity', 'position', 'hiring']):
            return 'job_opportunity'
        elif any(word in subject_lower for word in ['question', 'help', 'support', 'issue']):
            return 'support'
        elif any(word in subject_lower for word in ['newsletter', 'update', 'announcement']):
            return 'newsletter'
        else:
            return 'general'

    def _generate_email_response(
        self,
        email_type: str,
        sender: str,
        subject: str,
        body: str
    ) -> str:
        """Generate appropriate email response based on type"""

        templates = {
            'invoice': """Thank you for sending the invoice.

I have received your invoice regarding {subject} and will review it promptly.

If everything is in order, I will process the payment according to our standard terms.

Please let me know if you need any additional information from my end.

Best regards""",

            'urgent': """Thank you for bringing this to my attention.

I understand the urgency of this matter and will prioritize it accordingly.

I will review the details and get back to you as soon as possible with an update or resolution.

Best regards""",

            'meeting': """Thank you for reaching out about scheduling a meeting.

I would be happy to meet and discuss this further. Please let me know your availability, and I will do my best to accommodate.

Alternatively, you can check my calendar availability and book a time that works for both of us.

Best regards""",

            'job_opportunity': """Thank you for reaching out regarding this opportunity.

I appreciate you thinking of me for this position. I am [interested/not currently looking for new opportunities].

[If interested: I would be happy to discuss this further and learn more about the role.]

Best regards""",

            'support': """Thank you for reaching out.

I have received your inquiry and will look into this matter. I will provide you with more information or a resolution as soon as possible.

If you have any additional details that might help, please feel free to share them.

Best regards""",

            'newsletter': """Thank you for the update.

I have received and noted the information shared.

Best regards""",

            'general': """Thank you for your email.

I have received your message and will review it carefully. I will get back to you with a response as soon as possible.

Best regards"""
        }

        template = templates.get(email_type, templates['general'])
        return template.format(subject=subject, sender=sender)

    def generate_whatsapp_draft(
        self,
        original_message: Dict[str, Any],
        source_file: Path
    ) -> Dict[str, Any]:
        """
        Generate a WhatsApp reply draft

        Args:
            original_message: Original message details
            source_file: Source file path

        Returns:
            Draft generation result
        """
        try:
            sender = original_message.get('from', 'Unknown')
            phone = original_message.get('phone', '')
            message = original_message.get('message', '')

            # Generate reply based on message content
            reply = self._generate_whatsapp_reply(message)

            # Create draft file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_filename = f"WHATSAPP_REPLY_DRAFT_{timestamp}.md"
            draft_path = self.pending_approval_folder / 'WhatsApp' / draft_filename

            draft_content = f"""---
type: whatsapp
phone: {phone}
to: {sender}
original_file: {source_file.name}
status: pending_approval
created_at: {datetime.now().isoformat()}
---

# WhatsApp Reply Draft

**To:** {sender}
**Phone:** {phone}

## Original Message
{message}

## Draft Reply

{reply}

---

## Actions
- [ ] Review and edit draft
- [x] Approve (move to Approved folder to send)
- [ ] Reject
"""

            draft_path.write_text(draft_content, encoding='utf-8')
            logger.info(f"WhatsApp draft created: {draft_path.name}")

            return {
                "success": True,
                "draft_file": str(draft_path)
            }

        except Exception as e:
            logger.error(f"Failed to generate WhatsApp draft: {e}")
            return {"success": False, "error": str(e)}

    def _generate_whatsapp_reply(self, message: str) -> str:
        """Generate WhatsApp reply based on message content"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['urgent', 'asap', 'emergency']):
            return "Hi! I've received your urgent message. I'm looking into this right now and will get back to you shortly."
        elif any(word in message_lower for word in ['invoice', 'payment', 'bill']):
            return "Hi! Thanks for the update. I've noted this and will process it accordingly. Let me know if you need anything else."
        elif any(word in message_lower for word in ['meeting', 'call', 'schedule']):
            return "Hi! Thanks for reaching out. I'm available for a call/meeting. Please let me know your preferred time and I'll confirm."
        elif any(word in message_lower for word in ['thanks', 'thank you']):
            return "You're welcome! Let me know if there's anything else I can help with."
        elif '?' in message:
            return "Hi! Thanks for your question. Let me look into this and get back to you with the information you need."
        else:
            return "Hi! Thanks for your message. I've noted this and will respond with more details soon."

    def generate_linkedin_post_draft(
        self,
        topic: str,
        context: str = None,
        post_type: str = 'thought_leadership'
    ) -> Dict[str, Any]:
        """
        Generate a LinkedIn post draft

        Args:
            topic: Topic or theme for the post
            context: Additional context
            post_type: Type of post (thought_leadership, announcement, engagement)

        Returns:
            Draft generation result
        """
        try:
            # Generate post content
            post_content = self._generate_linkedin_post(topic, post_type, context)

            # Create draft file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_filename = f"LINKEDIN_POST_DRAFT_{timestamp}.md"
            draft_path = self.pending_approval_folder / 'LinkedIn' / draft_filename

            draft_content = f"""---
type: linkedin_post
topic: {topic}
post_type: {post_type}
status: pending_approval
created_at: {datetime.now().isoformat()}
---

# LinkedIn Post Draft

**Topic:** {topic}
**Type:** {post_type}

## Post Content

{post_content}

---

## Actions
- [ ] Review and edit content
- [x] Approve (move to Approved folder to post)
- [ ] Reject

## Tips
- Keep it authentic and professional
- Add relevant hashtags
- Consider adding an image for better engagement
"""

            draft_path.write_text(draft_content, encoding='utf-8')
            logger.info(f"LinkedIn draft created: {draft_path.name}")

            return {
                "success": True,
                "draft_file": str(draft_path)
            }

        except Exception as e:
            logger.error(f"Failed to generate LinkedIn draft: {e}")
            return {"success": False, "error": str(e)}

    def _generate_linkedin_post(
        self,
        topic: str,
        post_type: str,
        context: str = None
    ) -> str:
        """Generate LinkedIn post content"""

        templates = {
            'thought_leadership': f"""I've been thinking about {topic} lately, and here's what I've learned:

The key insight is that success in this area comes down to [key point].

Three things that have worked for me:
1. [First insight]
2. [Second insight]
3. [Third insight]

What's your experience with {topic}? I'd love to hear your thoughts in the comments.

#ProfessionalDevelopment #Leadership #Growth""",

            'announcement': f"""Exciting news to share!

{topic}

This represents [significance/impact]. I'm grateful for [acknowledgment].

Looking forward to [future outlook].

#Announcement #News #Milestone""",

            'engagement': f"""Quick question for my network:

{topic}

I've been exploring this topic and would love to hear different perspectives.

Drop your thoughts below!

#Discussion #Community #Engagement""",

            'educational': f"""Here's a quick tip about {topic}:

[Main tip or insight]

Why this matters:
- [Reason 1]
- [Reason 2]

Try this approach and let me know how it works for you!

#Tips #Learning #ProfessionalGrowth"""
        }

        return templates.get(post_type, templates['thought_leadership'])

    def generate_twitter_draft(
        self,
        topic: str,
        tweet_type: str = 'insight'
    ) -> Dict[str, Any]:
        """
        Generate a Twitter/X post draft

        Args:
            topic: Topic for the tweet
            tweet_type: Type (insight, question, announcement)

        Returns:
            Draft generation result
        """
        try:
            tweet_content = self._generate_tweet(topic, tweet_type)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_filename = f"TWITTER_DRAFT_{timestamp}.md"
            draft_path = self.pending_approval_folder / 'Twitter' / draft_filename

            draft_content = f"""---
type: twitter_post
topic: {topic}
tweet_type: {tweet_type}
status: pending_approval
created_at: {datetime.now().isoformat()}
character_count: {len(tweet_content)}
---

# Twitter Post Draft

**Topic:** {topic}
**Type:** {tweet_type}
**Characters:** {len(tweet_content)}/280

## Tweet Content

{tweet_content}

---

## Actions
- [ ] Review (ensure under 280 characters)
- [x] Approve (move to Approved folder to tweet)
- [ ] Reject
"""

            draft_path.write_text(draft_content, encoding='utf-8')
            logger.info(f"Twitter draft created: {draft_path.name}")

            return {
                "success": True,
                "draft_file": str(draft_path),
                "character_count": len(tweet_content)
            }

        except Exception as e:
            logger.error(f"Failed to generate Twitter draft: {e}")
            return {"success": False, "error": str(e)}

    def _generate_tweet(self, topic: str, tweet_type: str) -> str:
        """Generate tweet content (max 280 chars)"""

        templates = {
            'insight': f"Key insight about {topic}: [Your insight here]\n\nWhat do you think?",
            'question': f"Question for my followers:\n\nHow do you approach {topic}?\n\nDrop your thoughts below!",
            'announcement': f"Exciting update!\n\n{topic}\n\nMore details coming soon...",
            'thread_start': f"Thread: Everything you need to know about {topic}\n\n1/",
        }

        tweet = templates.get(tweet_type, templates['insight'])

        # Ensure under 280 characters
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."

        return tweet

    def process_needs_action_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a file from Needs_Action and generate appropriate draft

        Args:
            file_path: Path to the file

        Returns:
            Processing result
        """
        try:
            content = file_path.read_text(encoding='utf-8')

            # Determine file type from name or content
            filename_lower = file_path.name.lower()

            if filename_lower.startswith('email') or 'email' in filename_lower:
                # Parse email content
                email_data = self._parse_email_file(content, file_path)
                return self.generate_email_draft(email_data, file_path)

            elif 'whatsapp' in filename_lower:
                # Parse WhatsApp content
                wa_data = self._parse_whatsapp_file(content, file_path)
                return self.generate_whatsapp_draft(wa_data, file_path)

            elif 'linkedin' in filename_lower:
                # Generate LinkedIn post
                return self.generate_linkedin_post_draft(
                    topic=self._extract_topic(content),
                    post_type='thought_leadership'
                )

            elif 'twitter' in filename_lower:
                # Generate Twitter post
                return self.generate_twitter_draft(
                    topic=self._extract_topic(content)
                )

            else:
                logger.info(f"Unknown file type: {file_path.name}")
                return {"success": False, "error": "Unknown file type"}

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {"success": False, "error": str(e)}

    def _parse_email_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse email file content"""
        # Try to extract from YAML frontmatter
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    content = parts[2]
                except:
                    pass

        # Extract from content
        from_match = re.search(r'From:\s*(.+)', content, re.IGNORECASE)
        subject_match = re.search(r'Subject:\s*(.+)', content, re.IGNORECASE)

        return {
            'from': metadata.get('from') or (from_match.group(1) if from_match else 'Unknown'),
            'subject': metadata.get('subject') or (subject_match.group(1) if subject_match else file_path.stem),
            'body': content[:1000]
        }

    def _parse_whatsapp_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse WhatsApp file content"""
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    content = parts[2]
                except:
                    pass

        return {
            'from': metadata.get('from', 'Unknown'),
            'phone': metadata.get('phone', ''),
            'message': content[:500]
        }

    def _extract_topic(self, content: str) -> str:
        """Extract topic from content"""
        # Get first meaningful line
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#') and not l.startswith('-')]
        return lines[0][:100] if lines else "General Update"


class NeedsActionHandler(FileSystemEventHandler):
    """Watches Needs_Action folder for new files"""

    def __init__(self, generator: DraftGenerator):
        self.generator = generator
        self.processed_files = set()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            file_path = Path(event.src_path)
            if str(file_path) not in self.processed_files:
                logger.info(f"New file detected: {file_path.name}")
                self.processed_files.add(str(file_path))
                time.sleep(1)  # Wait for file to be fully written
                self.generator.process_needs_action_file(file_path)


def main():
    """Main function - runs the draft generator"""
    logger.info("=" * 60)
    logger.info("DRAFT GENERATOR - AI-Powered Content Generation")
    logger.info("=" * 60)

    vault_path = Path(__file__).parent.resolve()
    needs_action_folder = vault_path / 'Needs_Action'

    needs_action_folder.mkdir(exist_ok=True)

    generator = DraftGenerator(vault_path)
    event_handler = NeedsActionHandler(generator)

    # Process existing files first
    logger.info("Processing existing files in Needs_Action...")
    for file_path in needs_action_folder.glob("*.md"):
        try:
            result = generator.process_needs_action_file(file_path)
            if result.get('success'):
                logger.info(f"Generated draft for: {file_path.name}")
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")

    # Start watching
    observer = Observer()
    observer.schedule(event_handler, str(needs_action_folder), recursive=False)
    observer.start()

    logger.info(f"Monitoring: {needs_action_folder}")
    logger.info("Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nShutting down Draft Generator...")
        observer.stop()
        observer.join()
        logger.info("Draft Generator stopped")


if __name__ == "__main__":
    main()
