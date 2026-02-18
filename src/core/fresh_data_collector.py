#!/usr/bin/env python3
"""
Fresh Data Collector - AI Employee System
==========================================
Collects fresh data from ALL platforms:
- Gmail (IMAP)
- Twitter (API)
- LinkedIn (check status)
- Instagram (check status)
- WhatsApp (check status)

Run this to get latest data from everywhere.
"""

import os
import sys
import json
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Setup
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'C:/Users/LENOVO X1 YOGA/OneDrive/Desktop/hakathone zero/AI_Employee_vault'))
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
INBOX = VAULT_PATH / "Inbox"
LOGS = VAULT_PATH / "Logs"

NEEDS_ACTION.mkdir(exist_ok=True)
INBOX.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# EMAIL COLLECTOR (Gmail IMAP)
# ============================================================

def fetch_gmail_emails(limit: int = 10) -> List[Dict]:
    """Fetch latest emails from Gmail using IMAP"""
    emails = []

    imap_server = os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com')
    imap_port = int(os.getenv('EMAIL_IMAP_PORT', 993))
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')

    if not username or not password:
        logger.error("Email credentials not configured")
        return emails

    try:
        logger.info(f"Connecting to {imap_server}...")
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(username, password)
        mail.select('INBOX')

        # Search for recent emails (last 3 days)
        date_since = (datetime.now() - timedelta(days=3)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{date_since}")')

        if status != 'OK':
            logger.error("Failed to search emails")
            return emails

        email_ids = messages[0].split()
        logger.info(f"Found {len(email_ids)} emails from last 3 days")

        # Get latest emails
        for email_id in email_ids[-limit:]:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Decode subject
                subject = ""
                if msg['Subject']:
                    decoded = decode_header(msg['Subject'])
                    subject = decoded[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(decoded[0][1] or 'utf-8', errors='ignore')

                # Get sender
                sender = msg['From'] or "Unknown"

                # Get date
                date_str = msg['Date'] or ""

                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                            except:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(msg.get_payload())

                emails.append({
                    'id': email_id.decode(),
                    'subject': subject,
                    'from': sender,
                    'date': date_str,
                    'body': body[:500] if body else "",
                    'priority': determine_priority(subject + " " + body)
                })

            except Exception as e:
                logger.error(f"Error processing email {email_id}: {e}")

        mail.logout()
        logger.info(f"Successfully fetched {len(emails)} emails")

    except Exception as e:
        logger.error(f"Gmail connection error: {e}")

    return emails

def determine_priority(text: str) -> str:
    """Determine email priority based on keywords"""
    text = text.lower()
    high_keywords = ['urgent', 'asap', 'important', 'action required', 'deadline', 'invoice', 'payment']
    if any(kw in text for kw in high_keywords):
        return 'high'
    return 'normal'

# ============================================================
# TWITTER COLLECTOR (API)
# ============================================================

def fetch_twitter_data() -> Dict[str, Any]:
    """Fetch Twitter mentions, DMs, and timeline"""
    result = {
        'connected': False,
        'username': None,
        'mentions': [],
        'timeline': [],
        'error': None
    }

    try:
        import tweepy

        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([api_key, api_secret, access_token, access_secret]):
            result['error'] = 'Twitter credentials not configured'
            return result

        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        # Get user info
        me = client.get_me()
        if me and me.data:
            result['connected'] = True
            result['username'] = me.data.username
            logger.info(f"Twitter connected as @{me.data.username}")

            # Get mentions
            try:
                mentions = client.get_users_mentions(
                    id=me.data.id,
                    max_results=10,
                    tweet_fields=['created_at', 'text', 'author_id']
                )
                if mentions and mentions.data:
                    for m in mentions.data:
                        result['mentions'].append({
                            'id': m.id,
                            'text': m.text,
                            'created_at': str(m.created_at) if m.created_at else None
                        })
                    logger.info(f"Found {len(result['mentions'])} Twitter mentions")
            except Exception as e:
                logger.warning(f"Could not fetch mentions: {e}")

            # Get home timeline (using v1.1 API)
            try:
                auth = tweepy.OAuthHandler(api_key, api_secret)
                auth.set_access_token(access_token, access_secret)
                api = tweepy.API(auth)

                timeline = api.home_timeline(count=10)
                for tweet in timeline:
                    result['timeline'].append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'user': tweet.user.screen_name,
                        'created_at': str(tweet.created_at)
                    })
                logger.info(f"Fetched {len(result['timeline'])} timeline tweets")
            except Exception as e:
                logger.warning(f"Could not fetch timeline: {e}")

    except ImportError:
        result['error'] = 'tweepy not installed'
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Twitter error: {e}")

    return result

