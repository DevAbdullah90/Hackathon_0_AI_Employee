#!/usr/bin/env python3
"""
Safe Platform Poster - Human-like Social Media Automation
=========================================================

This script safely posts to all platforms with:
- TEST_MODE flag for safe testing
- Human-like typing delays (80-200ms)
- Random waits between actions (3-8 seconds)
- Hover before click behavior
- No aggressive automation
- Single attempt per item (no loops/retries)
- Clear logging of SUCCESS/FAILED

Platforms supported:
- LinkedIn (Playwright)
- Instagram (Playwright)
- Twitter/X (API - Tweepy)
- WhatsApp (Playwright)
- Email (SMTP)

Author: AI Employee System
Version: 1.0.0
"""

import os
import sys
import json
import time
import random
import smtplib
import asyncio
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
import logging

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================
# CONFIGURATION
# ============================================================

TEST_MODE = True  # SET TO False FOR REAL POSTING

VAULT_PATH = Path(os.getenv('VAULT_PATH', 'C:/Users/LENOVO X1 YOGA/OneDrive/Desktop/hakathone zero/AI_Employee_vault'))
DONE_FOLDER = VAULT_PATH / "Done"
LOGS_FOLDER = VAULT_PATH / "Logs"
SENT_TEST_FOLDER = VAULT_PATH / "Sent_Test"

