#!/usr/bin/env python3
"""
WhatsApp Poster
Posts messages to WhatsApp using Playwright and WhatsApp Web
"""

import os
import sys
import time
import json
import logging
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WhatsAppPoster:
    """WhatsApp automation using Playwright"""

    def __init__(self):
        # Use absolute paths relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        self.session_path = os.getenv('WHATSAPP_SESSION_PATH', str(project_root / 'whatsapp_session_v2'))
        self.browser = None
        self.context = None
        self.page = None
        
        # Create session directory if it doesn't exist
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

    def post_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Post a message to a specific phone number via WhatsApp Web
        
        Args:
            phone_number: Target phone number (with country code, no +)
            message: Message text to send
        """
        from playwright.sync_api import sync_playwright

        logger.info(f"Attempting to send WhatsApp message to {phone_number}")
        
        try:
            with sync_playwright() as p:
                # Launch persistent context
                # Headless is FALSE because we might need to scan QR code
                # and because WhatsApp Web often blocks headless browsers
                self.browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.session_path,
                    headless=False,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-blink-features=AutomationControlled'
                    ],
                    viewport={'width': 1280, 'height': 800}
                )
                
                self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
                
                # Encode message for URL
                encoded_msg = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_msg}"
                
                logger.info(f"Navigating to WhatsApp Web...")
                self.page.goto(url)
                
                # Wait for the main interface to load
                # We look for the send button or the chat list side panel
                # This wait might need to be long if the user needs to scan QR code
                logger.info("Waiting for WhatsApp to load (scan user QR code if needed)...")
                
                try:
                    # Wait for the chat to load by looking for the message input box or the extensive chat history
                    # This is more reliable than waiting for the send button directly
                    logger.info("Waiting for chat interface to be ready...")
                    
                    # Wait for message input box (common selectors)
                    # Use a broad enough selector to catch the input area
                    input_box_selector = 'div[contenteditable="true"][data-tab]'
                    self.page.wait_for_selector(input_box_selector, timeout=60000)
                    
                    logger.info("Chat loaded, input box found...")
                    
                    # Sometimes the pre-filled text needs a moment to register
                    time.sleep(2)
                    
                    # Focus the input box just in case
                    self.page.click(input_box_selector)
                    
                    # Check if Send button is visible
                    send_button_selector = 'span[data-icon="send"]'
                    if self.page.is_visible(send_button_selector):
                        logger.info("Clicking send button...")
                        self.page.click(send_button_selector)
                    else:
                        logger.info("Send button not found, pressing Enter...")
                        self.page.keyboard.press('Enter')
                        # Sometimes one Enter isn't enough if focus was lost, or it just focused the box
                        time.sleep(1)
                        self.page.keyboard.press('Enter')
                    
                    # Wait for message to be sent (check for single/double tick or just wait)
                    logger.info("Waiting for message to deliver...")
                    time.sleep(15)
                    
                    logger.info("Message sent successfully")
                    return {
                        "success": True,
                        "platform": "whatsapp",
                        "recipient": phone_number,
                        "status": "sent",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                except Exception as e:
                    # Capture screenshot for debugging
                    error_screenshot = os.path.join(self.session_path, f"error_{time.time()}.png")
                    self.page.screenshot(path=error_screenshot)
                    logger.info(f"Screenshot saved to {error_screenshot}")

                    # Check if it's because of login (timeout waiting for selector)
                    logger.error(f"Timeout or error waiting for chat to load: {e}")
                    
                    # Check if we are stuck on QR code screen
                    if self.page.query_selector('canvas'):
                        return {
                            "success": False,
                            "error": "WhatsApp Web requires QR code scan. Please run interactively first.",
                            "status": "needs_login"
                        }
                    
                    return {
                        "success": False,
                        "error": str(e)
                    }
                finally:
                    self.browser.close()

        except Exception as e:
            logger.error(f"WhatsApp automation failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Poster')
    parser.add_argument('--phone', required=True, help='Phone number with country code (e.g. 1234567890)')
    parser.add_argument('--message', required=True, help='Message to send')
    
    args = parser.parse_args()
    
    poster = WhatsAppPoster()
    result = poster.post_message(args.phone, args.message)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