# ============================================================
# LINKEDIN STATUS CHECK
# ============================================================

def check_linkedin_status() -> Dict[str, Any]:
    """Check LinkedIn session status"""
    result = {
        'session_exists': False,
        'cookies_exist': False,
        'needs_login': True
    }

    session_path = Path(os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
    cookies_path = Path(os.getenv('LINKEDIN_COOKIES_PATH', './linkedin_cookies.json'))

    result['session_exists'] = session_path.exists()
    result['cookies_exist'] = cookies_path.exists()

    if result['cookies_exist']:
        try:
            cookies = json.loads(cookies_path.read_text())
            # Check if LinkedIn cookies are present
            li_cookies = [c for c in cookies if 'linkedin.com' in c.get('domain', '')]
            if li_cookies:
                result['needs_login'] = False
                logger.info("LinkedIn: Session cookies found")
        except:
            pass

    if result['needs_login']:
        logger.warning("LinkedIn: Login required")

    return result

# ============================================================
# INSTAGRAM STATUS CHECK
# ============================================================

def check_instagram_status() -> Dict[str, Any]:
    """Check Instagram session status"""
    result = {
        'session_exists': False,
        'needs_login': True,
        'username': os.getenv('INSTAGRAM_USERNAME')
    }

    session_path = Path(os.getenv('INSTAGRAM_SESSION_PATH', './instagram_session'))
    result['session_exists'] = session_path.exists()

    if result['session_exists']:
        # Check if session has data
        session_files = list(session_path.glob('*'))
        if len(session_files) > 2:  # More than just basic files
            result['needs_login'] = False
            logger.info("Instagram: Session data found")

    if result['needs_login']:
        logger.warning("Instagram: Login required")

    return result

# ============================================================
# WHATSAPP STATUS CHECK
# ============================================================

def check_whatsapp_status() -> Dict[str, Any]:
    """Check WhatsApp session status"""
    result = {
        'session_exists': False,
        'needs_qr_scan': True
    }

    session_path = Path(os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'))
    result['session_exists'] = session_path.exists()

    if result['session_exists']:
        session_files = list(session_path.glob('*'))
        if len(session_files) > 5:  # Has session data
            result['needs_qr_scan'] = False
            logger.info("WhatsApp: Session data found")

    if result['needs_qr_scan']:
        logger.warning("WhatsApp: QR code scan required")

    return result

# ============================================================
# SAVE DATA TO NEEDS_ACTION
# ============================================================

def save_email_to_needs_action(email_data: Dict) -> Path:
    """Save email to Needs_Action folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"EMAIL_{timestamp}_{email_data['id']}.md"
    filepath = NEEDS_ACTION / filename

    content = f"""---
type: email
platform: gmail
priority: {email_data['priority']}
status: needs_action
fetched: {datetime.now().isoformat()}
---

# New Email

**From:** {email_data['from']}
**Subject:** {email_data['subject']}
**Date:** {email_data['date']}
**Priority:** {email_data['priority']}

## Content

{email_data['body']}

---
*Fetched by AI Employee*
"""

    filepath.write_text(content, encoding='utf-8')
    logger.info(f"Saved email: {filename}")
    return filepath

def save_twitter_mention_to_needs_action(mention: Dict) -> Path:
    """Save Twitter mention to Needs_Action folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"TWITTER_MENTION_{timestamp}_{mention['id']}.md"
    filepath = NEEDS_ACTION / filename

    content = f"""---
type: twitter_mention
platform: twitter
status: needs_action
fetched: {datetime.now().isoformat()}
---

# Twitter Mention

**Tweet ID:** {mention['id']}
**Date:** {mention.get('created_at', 'Unknown')}

## Content

{mention['text']}

---
*Fetched by AI Employee*
"""

    filepath.write_text(content, encoding='utf-8')
    logger.info(f"Saved Twitter mention: {filename}")
    return filepath

# ============================================================
# MAIN COLLECTOR
# ============================================================

def collect_all_fresh_data() -> Dict[str, Any]:
    """Collect fresh data from all platforms"""

    print("=" * 60)
    print("AI EMPLOYEE - FRESH DATA COLLECTOR")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {
        'timestamp': datetime.now().isoformat(),
        'email': {'status': 'pending', 'count': 0, 'saved': 0},
        'twitter': {'status': 'pending'},
        'linkedin': {'status': 'pending'},
        'instagram': {'status': 'pending'},
        'whatsapp': {'status': 'pending'}
    }

    # 1. FETCH EMAILS
    print("[EMAIL] FETCHING EMAILS...")
    print("-" * 40)
    emails = fetch_gmail_emails(limit=10)
    results['email']['count'] = len(emails)

    if emails:
        print(f"  Found {len(emails)} recent emails:")
        saved_count = 0
        for em in emails[:5]:  # Save top 5 to Needs_Action
            print(f"  - {em['subject'][:50]}... [{em['priority']}]")
            # Only save high priority or first 3
            if em['priority'] == 'high' or saved_count < 3:
                save_email_to_needs_action(em)
                saved_count += 1
        results['email']['saved'] = saved_count
        results['email']['status'] = 'success'
    else:
        print("  No new emails found")
        results['email']['status'] = 'no_data'

    # 2. FETCH TWITTER DATA
    print()
    print("[TWITTER] FETCHING TWITTER DATA...")
    print("-" * 40)
    twitter_data = fetch_twitter_data()
    results['twitter'] = twitter_data

    if twitter_data['connected']:
        print(f"  Connected as: @{twitter_data['username']}")
        print(f"  Mentions: {len(twitter_data['mentions'])}")
        print(f"  Timeline: {len(twitter_data['timeline'])} tweets")

        # Save mentions to Needs_Action
        for mention in twitter_data['mentions'][:3]:
            save_twitter_mention_to_needs_action(mention)
            print(f"  - Saved mention: {mention['text'][:50]}...")
    else:
        print(f"  Error: {twitter_data.get('error', 'Unknown')}")

    # 3. CHECK LINKEDIN
    print()
    print("[LINKEDIN] CHECKING LINKEDIN...")
    print("-" * 40)
    linkedin_status = check_linkedin_status()
    results['linkedin'] = linkedin_status

    if linkedin_status['needs_login']:
        print("  Status: LOGIN REQUIRED")
        print("  Run: python linkedin_poster.py --login")
    else:
        print("  Status: SESSION ACTIVE")

    # 4. CHECK INSTAGRAM
    print()
    print("[INSTAGRAM] CHECKING INSTAGRAM...")
    print("-" * 40)
    instagram_status = check_instagram_status()
    results['instagram'] = instagram_status

    if instagram_status['needs_login']:
        print(f"  Status: LOGIN REQUIRED")
        print(f"  Username: {instagram_status['username']}")
    else:
        print("  Status: SESSION ACTIVE")

    # 5. CHECK WHATSAPP
    print()
    print("[WHATSAPP] CHECKING WHATSAPP...")
    print("-" * 40)
    whatsapp_status = check_whatsapp_status()
    results['whatsapp'] = whatsapp_status

    if whatsapp_status['needs_qr_scan']:
        print("  Status: QR CODE SCAN REQUIRED")
    else:
        print("  Status: SESSION ACTIVE")

    # SUMMARY
    print()
    print("=" * 60)
    print("COLLECTION SUMMARY")
    print("=" * 60)
    print(f"  Emails fetched: {results['email']['count']}")
    print(f"  Emails saved to Needs_Action: {results['email']['saved']}")
    print(f"  Twitter connected: {results['twitter'].get('connected', False)}")
    print(f"  Twitter mentions: {len(results['twitter'].get('mentions', []))}")
    print(f"  LinkedIn ready: {not results['linkedin']['needs_login']}")
    print(f"  Instagram ready: {not results['instagram']['needs_login']}")
    print(f"  WhatsApp ready: {not results['whatsapp']['needs_qr_scan']}")
    print("=" * 60)

    # Save results to log
    log_file = LOGS / f"fresh_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved to: {log_file}")

    return results

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    collect_all_fresh_data()
