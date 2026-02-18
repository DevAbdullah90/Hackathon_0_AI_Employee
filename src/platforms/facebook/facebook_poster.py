#!/usr/bin/env python3
"""
Facebook Poster - Automated Facebook posting using Playwright
Posts content to Facebook with cookie-based authentication
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FacebookPoster:
    """Facebook Poster using Playwright automation"""

    def __init__(self):
        """Initialize Facebook Poster"""
        self.cookies_path = os.getenv('FACEBOOK_COOKIES_PATH', str(Path(__file__).parent / 'facebook_cookies.json'))
        self.session_path = os.getenv('FACEBOOK_SESSION_PATH', str(Path(__file__).parent / 'facebook_session'))
        self.email = os.getenv('FACEBOOK_EMAIL')
        self.password = os.getenv('FACEBOOK_PASSWORD')
        self.browser = None
        self.context = None
        self.page = None

        # Ensure directories exist
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

    async def _init_browser(self, headless: bool = False):
        """Initialize browser with persistent context"""
        try:
            # Check if already initialized and valid
            if self.context and self.page:
                return True

            from playwright.async_api import async_playwright

            self.playwright = await async_playwright().start()

            # Use persistent context for maintaining session
            self.context = await self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-notifications'
                ],
                viewport={'width': 1280, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

            # Load cookies if available
            await self._load_cookies()

            logger.info("Browser initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False

    async def _close_browser(self):
        """Close browser and save cookies"""
        try:
            # Save cookies before closing
            await self._save_cookies()

            if self.context:
                await self.context.close()
            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    async def _load_cookies(self):
        """Load saved cookies"""
        try:
            if Path(self.cookies_path).exists():
                with open(self.cookies_path, 'r') as f:
                    cookies = json.load(f)
                    if cookies:
                        await self.context.add_cookies(cookies)
                        logger.info("Loaded saved cookies")
        except Exception as e:
            logger.warning(f"Failed to load cookies: {e}")

    async def _save_cookies(self):
        """Save cookies to file"""
        try:
            cookies = await self.context.cookies()
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f, indent=2)
            logger.info("Saved cookies")
        except Exception as e:
            logger.warning(f"Failed to save cookies: {e}")

    async def _check_login_status(self) -> bool:
        """Check if logged into Facebook"""
        try:
            logger.info("Checking login status...")
            # Try to navigate specific URL that redirects if not logged in
            # But here we assume we are on some page.
            # If we are on login page, we are not logged in.
            
            # Check for common "logged in" elements
            # 1. Home link/icon
            home_link = await self.page.query_selector('a[aria-label="Home"]')
            if home_link: return True
            
            # 2. "What's on your mind"
            post_input = await self.page.query_selector('div[role="button"]:has-text("What\'s on your mind,")')
            if post_input: return True
            
            post_span = await self.page.query_selector('span:has-text("What\'s on your mind,")')
            if post_span: return True

            # 3. Profile link (often has user's name) - harder to detect generically
            # 4. Messenger icon
            messenger = await self.page.query_selector('div[aria-label="Messenger"]')
            if messenger: return True

            # If we are on the main page and not login page, assume logged in?
            # Safe to wait a bit
            await self.page.wait_for_timeout(2000)
            
            # Re-check URL
            if "facebook.com/login" in self.page.url:
                return False

            return False

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    async def login(self, email: str = None, password: str = None) -> bool:
        """Login to Facebook"""
        try:
            email = email or self.email
            password = password or self.password

            # 1. Check if already logged in (using cookies)
            logger.info("Navigating to Facebook to check session...")
            await self.page.goto('https://www.facebook.com/', wait_until='domcontentloaded')
            await self.page.wait_for_timeout(3000)

            if await self._check_login_status():
                logger.info("Already logged in to Facebook")
                await self._save_cookies()
                return True

            if not email or not password:
                logger.error("Facebook credentials not provided and not logged in")
                return False

            logger.info("Session expired or not found. Logging in...")
            await self.page.goto('https://www.facebook.com/login')
            await self.page.wait_for_timeout(2000)

            # Handle cookie banner if present
            try:
                cookie_btn = self.page.locator('button[title="Allow all cookies"], button:has-text("Allow access")').first
                if await cookie_btn.is_visible():
                    await cookie_btn.click()
                    await self.page.wait_for_timeout(1000)
            except:
                pass

            # Fill credentials
            await self.page.fill('#email', email)
            await self.page.fill('#pass', password)

            # Click login
            await self.page.click('#loginbutton, button[name="login"]')
            await self.page.wait_for_timeout(5000)

            # Check for "Save Browser" or 2FA
            # Ideally manual intervention needed for 2FA on first run
            
            if await self._check_login_status():
                logger.info("Facebook login successful")
                await self._save_cookies()
                return True

            logger.error("Facebook login failed")
            return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def post(self, content: str, image_path: str = None) -> Dict[str, Any]:
        """Post content to Facebook"""
        try:
            if not await self._init_browser():
                return {"success": False, "error": "Failed to initialize browser"}

            # Check if logged in
            if not await self._check_login_status():
                logger.warning("Not logged in, attempting login...")
                if not await self.login():
                    await self._close_browser()
                    return {"success": False, "error": "Not logged in to Facebook. Please login first (run manually for 2FA)."}

            # Go to home
            await self.page.goto('https://www.facebook.com/')
            await self.page.wait_for_timeout(5000)

            # Click "What's on your mind?"
            # This selector changes often, need robust finding
            logger.info("Looking for post input...")
            
            # Common selectors for the post creation flow
            try:
                # 1. Click the dummy input to open modal
                # Try multiple potential selectors
                post_input_selectors = [
                    'div[role="button"] span:has-text("What\'s on your mind,")',
                    'div[role="button"]:has-text("What\'s on your mind,")',
                    'span:has-text("What\'s on your mind,")',
                    'div[aria-label^="What\'s on your mind"]',
                    'div[role="button"]:has-text("Write something...")'
                ]
                
                post_input = None
                for selector in post_input_selectors:
                    try:
                        element = self.page.locator(selector).first
                        if await element.is_visible():
                            post_input = element
                            logger.info(f"Found post input with selector: {selector}")
                            break
                    except:
                        continue
                
                if not post_input:
                     logger.warning("Could not find standard post input, trying generic approach")
                     # Fallback: key press 'p' often opens post modal on Facebook
                     await self.page.keyboard.press('p')
                else:
                    await post_input.click()
                
                logger.info("Clicked post input, waiting for dialog...")
                await self.page.wait_for_timeout(2000)

                # 2. Type content in the actual editor dialog
                # Wait for the modal to appear explicitly
                try:
                    dialog = self.page.locator('div[role="dialog"]').first
                    await dialog.wait_for(state='visible', timeout=10000)
                    logger.info("Create Post dialog found")
                except:
                    logger.warning("Dialog not found, assuming inline or full page editor")
                    dialog = self.page

                # Find editor within dialog
                editor_selectors = [
                    'div[role="textbox"][contenteditable="true"]',
                    'div[aria-label^="What\'s on your mind"]'
                ]
                
                editor = None
                for selector in editor_selectors:
                    try:
                         element = dialog.locator(selector).first
                         if await element.is_visible():
                             editor = element
                             logger.info(f"Found editor with selector: {selector}")
                             break
                    except:
                        continue
                
                if editor:
                    await editor.click()
                    await self.page.wait_for_timeout(1000)
                    
                    # Check if "Add to your post" popped up (it steals focus)
                    # The screenshot showed this overlay
                    try:
                        overlay = self.page.locator('span:has-text("Add to your post")').first
                        if await overlay.is_visible():
                            logger.warning("Found 'Add to your post' overlay, closing it...")
                            # Click the back button or close button in the overlay
                            back_btn = self.page.locator('div[aria-label="Back"], div[role="button"][aria-label="Back"]').first
                            if await back_btn.is_visible():
                                await back_btn.click()
                            else:
                                # Try Escape
                                await self.page.keyboard.press('Escape')
                            await self.page.wait_for_timeout(1000)
                            # Re-click editor
                            await editor.click()
                    except:
                        pass

                    await self.page.keyboard.type(content)
                    await self.page.wait_for_timeout(2000)
                    
                    # Verify text was typed
                    try:
                        existing_text = await editor.inner_text()
                        if not content[:10] in existing_text: # Check first 10 chars
                           logger.warning(f"Text verification failed! Expected '{content[:10]}...', found '{existing_text[:20]}...'")
                           logger.info("Retrying text entry with clear first...")
                           
                           # Retry: Clear and type again
                           await editor.click()
                           await self.page.wait_for_timeout(500)
                           
                           # Select all and delete
                           await self.page.keyboard.press('Control+A')
                           await self.page.wait_for_timeout(200)
                           await self.page.keyboard.press('Backspace')
                           await self.page.wait_for_timeout(500)
                           
                           await self.page.keyboard.type(content)
                    except Exception as e:
                        logger.warning(f"Text verification error: {e}")

                else:
                    raise Exception("Could not find post editor text area")

            except Exception as e:
                logger.error(f"Failed to enter post content: {e}")
                await self._close_browser()
                return {"success": False, "error": f"Could not open post dialog: {e}"}

            # Add image if provided
            if image_path and Path(image_path).exists():
                try:
                    # Look for photo/video button in the Create Post modal
                    photo_btn = self.page.locator('div[aria-label="Photo/video"]').first
                    await photo_btn.click()
                    await self.page.wait_for_timeout(1000)

                    # Handle file upload
                    file_input = self.page.locator('input[type="file"]').last # Often hidden
                    await file_input.set_input_files(str(Path(image_path).absolute()))
                    await self.page.wait_for_timeout(5000) # Wait for upload

                except Exception as e:
                    logger.warning(f"Failed to add image: {e}")

            # Click Post button
            try:
                logger.info("Content filled, looking for Post button...")
                
                # Check for "Add to your post" overlay again before posting and close it if present
                # This often blocks the Post button or appears after clicking something else
                try:
                    add_to_post = self.page.locator('span:has-text("Add to your post")').first
                    if await add_to_post.is_visible():
                        logger.warning("Found 'Add to your post' overlay blocking view, attempting to go back...")
                        back_btn = self.page.locator('div[aria-label="Back"], div[role="button"][aria-label="Back"]').first
                        if await back_btn.is_visible():
                            await back_btn.click()
                            await self.page.wait_for_timeout(1500)
                except:
                    pass

                # Multiple selectors for the Post/Next button
                # Sometimes it says "Next" instead of "Post"
                post_btn_selectors = [
                    'div[aria-label="Post"]',
                    'div[role="button"]:has-text("Post")',
                    'div[aria-label="Next"]',
                    'div[role="button"]:has-text("Next")',
                    'span:has-text("Post")',
                    'span:has-text("Next")',
                    'button:has-text("Post")'
                ]
                
                post_btn = None
                for selector in post_btn_selectors:
                    try:
                        # Get all matches and filter for visible & enabled
                        elements = await self.page.locator(selector).all()
                        for el in elements:
                            if await el.is_visible():
                                # Avoid "Add to your post" buttons or "Boost post"
                                text = await el.inner_text()
                                if "Add to your post" in text or "Boost" in text:
                                    continue
                                    
                                # Check enablement
                                disabled = await el.get_attribute("aria-disabled")
                                if disabled != "true":
                                    post_btn = el
                                    logger.info(f"Found Post/Next button with selector: {selector} Text: '{text}'")
                                    break
                        if post_btn: break
                    except:
                        continue
                
                if not post_btn:
                    # Debug dump
                    # await self.page.screenshot(path="debug_no_post_btn.png")
                    raise Exception("Could not find enabled Post/Next button")

                # Double check enablement
                if await post_btn.get_attribute("aria-disabled") == "true":
                    logger.warning("Post button appears disabled, waiting a moment...")
                    await self.page.wait_for_timeout(2000)
                
                # Scroll into view
                await post_btn.scroll_into_view_if_needed()
                
                await post_btn.click()
                logger.info("Clicked Post/Next button, waiting for completion or next step...")
                
                # Loop to handle multi-step flows (Next -> Post or Post -> Post Settings -> Post)
                for _ in range(3):
                    await self.page.wait_for_timeout(2000)
                    
                    # Check for "Post settings" modal
                    try:
                        post_settings = self.page.locator('span:has-text("Post settings"), div[aria-label="Post settings"]').first
                        if await post_settings.is_visible():
                            logger.info("Found 'Post settings' modal")
                    except:
                        pass

                    # Look for a confirmation "Post" button
                    # likely blue, not "Boost post"
                    try:
                        final_btn_selectors = [
                            'div[aria-label="Post"]', 
                            'div[role="button"]:has-text("Post")',
                            'button:has-text("Post")'
                        ]
                        
                        final_btn = None
                        for sel in final_btn_selectors:
                            elements = await self.page.locator(sel).all()
                            for el in elements:
                                if await el.is_visible():
                                    text = await el.inner_text()
                                    if "Boost" in text: continue
                                    # Ensure it's not the disabled button we just clicked if it's still there
                                    # But usually the new one is in a new modal (high z-index)
                                    final_btn = el
                                    break
                            if final_btn: break
                        
                        if final_btn:
                            logger.info("Found valid final Post button, clicking...")
                            await final_btn.click()
                            await self.page.wait_for_timeout(3000)
                            continue # Check again just in case
                    except:
                        pass
                    
                    # If the post input is gone, we are likely done
                    # But we should rely on "Post created" checks or just wait
                
                await self.page.wait_for_timeout(5000) # Wait for posting to complete

            except Exception as e:
                logger.error(f"Failed to click post button: {e}")
                await self._close_browser()
                return {"success": False, "error": f"Could not submit post: {e}"}

            logger.info("Facebook post created successfully")
            await self._close_browser()

            return {
                "success": True,
                "platform": "facebook",
                "content_preview": content[:100],
                "has_image": image_path is not None,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Post creation failed: {e}")
            await self._close_browser()
            return {"success": False, "error": str(e)}

# Sync wrapper
def post_sync(content: str, image_path: str = None) -> Dict[str, Any]:
    poster = FacebookPoster()
    return asyncio.run(poster.post(content, image_path))

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Facebook Poster')
    parser.add_argument('action', choices=['login', 'post'])
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--image', help='Image path')
    
    args = parser.parse_args()
    
    poster = FacebookPoster()
    
    if args.action == 'login':
        asyncio.run(poster._init_browser(headless=False)) # Always headful for login
        asyncio.run(poster.login())
        asyncio.run(poster._close_browser())
    elif args.action == 'post':
        if not args.content:
            print("Content required")
            sys.exit(1)
        result = asyncio.run(poster.post(args.content, args.image))
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
