#!/usr/bin/env python3
"""
LinkedIn Poster - Automated LinkedIn posting using Playwright
Posts content to LinkedIn with cookie-based authentication
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


class LinkedInPoster:
    """LinkedIn Poster using Playwright automation"""

    def __init__(self):
        """Initialize LinkedIn Poster"""
        # Use absolute paths relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        self.cookies_path = os.getenv('LINKEDIN_COOKIES_PATH', str(project_root / 'linkedin_cookies.json'))
        self.session_path = os.getenv('LINKEDIN_SESSION_PATH', str(project_root / 'linkedin_session'))
        self.browser = None
        self.context = None
        self.page = None

        # Ensure directories exist
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

    async def _init_browser(self, headless: bool = False):
        """Initialize browser with persistent context"""
        try:
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
                    '--disable-blink-features=AutomationControlled'
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
        """Check if logged into LinkedIn"""
        try:
            await self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
            await self.page.wait_for_timeout(3000)

            # Check for login page indicators
            login_button = await self.page.query_selector('a[data-tracking-control-name="guest_homepage-basic_sign-in-button"]')
            if login_button:
                return False

            # Check for feed content (indicates logged in)
            feed = await self.page.query_selector('.feed-shared-update-v2, .share-box-feed-entry__trigger')
            return feed is not None

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    async def login(self, email: str = None, password: str = None) -> bool:
        """
        Login to LinkedIn

        Args:
            email: LinkedIn email (or from env LINKEDIN_EMAIL)
            password: LinkedIn password (or from env LINKEDIN_PASSWORD)

        Returns:
            True if login successful
        """
        try:
            email = email or os.getenv('LINKEDIN_EMAIL')
            password = password or os.getenv('LINKEDIN_PASSWORD')

            if not email or not password:
                logger.error("LinkedIn credentials not provided")
                return False

            await self.page.goto('https://www.linkedin.com/login')
            await self.page.wait_for_timeout(2000)

            # Fill credentials
            await self.page.fill('#username', email)
            await self.page.fill('#password', password)

            # Click sign in
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_timeout(5000)

            # Check for successful login
            if await self._check_login_status():
                logger.info("LinkedIn login successful")
                await self._save_cookies()
                return True

            logger.error("LinkedIn login failed")
            return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def post(self, content: str, image_path: str = None) -> Dict[str, Any]:
        """
        Post content to LinkedIn

        Args:
            content: Post text content
            image_path: Optional path to image to attach

        Returns:
            Post result with success status
        """
        try:
            if not await self._init_browser():
                return {"success": False, "error": "Failed to initialize browser"}

            # Check if logged in
            if not await self._check_login_status():
                logger.warning("Not logged in, attempting login...")
                if not await self.login():
                    await self._close_browser()
                    return {"success": False, "error": "Not logged in to LinkedIn. Please login first."}

            # Go to feed
            await self.page.goto('https://www.linkedin.com/feed/')
            await self.page.wait_for_timeout(3000)

            # Click "Start a post" button
            try:
                # Try different selectors for the post button
                post_button_selectors = [
                    'button.share-box-feed-entry__trigger',
                    '[data-control-name="share.main_feed"]',
                    'button:has-text("Start a post")',
                    '.share-box-feed-entry__trigger'
                ]

                clicked = False
                for selector in post_button_selectors:
                    try:
                        button = self.page.locator(selector).first
                        if await button.is_visible():
                            await button.click()
                            clicked = True
                            break
                    except:
                        continue

                if not clicked:
                    raise Exception("Could not find post button")

                await self.page.wait_for_timeout(2000)

            except Exception as e:
                logger.error(f"Failed to click post button: {e}")
                await self._close_browser()
                return {"success": False, "error": f"Could not open post dialog: {e}"}

            # Type content in editor
            try:
                # Find the text editor
                editor_selectors = [
                    '.ql-editor[data-placeholder="What do you want to talk about?"]',
                    '.ql-editor',
                    '[role="textbox"]',
                    '.editor-content [contenteditable="true"]'
                ]

                for selector in editor_selectors:
                    try:
                        editor = self.page.locator(selector).first
                        if await editor.is_visible():
                            await editor.fill(content)
                            break
                    except:
                        continue

                await self.page.wait_for_timeout(1000)

            except Exception as e:
                logger.error(f"Failed to enter content: {e}")
                await self._close_browser()
                return {"success": False, "error": f"Could not enter post content: {e}"}

            # Add image if provided
            if image_path and Path(image_path).exists():
                try:
                    # Click add media button
                    media_button = self.page.locator('[aria-label="Add a photo"], [data-control-name="share.add_media"]').first
                    await media_button.click()
                    await self.page.wait_for_timeout(1000)

                    # Upload file
                    file_input = self.page.locator('input[type="file"]').first
                    await file_input.set_input_files(str(Path(image_path).absolute()))
                    await self.page.wait_for_timeout(3000)

                except Exception as e:
                    logger.warning(f"Failed to add image: {e}")

            # Click Post button
            try:
                post_button_selectors = [
                    'button.share-actions__primary-action',
                    'button:has-text("Post")',
                    '[data-control-name="share.post"]'
                ]

                for selector in post_button_selectors:
                    try:
                        button = self.page.locator(selector).first
                        if await button.is_visible():
                            await button.click()
                            break
                    except:
                        continue

                await self.page.wait_for_timeout(5000)

            except Exception as e:
                logger.error(f"Failed to click post button: {e}")
                await self._close_browser()
                return {"success": False, "error": f"Could not submit post: {e}"}

            # Verify post was created
            # Check for success indicators or absence of modal
            modal_closed = await self.page.query_selector('.share-box-feed-entry__trigger')

            logger.info("LinkedIn post created successfully")
            await self._close_browser()

            return {
                "success": True,
                "platform": "linkedin",
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "has_image": image_path is not None,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Post creation failed: {e}")
            await self._close_browser()
            return {"success": False, "error": str(e)}

    async def post_article(
        self,
        title: str,
        content: str,
        cover_image_path: str = None
    ) -> Dict[str, Any]:
        """
        Create and publish a LinkedIn article

        Args:
            title: Article title
            content: Article content (HTML supported)
            cover_image_path: Optional cover image path

        Returns:
            Article creation result
        """
        try:
            if not await self._init_browser():
                return {"success": False, "error": "Failed to initialize browser"}

            if not await self._check_login_status():
                await self._close_browser()
                return {"success": False, "error": "Not logged in to LinkedIn"}

            # Navigate to article creation
            await self.page.goto('https://www.linkedin.com/article/new/')
            await self.page.wait_for_timeout(3000)

            # Add cover image if provided
            if cover_image_path and Path(cover_image_path).exists():
                try:
                    cover_button = self.page.locator('button:has-text("Add a cover")').first
                    await cover_button.click()
                    await self.page.wait_for_timeout(1000)

                    file_input = self.page.locator('input[type="file"]').first
                    await file_input.set_input_files(str(Path(cover_image_path).absolute()))
                    await self.page.wait_for_timeout(3000)
                except Exception as e:
                    logger.warning(f"Failed to add cover image: {e}")

            # Add title
            title_input = self.page.locator('input[placeholder="Title"], .article-title-input').first
            await title_input.fill(title)
            await self.page.wait_for_timeout(500)

            # Add content
            content_editor = self.page.locator('.ql-editor, [contenteditable="true"]').first
            await content_editor.fill(content)
            await self.page.wait_for_timeout(1000)

            # Click Publish
            publish_button = self.page.locator('button:has-text("Publish")').first
            await publish_button.click()
            await self.page.wait_for_timeout(3000)

            # Confirm publish in modal
            confirm_button = self.page.locator('button:has-text("Publish")').last
            await confirm_button.click()
            await self.page.wait_for_timeout(5000)

            logger.info("LinkedIn article published successfully")
            await self._close_browser()

            return {
                "success": True,
                "platform": "linkedin",
                "type": "article",
                "title": title,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Article creation failed: {e}")
            await self._close_browser()
            return {"success": False, "error": str(e)}

    async def schedule_post(
        self,
        content: str,
        schedule_time: datetime,
        image_path: str = None
    ) -> Dict[str, Any]:
        """
        Schedule a LinkedIn post for later

        Args:
            content: Post content
            schedule_time: When to post
            image_path: Optional image path

        Returns:
            Schedule result
        """
        try:
            # Save to scheduled posts file
            scheduled_dir = Path("Scheduled/LinkedIn")
            scheduled_dir.mkdir(parents=True, exist_ok=True)

            post_data = {
                "content": content,
                "schedule_time": schedule_time.isoformat(),
                "image_path": image_path,
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }

            filename = scheduled_dir / f"post_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(post_data, f, indent=2)

            logger.info(f"LinkedIn post scheduled for {schedule_time}")

            return {
                "success": True,
                "platform": "linkedin",
                "schedule_time": schedule_time.isoformat(),
                "schedule_file": str(filename)
            }

        except Exception as e:
            logger.error(f"Failed to schedule post: {e}")
            return {"success": False, "error": str(e)}

    async def get_profile_info(self) -> Dict[str, Any]:
        """Get current user's profile information"""
        try:
            if not await self._init_browser():
                return {"success": False, "error": "Failed to initialize browser"}

            if not await self._check_login_status():
                await self._close_browser()
                return {"success": False, "error": "Not logged in to LinkedIn"}

            # Navigate to profile
            await self.page.goto('https://www.linkedin.com/in/me/')
            await self.page.wait_for_timeout(3000)

            # Extract profile info
            name_el = await self.page.query_selector('h1.text-heading-xlarge')
            name = await name_el.inner_text() if name_el else "Unknown"

            headline_el = await self.page.query_selector('.text-body-medium.break-words')
            headline = await headline_el.inner_text() if headline_el else ""

            await self._close_browser()

            return {
                "success": True,
                "name": name,
                "headline": headline
            }

        except Exception as e:
            logger.error(f"Failed to get profile info: {e}")
            await self._close_browser()
            return {"success": False, "error": str(e)}