# Create folders
LOGS_FOLDER.mkdir(exist_ok=True)
SENT_TEST_FOLDER.mkdir(exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_FOLDER / 'safe_poster.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# HUMAN-LIKE BEHAVIOR UTILITIES
# ============================================================

def random_delay(min_sec: float = 3, max_sec: float = 8) -> float:
    """Random wait between actions (human-like)"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay

def typing_delay() -> int:
    """Random typing delay in ms (80-200ms per character)"""
    return random.randint(80, 200)

async def human_type(page, selector: str, text: str):
    """
    Type text with human-like delays.
    Uses page.type() with random delay per character.
    """
    element = page.locator(selector)
    await element.click()
    await page.wait_for_timeout(random.randint(300, 600))

    for char in text:
        await page.keyboard.type(char, delay=typing_delay())
        # Occasional longer pause (simulates thinking)
        if random.random() < 0.05:
            await page.wait_for_timeout(random.randint(200, 500))

async def hover_and_click(page, selector: str):
    """Hover over element before clicking (human-like)"""
    element = page.locator(selector)
    await element.hover()
    await page.wait_for_timeout(random.randint(300, 800))
    await element.click()

# ============================================================
# PLATFORM DETECTION
# ============================================================

def detect_platform(filename: str) -> str:
    """Detect platform from filename"""
    name = filename.upper()

    if 'LINKEDIN' in name or 'LI_POST' in name:
        return 'linkedin'
    elif 'INSTAGRAM' in name or 'IG_POST' in name:
        return 'instagram'
    elif 'TWITTER' in name or 'TW_POST' in name or 'TWEET' in name:
        return 'twitter'
    elif 'WHATSAPP' in name or 'WA_' in name:
        return 'whatsapp'
    elif 'EMAIL' in name or 'MAIL' in name:
        return 'email'
    elif 'FB_POST' in name or 'FACEBOOK' in name:
        return 'facebook'
    else:
        return 'unknown'

def extract_content(filepath: Path) -> Dict[str, Any]:
    """Extract content from markdown file"""
    try:
        content = filepath.read_text(encoding='utf-8')

        # Extract metadata if present (YAML frontmatter)
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    metadata = yaml.safe_load(parts[1]) or {}
                    content = parts[2].strip()
                except:
                    pass

        return {
            'content': content.strip(),
            'metadata': metadata,
            'filename': filepath.name,
            'platform': detect_platform(filepath.name)
        }
    except Exception as e:
        logger.error(f"Failed to read {filepath}: {e}")
        return None

# ============================================================
# LINKEDIN POSTER (Playwright - Safe)
# ============================================================

async def post_to_linkedin(content: str, metadata: Dict) -> Dict[str, Any]:
    """
    Post to LinkedIn using Playwright with human-like behavior.

    Safety features:
    - headless=False (visible browser)
    - Human-like typing delays
    - Random waits
    - Hover before click
    - No page.fill()
    """
    result = {
        'platform': 'linkedin',
        'status': 'FAILED',
        'timestamp': datetime.now().isoformat(),
        'test_mode': TEST_MODE
    }

    if TEST_MODE:
        logger.info(f"[TEST MODE] Would post to LinkedIn: {content[:100]}...")
        result['status'] = 'SUCCESS (TEST)'
        result['message'] = 'Test mode - no actual post'
        return result

    try:
        from playwright.async_api import async_playwright

        session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session')
        cookies_path = os.getenv('LINKEDIN_COOKIES_PATH', './linkedin_cookies.json')

        async with async_playwright() as p:
            # Launch visible browser
            context = await p.chromium.launch_persistent_context(
                session_path,
                headless=False,  # VISIBLE BROWSER
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ],
                viewport={'width': 1280, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = context.pages[0] if context.pages else await context.new_page()

            # Load cookies if available
            if Path(cookies_path).exists():
                with open(cookies_path, 'r') as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)

            # Navigate to LinkedIn feed
            await page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
            await page.wait_for_timeout(random.randint(3000, 5000))

            # Check if logged in
            login_check = await page.query_selector('.share-box-feed-entry__trigger')
            if not login_check:
                logger.error("Not logged into LinkedIn - please login manually first")
                result['error'] = 'Not logged in'
                await context.close()
                return result

            # Random wait (human-like)
            await page.wait_for_timeout(random.randint(2000, 4000))

            # Hover and click "Start a post"
            await hover_and_click(page, 'button.share-box-feed-entry__trigger')
            await page.wait_for_timeout(random.randint(1500, 2500))

            # Wait for editor to appear
            await page.wait_for_selector('.ql-editor', timeout=10000)
            await page.wait_for_timeout(random.randint(500, 1000))

            # Type content with human-like delays (NOT page.fill!)
            await human_type(page, '.ql-editor', content)

            # Random wait before posting
            await page.wait_for_timeout(random.randint(2000, 4000))

            # Hover and click Post button
            await hover_and_click(page, 'button.share-actions__primary-action')
            await page.wait_for_timeout(random.randint(3000, 5000))

            # Save cookies
            cookies = await context.cookies()
            with open(cookies_path, 'w') as f:
                json.dump(cookies, f, indent=2)

            await context.close()

            result['status'] = 'SUCCESS'
            result['message'] = 'Posted to LinkedIn'
            logger.info("LinkedIn post SUCCESS")

    except Exception as e:
        logger.error(f"LinkedIn post FAILED: {e}")
        result['error'] = str(e)

    return result

# ============================================================
# INSTAGRAM POSTER (Playwright - Safe)
# ============================================================

async def post_to_instagram(content: str, metadata: Dict) -> Dict[str, Any]:
    """
    Post to Instagram using Playwright with human-like behavior.
    Note: Instagram requires an image - this creates a text story or comment.
    For image posts, image_path must be provided in metadata.
    """
    result = {
        'platform': 'instagram',
        'status': 'FAILED',
        'timestamp': datetime.now().isoformat(),
        'test_mode': TEST_MODE
    }

    if TEST_MODE:
        logger.info(f"[TEST MODE] Would post to Instagram: {content[:100]}...")
        result['status'] = 'SUCCESS (TEST)'
        result['message'] = 'Test mode - no actual post'
        return result

    try:
        from playwright.async_api import async_playwright

        session_path = os.getenv('INSTAGRAM_SESSION_PATH', './instagram_session')

        async with async_playwright() as p:
            # Launch visible browser with mobile viewport
            context = await p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled'],
                viewport={'width': 430, 'height': 932},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
            )

            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto('https://www.instagram.com/', wait_until='domcontentloaded')
            await page.wait_for_timeout(random.randint(3000, 5000))

            # Check if logged in
            login_form = await page.query_selector('input[name="username"]')
            if login_form:
                logger.error("Not logged into Instagram - please login manually first")
                result['error'] = 'Not logged in'
                await context.close()
                return result

            # Instagram requires images for posts
            # For now, log that we need image support
            logger.warning("Instagram text-only posts not supported. Need image_path in metadata.")
            result['status'] = 'SKIPPED'
            result['message'] = 'Instagram requires image - text-only not supported'

            await context.close()

    except Exception as e:
        logger.error(f"Instagram post FAILED: {e}")
        result['error'] = str(e)

    return result

# ============================================================
# TWITTER POSTER (API - Tweepy)
# ============================================================

async def post_to_twitter(content: str, metadata: Dict) -> Dict[str, Any]:
    """
    Post to Twitter/X using Tweepy API.
    API-based posting (not Playwright).
    """
    result = {
        'platform': 'twitter',
        'status': 'FAILED',
        'timestamp': datetime.now().isoformat(),
        'test_mode': TEST_MODE
    }

    if TEST_MODE:
        logger.info(f"[TEST MODE] Would tweet: {content[:100]}...")
        result['status'] = 'SUCCESS (TEST)'
        result['message'] = 'Test mode - no actual tweet'
        return result

    try:
        import tweepy

        # Get credentials
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([api_key, api_secret, access_token, access_token_secret]):
            result['error'] = 'Twitter credentials not configured'
            return result

        # Initialize client
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Truncate to 280 characters
        tweet_text = content[:280] if len(content) > 280 else content

        # Post tweet
        response = client.create_tweet(text=tweet_text)

        result['status'] = 'SUCCESS'
        result['tweet_id'] = response.data['id']
        result['url'] = f"https://twitter.com/i/web/status/{response.data['id']}"
        logger.info(f"Twitter post SUCCESS: {result['url']}")

    except Exception as e:
        logger.error(f"Twitter post FAILED: {e}")
        result['error'] = str(e)

    return result

# ============================================================
# WHATSAPP SENDER (Playwright - Safe)
# ============================================================

async def send_whatsapp(content: str, metadata: Dict) -> Dict[str, Any]:
    """
    Send WhatsApp message using Playwright.
    Requires phone number in metadata or content.
    """
    result = {
        'platform': 'whatsapp',
        'status': 'FAILED',
        'timestamp': datetime.now().isoformat(),
        'test_mode': TEST_MODE
    }

    # Extract phone number
    phone = metadata.get('phone') or metadata.get('to')
    if not phone:
        # Try to extract from content
        import re
        phone_match = re.search(r'\+?\d{10,15}', content)
        if phone_match:
            phone = phone_match.group()

    if not phone:
        result['error'] = 'No phone number found'
        logger.error("WhatsApp: No phone number provided")
        return result

    if TEST_MODE:
        logger.info(f"[TEST MODE] Would send WhatsApp to {phone}: {content[:100]}...")
        result['status'] = 'SUCCESS (TEST)'
        result['message'] = 'Test mode - no actual message'
        return result

    try:
        from playwright.async_api import async_playwright

        session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                args=['--no-sandbox']
            )

            page = context.pages[0] if context.pages else await context.new_page()

            # Clean phone number
            phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
            if not phone_clean.startswith('+'):
                phone_clean = '+' + phone_clean

            # Navigate to WhatsApp Web
            await page.goto(f'https://web.whatsapp.com/send?phone={phone_clean}')
            await page.wait_for_timeout(random.randint(5000, 8000))

            # Check if QR code is needed
            qr_code = await page.query_selector('canvas[aria-label="Scan me!"]')
            if qr_code:
                logger.warning("WhatsApp QR code login required. Please scan with your phone.")
                result['error'] = 'QR code login required'
                await context.close()
                return result

            # Wait for message input
            try:
                msg_box = page.locator('[data-testid="conversation-compose-box-input"]')
                await msg_box.wait_for(timeout=30000)

                # Type message with human delays
                await msg_box.click()
                await page.wait_for_timeout(random.randint(500, 1000))

                for char in content:
                    await page.keyboard.type(char, delay=typing_delay())

                await page.wait_for_timeout(random.randint(1000, 2000))

                # Send
                send_btn = page.locator('[data-testid="send"]')
                await send_btn.hover()
                await page.wait_for_timeout(random.randint(300, 600))
                await send_btn.click()

                await page.wait_for_timeout(random.randint(2000, 3000))

                result['status'] = 'SUCCESS'
                result['phone'] = phone
                logger.info(f"WhatsApp message SUCCESS to {phone}")

            except Exception as e:
                result['error'] = f'Message send failed: {e}'

            await context.close()

    except Exception as e:
        logger.error(f"WhatsApp FAILED: {e}")
        result['error'] = str(e)

    return result

# ============================================================
# EMAIL SENDER (SMTP)
# ============================================================

async def send_email(content: str, metadata: Dict) -> Dict[str, Any]:
    """
    Send email using SMTP.
    Requires 'to' and 'subject' in metadata.
    """
    result = {
        'platform': 'email',
        'status': 'FAILED',
        'timestamp': datetime.now().isoformat(),
        'test_mode': TEST_MODE
    }

    to_addr = metadata.get('to') or metadata.get('email')
    subject = metadata.get('subject', 'Message from AI Employee')

    if not to_addr:
        result['error'] = 'No recipient email address'
        return result

    if TEST_MODE:
        logger.info(f"[TEST MODE] Would email to {to_addr}: {subject}")
        result['status'] = 'SUCCESS (TEST)'
        result['message'] = 'Test mode - no actual email'
        return result

    try:
        smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('EMAIL_SMTP_PORT', 587))
        username = os.getenv('EMAIL_USERNAME')
        password = os.getenv('EMAIL_PASSWORD')
        from_name = os.getenv('EMAIL_FROM_NAME', 'AI Employee')

        if not all([username, password]):
            result['error'] = 'Email credentials not configured'
            return result

        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{username}>"
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))

        # Send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

        result['status'] = 'SUCCESS'
        result['to'] = to_addr
        result['subject'] = subject
        logger.info(f"Email SUCCESS to {to_addr}")

    except Exception as e:
        logger.error(f"Email FAILED: {e}")
        result['error'] = str(e)

    return result

# ============================================================
# MAIN SCANNER AND PROCESSOR
# ============================================================

def scan_done_folder() -> Dict[str, List[Dict]]:
    """Scan Done folder and categorize by platform"""
    items = {
        'linkedin': [],
        'instagram': [],
        'twitter': [],
        'whatsapp': [],
        'email': [],
        'facebook': [],
        'unknown': []
    }

    for file in DONE_FOLDER.glob('*.md'):
        data = extract_content(file)
        if data:
            platform = data['platform']
            items[platform].append(data)

    return items

async def process_single_item(item: Dict) -> Dict[str, Any]:
    """
    Process a SINGLE item - attempt ONCE, no retries.
    """
    platform = item['platform']
    content = item['content']
    metadata = item.get('metadata', {})
    filename = item['filename']

    logger.info(f"Processing: {filename} ({platform})")

    result = None

    if platform == 'linkedin':
        result = await post_to_linkedin(content, metadata)
    elif platform == 'instagram':
        result = await post_to_instagram(content, metadata)
    elif platform == 'twitter':
        result = await post_to_twitter(content, metadata)
    elif platform == 'whatsapp':
        result = await send_whatsapp(content, metadata)
    elif platform == 'email':
        result = await send_email(content, metadata)
    elif platform == 'facebook':
        logger.warning(f"Facebook posting not implemented (needs API token)")
        result = {'platform': 'facebook', 'status': 'SKIPPED', 'message': 'API not configured'}
    else:
        logger.warning(f"Unknown platform for {filename}")
        result = {'platform': 'unknown', 'status': 'SKIPPED'}

    result['filename'] = filename

    # Log result
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        'platform': platform,
        'status': result.get('status', 'UNKNOWN'),
        'test_mode': TEST_MODE
    }

    log_file = LOGS_FOLDER / f"post_results_{datetime.now().strftime('%Y%m%d')}.json"
    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
        except:
            logs = []
    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2))

    # Move to Sent_Test folder if successful
    if 'SUCCESS' in result.get('status', ''):
        source = DONE_FOLDER / filename
        dest = SENT_TEST_FOLDER / f"SENT_TEST_{filename}"
        if source.exists():
            try:
                dest.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
                logger.info(f"Marked as SENT_TEST: {filename}")
            except:
                pass

    return result

async def run_test_posting():
    """
    Main function to scan and process items.
    Each item is processed ONCE with no retries.
    """
    print("=" * 60)
    print("SAFE PLATFORM POSTER")
    print(f"TEST_MODE: {TEST_MODE}")
    print("=" * 60)

    # Scan Done folder
    items = scan_done_folder()

    # Print summary
    print("\n📁 DONE FOLDER CONTENTS:")
    print("-" * 40)
    for platform, files in items.items():
        if files:
            print(f"  {platform.upper()}: {len(files)} items")

    print("\n🚀 PROCESSING (One attempt per item):")
    print("-" * 40)

    results = []

    # Process each platform (one item each for testing)
    for platform, files in items.items():
        if files and platform != 'unknown':
            # Take first item only for test
            item = files[0]
            result = await process_single_item(item)
            results.append(result)

            # Log
            status_icon = "✅" if 'SUCCESS' in result.get('status', '') else "❌"
            print(f"  {status_icon} {item['filename']}: {result.get('status', 'UNKNOWN')}")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY:")
    print("-" * 40)

    success = sum(1 for r in results if 'SUCCESS' in r.get('status', ''))
    failed = sum(1 for r in results if r.get('status') == 'FAILED')
    skipped = sum(1 for r in results if r.get('status') == 'SKIPPED')

    print(f"  SUCCESS: {success}")
    print(f"  FAILED:  {failed}")
    print(f"  SKIPPED: {skipped}")
    print("=" * 60)

    return results


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("\n🔒 Safe Platform Poster v1.0")
    print(f"📂 Vault: {VAULT_PATH}")
    print(f"🧪 Test Mode: {TEST_MODE}")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        TEST_MODE = False
        print("⚠️  LIVE MODE ENABLED - Real posts will be made!")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)

    asyncio.run(run_test_posting())
