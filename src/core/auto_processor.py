#!/usr/bin/env python3
"""
Auto Processor - 24/7 File Monitoring System with Platform Posting
Watches the "Approved" folder and actually sends/posts content to platforms
"""

import os
import sys
import json
import time
import signal
import re
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
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
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Configure logging
log_dir = Path("Logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/auto_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PlatformPoster:
    """Handles actual posting to different platforms"""

    def __init__(self):
        self.vault_path = Path(os.getenv('VAULT_PATH', '.'))

    async def post_to_linkedin(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """Post content to LinkedIn using Playwright"""
        try:
            # Import LinkedIn poster
            sys.path.insert(0, str(self.vault_path))
            from src.platforms.linkedin.linkedin_poster import LinkedInPoster

            poster = LinkedInPoster()
            result = await poster.post(content)

            if not result.get('success'):
                logger.error(f"LinkedIn post failed: {result.get('error')}")
                return {
                    "success": False,
                    "platform": "linkedin",
                    "error": result.get('error')
                }

            logger.info(f"LinkedIn post successful: {result.get('post_id', 'N/A')}")
            return {
                "success": True,
                "platform": "linkedin",
                "post_id": result.get("post_id"),
                "url": result.get("url"),
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            logger.warning("LinkedIn poster not available, using fallback")
            return await self._linkedin_fallback(content, metadata)
        except Exception as e:
            logger.error(f"LinkedIn posting failed: {e}")
            return {"success": False, "platform": "linkedin", "error": str(e)}

    async def post_to_facebook(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """Post content to Facebook using Playwright"""
        try:
            # Import Facebook poster
            sys.path.insert(0, str(self.vault_path))
            from src.platforms.facebook.facebook_poster import FacebookPoster

            # Get image path from metadata
            image_path = metadata.get('image_path') or metadata.get('image') or metadata.get('media')

            # Convert to absolute path if relative
            if image_path:
                image_path_obj = Path(image_path)
                if not image_path_obj.is_absolute():
                    image_path_obj = self.vault_path / image_path
                
                if image_path_obj.exists():
                    image_path = str(image_path_obj)
                else:
                    logger.warning(f"Facebook image not found: {image_path_obj}")
                    image_path = None

            poster = FacebookPoster()
            result = await poster.post(content, image_path)

            if result.get('success'):
                logger.info(f"Facebook post successful")
                return result
            else:
                logger.error(f"Facebook post failed: {result.get('error')}")
                return result

        except ImportError:
             return {"success": False, "platform": "facebook", "error": "Facebook module not found"}
        except Exception as e:
            logger.error(f"Facebook posting failed: {e}")
            return {"success": False, "platform": "facebook", "error": str(e)}

    async def _linkedin_fallback(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """Fallback LinkedIn posting using direct Playwright"""
        try:
            from playwright.async_api import async_playwright

            cookies_path = os.getenv('LINKEDIN_COOKIES_PATH', 'linkedin_cookies.json')

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()

                # Load cookies if available
                if Path(cookies_path).exists():
                    with open(cookies_path, 'r') as f:
                        cookies = json.load(f)
                        await context.add_cookies(cookies)

                page = await context.new_page()
                await page.goto('https://www.linkedin.com/feed/')

                # Wait for page to load
                await page.wait_for_timeout(3000)

                # Click "Start a post" button
                await page.click('button.share-box-feed-entry__trigger')
                await page.wait_for_timeout(1000)

                # Type content
                editor = page.locator('.ql-editor')
                await editor.fill(content)
                await page.wait_for_timeout(500)

                # Click Post button
                await page.click('button.share-actions__primary-action')
                await page.wait_for_timeout(3000)

                # Save updated cookies
                cookies = await context.cookies()
                with open(cookies_path, 'w') as f:
                    json.dump(cookies, f)

                await browser.close()

                return {
                    "success": True,
                    "platform": "linkedin",
                    "method": "playwright",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"LinkedIn Playwright posting failed: {e}")
            return {"success": False, "platform": "linkedin", "error": str(e)}

    async def send_whatsapp(self, phone: str, message: str, metadata: Dict) -> Dict[str, Any]:
        """Send WhatsApp message using Playwright"""
        try:
            from playwright.async_api import async_playwright

            # Use absolute path for session
            project_root = self.vault_path
            session_path = os.getenv('WHATSAPP_SESSION_PATH', str(project_root / 'whatsapp_session_v2'))

            async with async_playwright() as p:
                browser = await p.chromium.launch_persistent_context(
                    session_path,
                    headless=False,
                    args=['--no-sandbox']
                )

                page = browser.pages[0] if browser.pages else await browser.new_page()

                # Format phone number (remove spaces, dashes)
                phone = str(phone)
                phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
                if not phone_clean.startswith('+'):
                    phone_clean = '+' + phone_clean

                # Navigate to WhatsApp Web with phone number
                url = f'https://web.whatsapp.com/send?phone={phone_clean}&text={message}'
                await page.goto(url)

                # Wait for chat to load
                await page.wait_for_timeout(5000)

                # Wait for send button and click
                try:
                    send_button = page.locator('button[aria-label="Send"]')
                    await send_button.wait_for(timeout=30000)
                    await send_button.click()
                    await page.wait_for_timeout(2000)

                    logger.info(f"WhatsApp message sent to {phone}")

                    await browser.close()

                    return {
                        "success": True,
                        "platform": "whatsapp",
                        "phone": phone,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"WhatsApp send button not found: {e}")
                    await browser.close()
                    return {"success": False, "platform": "whatsapp", "error": str(e)}

        except Exception as e:
            logger.error(f"WhatsApp sending failed: {e}")
            return {"success": False, "platform": "whatsapp", "error": str(e)}

    def post_to_twitter(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """Post tweet using Tweepy"""
        try:
            import tweepy

            # Get credentials from environment
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

            if not all([api_key, api_secret, access_token, access_token_secret]):
                raise ValueError("Twitter credentials not configured in .env")

            # Authenticate with Twitter API v2
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            # Truncate if too long
            if len(content) > 280:
                content = content[:277] + "..."

            # Post tweet
            response = client.create_tweet(text=content)
            tweet_id = response.data['id']

            logger.info(f"Tweet posted successfully: {tweet_id}")

            return {
                "success": True,
                "platform": "twitter",
                "tweet_id": tweet_id,
                "url": f"https://twitter.com/i/web/status/{tweet_id}",
                "timestamp": datetime.now().isoformat()
            }

        except ImportError:
            logger.error("Tweepy not installed. Run: pip install tweepy")
            return {"success": False, "platform": "twitter", "error": "Tweepy not installed"}
        except Exception as e:
            logger.error(f"Twitter posting failed: {e}")
            return {"success": False, "platform": "twitter", "error": str(e)}

    def send_email(self, to: str, subject: str, body: str, metadata: Dict) -> Dict[str, Any]:
        """Send email using SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Get SMTP credentials from environment
            smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
            username = os.getenv('EMAIL_USERNAME')
            password = os.getenv('EMAIL_PASSWORD')

            if not all([username, password]):
                raise ValueError("Email credentials not configured in .env")

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = username
            msg['To'] = to

            # Add body
            text_part = MIMEText(body, 'plain')
            html_part = MIMEText(f"<html><body>{body.replace(chr(10), '<br>')}</body></html>", 'html')
            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            logger.info(f"Email sent to {to}")

            return {
                "success": True,
                "platform": "email",
                "to": to,
                "subject": subject,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {"success": False, "platform": "email", "error": str(e)}

    async def post_to_instagram(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """Post content to Instagram using Playwright automation"""
        try:
            # Import Instagram poster
            sys.path.insert(0, str(self.vault_path))
            from src.platforms.instagram.instagram_playwright import InstagramPlaywright

            # Get image path from metadata
            image_path = metadata.get('image_path') or metadata.get('image') or metadata.get('media')

            if not image_path:
                logger.warning("No image path specified, checking for default images...")
                # Look for common image locations
                possible_paths = [
                    self.vault_path / 'images' / 'default_post.jpg',
                    self.vault_path / 'assets' / 'default_post.jpg',
                    self.vault_path / 'media' / 'default_post.jpg',
                ]
                for path in possible_paths:
                    if path.exists():
                        image_path = str(path)
                        break

                if not image_path:
                    return {
                        "success": False,
                        "platform": "instagram",
                        "error": "No image path specified in metadata. Add 'image_path' to the post file."
                    }

            # Convert to absolute path if relative
            image_path_obj = Path(image_path)
            if not image_path_obj.is_absolute():
                image_path_obj = self.vault_path / image_path

            if not image_path_obj.exists():
                return {
                    "success": False,
                    "platform": "instagram",
                    "error": f"Image file not found: {image_path_obj}"
                }

            # Extract caption from content
            caption = content

            # Initialize Instagram automation
            ig = InstagramPlaywright()

            # Post the image
            result = await ig.post_image(str(image_path_obj), caption)

            if result.get('success'):
                logger.info(f"Instagram post successful")
                return {
                    "success": True,
                    "platform": "instagram",
                    "image": str(image_path_obj),
                    "caption_preview": caption[:50] + "..." if len(caption) > 50 else caption,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return result

        except ImportError as e:
            logger.error(f"Instagram Playwright not available: {e}")
            return {"success": False, "platform": "instagram", "error": "Instagram Playwright module not found"}
        except Exception as e:
            logger.error(f"Instagram posting failed: {e}")
            return {"success": False, "platform": "instagram", "error": str(e)}

    async def post_instagram_story(self, metadata: Dict) -> Dict[str, Any]:
        """Post a story to Instagram"""
        try:
            sys.path.insert(0, str(self.vault_path))
            from src.platforms.instagram.instagram_playwright import InstagramPlaywright

            image_path = metadata.get('image_path') or metadata.get('image') or metadata.get('media')

            if not image_path:
                return {"success": False, "platform": "instagram_story", "error": "No image path specified"}

            image_path_obj = Path(image_path)
            if not image_path_obj.is_absolute():
                image_path_obj = self.vault_path / image_path

            if not image_path_obj.exists():
                return {"success": False, "platform": "instagram_story", "error": f"Image not found: {image_path_obj}"}

            ig = InstagramPlaywright()
            result = await ig.post_story(str(image_path_obj))

            if result.get('success'):
                logger.info("Instagram story posted successfully")
                return {
                    "success": True,
                    "platform": "instagram_story",
                    "image": str(image_path_obj),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Instagram story posting failed: {e}")
            return {"success": False, "platform": "instagram_story", "error": str(e)}


class ApprovedFileHandler(FileSystemEventHandler):
    """Handles file events in the Approved folder"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.approved_folder = vault_path / 'Approved'
        self.done_folder = vault_path / 'Done'
        self.failed_folder = vault_path / 'Failed'
        self.logs_folder = vault_path / 'Logs'
        self.dashboard_file = vault_path / 'Dashboard.md'
        self.poster = PlatformPoster()
        self.processed_files = set()

        # Ensure directories exist
        self.done_folder.mkdir(exist_ok=True)
        self.failed_folder.mkdir(exist_ok=True)
        self.logs_folder.mkdir(exist_ok=True)
        self.approved_folder.mkdir(exist_ok=True)

    def on_created(self, event):
        """Called when a file is created in the Approved folder"""
        if not event.is_directory and event.src_path.endswith('.md'):
            file_path = Path(event.src_path)
            if str(file_path) not in self.processed_files:
                logger.info(f"New file detected: {event.src_path}")
                self.processed_files.add(str(file_path))
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

    def extract_metadata(self, content: str) -> Dict[str, Any]:
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
        # Look for "## Post Content" or "## Message" sections
        patterns = [
            r'## Post Content\s*\n(.*?)(?=\n##|\Z)',
            r'## Message\s*\n(.*?)(?=\n##|\Z)',
            r'## Content\s*\n(.*?)(?=\n##|\Z)',
            r'## Tweet\s*\n(.*?)(?=\n##|\Z)',
            r'## Email Body\s*\n(.*?)(?=\n##|\Z)',
            r'## Caption\s*\n(.*?)(?=\n##|\n---|\Z)',  # Instagram caption
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()

        # If no specific section found, return content without headers
        lines = content.split('\n')
        clean_lines = [l for l in lines if not l.startswith('#') and not l.startswith('-')]
        return '\n'.join(clean_lines).strip()

    async def route_to_platform(self, file_type: str, content: str, metadata: Dict) -> Dict[str, Any]:
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
            'insta': 'instagram',
            'ig_post': 'instagram',
            'instagram_story': 'instagram_story',
            'ig_story': 'instagram_story',
            'insta_story': 'instagram_story',
            'facebook_post': 'facebook',
            'fb_post': 'facebook',
            'facebook': 'facebook',
            'fb': 'facebook',
        }

        platform = type_mapping.get(file_type, file_type)

        if platform == 'linkedin':
            return await self.poster.post_to_linkedin(content, metadata)

        elif platform == 'twitter':
            return self.poster.post_to_twitter(content, metadata)

        elif platform == 'whatsapp':
            phone = metadata.get('phone') or metadata.get('to') or metadata.get('recipient')
            if not phone:
                return {"success": False, "platform": "whatsapp", "error": "No phone number specified"}
            return await self.poster.send_whatsapp(phone, content, metadata)

        elif platform == 'email':
            to = metadata.get('to') or metadata.get('recipient')
            subject = metadata.get('subject', 'No Subject')
            if not to:
                return {"success": False, "platform": "email", "error": "No recipient specified"}
            return self.poster.send_email(to, subject, content, metadata)

        elif platform == 'instagram':
            return await self.poster.post_to_instagram(content, metadata)

        elif platform == 'instagram_story':
            return await self.poster.post_instagram_story(metadata)

        elif platform == 'facebook':
            return await self.poster.post_to_facebook(content, metadata)

        else:
            logger.warning(f"Unknown platform type: {file_type}. Processing as generic file.")
            return {
                "success": True,
                "platform": "generic",
                "note": "Processed without posting"
            }

    def create_log_entry(self, file_path: Path, metadata: Dict, result: Dict, success: bool):
        """Create a JSON log entry"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status = "success" if success else "failed"
        log_filename = f"{status}_{timestamp}_{file_path.stem}.json"
        log_path = self.logs_folder / log_filename

        log_entry = {
            'event_type': 'platform_post',
            'timestamp': datetime.now().isoformat(),
            'processor': 'auto_processor',
            'filename': file_path.name,
            'metadata': metadata,
            'result': result,
            'success': success
        }

        log_path.write_text(json.dumps(log_entry, indent=2, default=str))
        return log_path

    def move_to_done(self, file_path: Path) -> Path:
        """Move file to Done folder"""
        dest_path = self.done_folder / file_path.name
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = self.done_folder / f"{file_path.stem}_{timestamp}.md"
        file_path.rename(dest_path)
        return dest_path

    def move_to_failed(self, file_path: Path) -> Path:
        """Move file to Failed folder"""
        dest_path = self.failed_folder / file_path.name
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = self.failed_folder / f"{file_path.stem}_{timestamp}.md"
        if file_path.exists():
            file_path.rename(dest_path)
        return dest_path

    def update_dashboard(self, filename: str, metadata: Dict, result: Dict, success: bool):
        """Update Dashboard.md with processing result"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_icon = "" if success else ""
        platform = result.get('platform', 'unknown')

        entry = f"""

## {timestamp} - {status_icon} {platform.title()} {'Posted' if success else 'Failed'}

**File**: {filename}
**Platform**: {platform}
**Status**: {'Successfully posted' if success else 'Failed to post'}
**Type**: {metadata.get('type', 'unknown')}
{f"**Error**: {result.get('error')}" if not success else ""}
{f"**Post URL**: {result.get('url')}" if result.get('url') else ""}

---
"""
        try:
            with open(self.dashboard_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")

    def process_existing_files(self):
        """Process any existing files in Approved folder on startup"""
        logger.info("Checking for existing files in Approved folder...")

        existing_files = list(self.approved_folder.glob("*.md"))
        if not existing_files:
            logger.info("No existing files to process")
            return

        logger.info(f"Found {len(existing_files)} existing files to process")

        for file_path in existing_files:
            try:
                logger.info(f"Processing existing file: {file_path.name}")
                asyncio.run(self.process_file(file_path))
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing existing file {file_path.name}: {e}")


def main():
    """Main function - runs the auto processor"""
    logger.info("=" * 60)
    logger.info("AUTO PROCESSOR - Starting 24/7 Platform Poster")
    logger.info("=" * 60)

    # Set up vault path
    vault_path_env = os.getenv('VAULT_PATH')
    if vault_path_env:
        vault_path = Path(vault_path_env).resolve()
    else:
        # Assuming we are in src/core, go up 2 levels
        vault_path = Path(__file__).parents[2].resolve()
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

    # Graceful shutdown handler
    def signal_handler(sig, frame):
        logger.info("\nShutting down Auto Processor...")
        observer.stop()
        observer.join()
        logger.info("Auto Processor stopped gracefully")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start watching
    observer.start()
    logger.info(f"Started monitoring: {approved_folder}")
    logger.info("Watching for .md files in Approved folder")
    logger.info("Supported types: linkedin_post, twitter_post, whatsapp, email, instagram_post, instagram_story")
    logger.info("Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