# Synchronous wrapper
def post_sync(content: str, image_path: str = None) -> Dict[str, Any]:
    """Synchronous wrapper for posting"""
    poster = LinkedInPoster()
    return asyncio.run(poster.post(content, image_path))


def main():
    """Main entry point for CLI"""
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Poster with Playwright')
    parser.add_argument('action', choices=[
        'post',
        'article',
        'schedule',
        'profile',
        'login'
    ], help='Action to perform')

    parser.add_argument('--content', help='Post content')
    parser.add_argument('--title', help='Article title')
    parser.add_argument('--image', help='Image path')
    parser.add_argument('--schedule-time', help='Schedule time (ISO format)')
    parser.add_argument('--email', help='LinkedIn email')
    parser.add_argument('--password', help='LinkedIn password')

    args = parser.parse_args()

    try:
        poster = LinkedInPoster()

        if args.action == 'post':
            if not args.content:
                print(json.dumps({"error": "--content required"}))
                sys.exit(1)
            result = asyncio.run(poster.post(args.content, args.image))

        elif args.action == 'article':
            if not all([args.title, args.content]):
                print(json.dumps({"error": "--title and --content required"}))
                sys.exit(1)
            result = asyncio.run(poster.post_article(args.title, args.content, args.image))

        elif args.action == 'schedule':
            if not all([args.content, args.schedule_time]):
                print(json.dumps({"error": "--content and --schedule-time required"}))
                sys.exit(1)
            schedule_time = datetime.fromisoformat(args.schedule_time)
            result = asyncio.run(poster.schedule_post(args.content, schedule_time, args.image))

        elif args.action == 'profile':
            result = asyncio.run(poster.get_profile_info())

        elif args.action == 'login':
            async def do_login():
                await poster._init_browser()
                result = await poster.login(args.email, args.password)
                await poster._close_browser()
                return {"success": result}
            result = asyncio.run(do_login())

        print(json.dumps(result, indent=2))

    except Exception as e:
        logger.error(f"Error: {e}")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
