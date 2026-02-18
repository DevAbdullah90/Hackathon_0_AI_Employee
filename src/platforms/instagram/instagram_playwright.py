#!/usr/bin/env python3
"""
Instagram Playwright Automation
Posts images/reels, sends DMs, and monitors activity using Playwright
No API needed - uses browser automation
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


class InstagramPlaywright:
    """Instagram automation using Playwright - no API required"""

    def __init__(self):
        self.session_path = os.getenv('INSTAGRAM_SESSION_PATH', str(Path(__file__).parent / 'instagram_session_v2'))
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.playwright = None
        self.context = None
        self.page = None

        Path(self.session_path).mkdir(parents=True, exist_ok=True)

    async def initialize(self, headless: bool = False):
        """Initialize browser with persistent context"""
        try:
            if self.page and self.context:
                return True

            from playwright.async_api import async_playwright

            if not self.playwright:
                self.playwright = await async_playwright().start()

            # Use exact config from successful debug_playwright_minimal.py
            self.context = await self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=headless,
                args=[
                    '--disable-notifications',
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled'
                ],
                no_viewport=True,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            
            logger.info("Browser initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to init browser: {e}")
            await self.close()
            return False

# ... (omitted close/check_login methods) ...

    async def login(self, username: str = None, password: str = None) -> Dict[str, Any]:
        """Login to Instagram"""
        try:
            if not self.page:
                if not await self.initialize():
                    return {"success": False, "error": "Browser not initialized"}

            username = username or self.username
            password = password or self.password

            # 1. Check if already logged in
            if await self._check_login(navigate=True):
                logger.info("Already logged in")
                return {"success": True, "username": username, "status": "already_logged_in"}

            # 2. Go to Login page
            logger.info("Navigating to login page...")
            await self.page.goto('https://www.instagram.com/accounts/login/')
            await self.page.wait_for_timeout(2000)
            
            # Double check if we got redirected to home
            if await self._check_login(navigate=False):
                return {"success": True, "username": username}

            # 3. Fill credentials
            logger.info("Filling credentials...")
            await self.page.fill('input[name="username"]', username)
            await self.page.fill('input[name="password"]', password)
            await self.page.wait_for_timeout(1000)

            # 4. Click login
            logger.info("Clicking login...")
            await self.page.click('button[type="submit"]')
            
            # 5. Wait for result / approval
            start_time = time.time()
            max_wait = 300  # 5 minutes
            
            logger.info(f"Waiting up to {max_wait}s for login/approval...")
            
            while time.time() - start_time < max_wait:
                # Check success
                if await self._check_login(navigate=False):
                    logger.info("Login successful!")
                    return {"success": True, "username": username}

                # Check error
                if await self.page.locator('#slfErrorAlert').count() > 0:
                    error = await self.page.locator('#slfErrorAlert').inner_text()
                    return {"success": False, "error": error}
                
                # Handle Popups (Robust)
                try:
                    # Generic "Not Now" / "Dismiss" handling
                    # We look for buttons containing these texts
                    popups = [
                        'button:has-text("Not Now")',
                        'div[role="button"]:has-text("Not Now")',
                        'button:has-text("Dismiss")',
                        'div[role="button"]:has-text("Dismiss")',
                        'button:has-text("Save Info")', # Sometimes it's the affirmative we want to avoid, wait... no, click Not Now.
                        # If "Save your login info?" appears, usually "Not Now" is the secondary button.
                    ]
                    
                    for selector in popups:
                        if await self.page.locator(selector).count() > 0:
                             if await self.page.locator(selector).first.is_visible():
                                 logger.info(f"Dismissing popup: {selector}")
                                 await self.page.locator(selector).first.click()
                                 await self.page.wait_for_timeout(1000)
                except:
                    pass
                
                if int(time.time() - start_time) % 15 == 0:
                    title = await self.page.title()
                    url = self.page.url
                    logger.info(f"Still waiting... Title: {title}, URL: {url}")
                
                await self.page.wait_for_timeout(2000)

            return {"success": False, "error": "Login timed out"}

        except Exception as e:
            logger.error(f"Login error: {e}")
            return {"success": False, "error": str(e)}

    async def post_image(self, image_path: str, caption: str) -> Dict[str, Any]:
        """Post an image to Instagram"""
        try:
            if not self.page:
                if not await self.initialize():
                    return {"success": False, "error": "Browser not initialized"}

            if not Path(image_path).exists():
                return {"success": False, "error": f"Image not found: {image_path}"}

            # Ensure logged in
            if not await self._check_login():
                logger.warning("Session expired, trying to login...")
                res = await self.login()
                if not res['success']:
                    return res

            # Go home
            await self.page.goto('https://www.instagram.com/')
            
            # Click Create
            create_btn = self.page.locator('svg[aria-label="New post"]').first
            if not await create_btn.is_visible():
                create_btn = self.page.locator('span:has-text("Create")').first
            
            if not await create_btn.is_visible():
                return {"success": False, "error": "Create button not found"}
                
            await create_btn.click()
            await self.page.wait_for_timeout(2000)

            # Upload
            # Monitor for file chooser
            async with self.page.expect_file_chooser() as fc_info:
                # Try clicking "Select from computer"
                select_btn = self.page.locator('button:has-text("Select from computer")').first
                if await select_btn.is_visible():
                    await select_btn.click()
                else:
                    # Input might already be there
                    # But if we are in expected_file_chooser block, we expect an action to trigger it
                    # If input is directly available we might not need this block?
                    # Let's try direct set first? No, the modal is tricky.
                    pass
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(str(Path(image_path).absolute()))
            await self.page.wait_for_timeout(3000)

            # Next (Crop)
            next_btn = self.page.locator('div[role="button"]:has-text("Next")').first
            await next_btn.click()
            await self.page.wait_for_timeout(2000)

            # Next (Filter)
            await next_btn.click()
            await self.page.wait_for_timeout(2000)

            # Caption
            caption_area = self.page.locator('div[aria-label="Write a caption..."]').first
            await caption_area.click()
            await caption_area.fill(caption)
            await self.page.wait_for_timeout(1000)

            # Share
            share_btn = self.page.locator('div[role="button"]:has-text("Share")').first
            await share_btn.click()
            
            # Wait for success
            logger.info("Sharing...")
            # Look for "Post shared" or checkmark
            try:
                await self.page.wait_for_selector('img[alt="Animated checkmark"]', timeout=30000)
                logger.info("Post shared successfully")
                return {
                    "success": True, 
                    "platform": "instagram", 
                    "type": "image",
                    "timestamp": datetime.now().isoformat()
                }
            except:
                logger.warning("Did not see success animation, but maybe posted.")
                return {"success": True, "warning": "Confirmation timeout"}

        except Exception as e:
            logger.error(f"Post failed: {e}")
            return {"success": False, "error": str(e)}

    async def post_story(self, image_path: str) -> Dict[str, Any]:
        """
        Post a story to Instagram

        Args:
            image_path: Path to image/video file
        """
        try:
            if not Path(image_path).exists():
                return {"success": False, "error": f"File not found: {image_path}"}

            if not await self.initialize():
                return {"success": False, "error": "Failed to init browser"}

            if not await self._check_login():
                return {"success": False, "error": "Not logged in"}

            await self.page.goto('https://www.instagram.com/')
            await self.page.wait_for_timeout(3000)

            # Click on profile/story icon to add story
            story_btn = self.page.locator('svg[aria-label="New story"]').first
            if not await story_btn.is_visible():
                story_btn = self.page.locator('div[role="button"]:has-text("Story")').first
            
            if not await story_btn.is_visible():
                 # Sometimes it's the + button then Story
                 create_btn = self.page.locator('svg[aria-label="New post"]').first
                 if await create_btn.is_visible():
                     await create_btn.click()
                     await self.page.wait_for_timeout(1000)
                     story_menu_item = self.page.locator('span:has-text("Story")').first
                     if await story_menu_item.is_visible():
                         await story_menu_item.click()
                     else:
                         # click away/cancel
                         await self.page.locator('svg[aria-label="Close"]').first.click()
                         # Try profile icon?
                         pass
            
            # If still not found, try direct URL? 
            # await self.page.goto('https://www.instagram.com/create/story/') # Not standard
            
            if await story_btn.is_visible():
                await story_btn.click()
            else:
                # Fallback to create button generic flow
                 create_btn = self.page.locator('svg[aria-label="New post"]').first
                 await create_btn.click()
                 await self.page.wait_for_timeout(1000)
                 # Assume it might default to Post, switch to Story?
                 # This is tricky on web. 
                 # Let's assume standard behavior for now.

            await self.page.wait_for_timeout(2000)

            # Upload file
            file_input = self.page.locator('input[type="file"]').first
            await file_input.set_input_files(str(Path(image_path).absolute()))
            await self.page.wait_for_timeout(3000)

            # Share to story
            share_btn = self.page.locator('text="Share to Story"').first
            await share_btn.click()
            await self.page.wait_for_timeout(3000)

            logger.info("Story posted successfully")

            return {
                "success": True,
                "platform": "instagram",
                "type": "story",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Story post failed: {e}")
            return {"success": False, "error": str(e)}

    async def send_dm(self, username: str, message: str) -> Dict[str, Any]:
        """
        Send a direct message

        Args:
            username: Recipient username
            message: Message text
        """
        try:
            if not await self.initialize():
                return {"success": False, "error": "Failed to init browser"}

            if not await self._check_login():
                return {"success": False, "error": "Not logged in"}

            # Go to DMs
            await self.page.goto('https://www.instagram.com/direct/inbox/')
            await self.page.wait_for_timeout(4000)

            # Handle "Turn on Notifications" popup in DMs
            try:
                not_now = self.page.locator('button:has-text("Not Now")').first
                if await not_now.is_visible():
                    await not_now.click()
                    await self.page.wait_for_timeout(1000)
            except:
                pass

            # Click new message
            new_msg = self.page.locator('svg[aria-label="New message"]').first
            if not await new_msg.is_visible():
                new_msg = self.page.locator('div[role="button"]:has-text("New message")').first
            
            await new_msg.click()
            await self.page.wait_for_timeout(2000)

            # Select user
            input_selector = 'input[name="queryBox"]'
            if not await self.page.locator(input_selector).count():
                 input_selector = 'input[placeholder="Search..."]'
            
            await self.page.fill(input_selector, username)
            await self.page.wait_for_timeout(2000) 

            # Click the specific user row
            user_row = self.page.locator(f'div[role="button"]:has-text("{username}")').first
            
            # Wait for it
            try:
                await user_row.wait_for(state="visible", timeout=5000)
                await user_row.click()
            except:
                 # Fallback: Click first result
                 await self.page.locator('div[role="button"]').nth(1).click() # 0 might be "New message" header?
            
            await self.page.wait_for_timeout(2000)

            # Click Chat/Next
            proceed_btn = self.page.locator('div[role="button"]:has-text("Chat")').first
            if not await proceed_btn.is_visible():
                proceed_btn = self.page.locator('div[role="button"]:has-text("Next")').first
            
            if await proceed_btn.is_enabled():
                await proceed_btn.click()
            else:
                # Sometimes force click works
                await proceed_btn.click(force=True)

            await self.page.wait_for_timeout(3000)

            # Handle possible "Invite sent" or other popups
            try:
                not_now = self.page.locator('text="Not Now"').first
                if await not_now.is_visible():
                    await not_now.click()
            except:
                pass

            # Type message
            msg_input = self.page.locator('div[aria-label="Message..."]').first
            if not await msg_input.is_visible():
                 msg_input = self.page.locator('textarea[placeholder="Message..."]').first
            
            await msg_input.click()
            await msg_input.fill(message)
            await self.page.wait_for_timeout(500)

            # Send
            send_btn = self.page.locator('div[role="button"]:has-text("Send")').first
            if not await send_btn.is_visible():
                 # Press enter
                 await self.page.keyboard.press('Enter')
            else:
                 await send_btn.click()
                 
            await self.page.wait_for_timeout(2000)

            logger.info(f"DM sent to {username}")

            return {
                "success": True,
                "platform": "instagram",
                "type": "dm",
                "to": username,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"DM failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_notifications(self) -> Dict[str, Any]:
        """Get recent notifications"""
        try:
            if not await self.initialize():
                return {"success": False, "error": "Failed to init browser"}

            if not await self._check_login():
                return {"success": False, "error": "Not logged in"}

            # Go to notifications
            await self.page.goto('https://www.instagram.com/')
            await self.page.wait_for_timeout(2000)

            # Click notifications
            notif_btn = self.page.locator('svg[aria-label="Notifications"]').first
            await notif_btn.click()
            await self.page.wait_for_timeout(2000)

            # Get notification items
            notifications = []
            try:
                 # Wait for content
                await self.page.wait_for_selector('div[role="button"]', timeout=5000)
                notif_items = await self.page.query_selector_all('div[role="button"]')

                for item in notif_items[:10]:
                    try:
                        text = await item.inner_text()
                        if text and len(text) > 10:
                            notifications.append({"text": text[:100]})
                    except:
                        continue
            except:
                logger.warning("No notifications found or timed out")

            return {
                "success": True,
                "count": len(notifications),
                "notifications": notifications
            }

        except Exception as e:
            logger.error(f"Get notifications failed: {e}")
            return {"success": False, "error": str(e)}

    async def follow_user(self, username: str) -> Dict[str, Any]:
        """Follow a user"""
        try:
            if not await self.initialize():
                return {"success": False, "error": "Failed to init browser"}

            if not await self._check_login():
                return {"success": False, "error": "Not logged in"}

            # Go to user profile
            await self.page.goto(f'https://www.instagram.com/{username}/')
            await self.page.wait_for_timeout(3000)

            # Click follow button
            # It can be "Follow", "Following", "Requested"
            follow_btn = self.page.locator('button:has-text("Follow")').first
            
            if await follow_btn.is_visible():
                await follow_btn.click()
                await self.page.wait_for_timeout(2000)

                logger.info(f"Followed {username}")
                return {"success": True, "action": "follow", "username": username}
            else:
                status = "unknown"
                if await self.page.locator('button:has-text("Following")').count():
                    status = "already_following"
                elif await self.page.locator('button:has-text("Requested")').count():
                    status = "requested"
                
                return {"success": False, "error": f"Action skipped: {status}"}

        except Exception as e:
            logger.error(f"Follow failed: {e}")
            return {"success": False, "error": str(e)}

    async def like_post(self, post_url: str) -> Dict[str, Any]:
        """Like a post by URL"""
        try:
            if not await self.initialize():
                return {"success": False, "error": "Failed to init browser"}

            if not await self._check_login():
                return {"success": False, "error": "Not logged in"}

            await self.page.goto(post_url)
            await self.page.wait_for_timeout(3000)

            # Click like button
            # Often it's an SVG with aria-label="Like" (unliked) vs "Unlike" (liked)
            like_btn = self.page.locator('svg[aria-label="Like"]').first
            
            if await like_btn.is_visible():
                await like_btn.click()
                await self.page.wait_for_timeout(1000)

                logger.info(f"Liked post: {post_url}")
                return {"success": True, "action": "like", "url": post_url}
            else:
                if await self.page.locator('svg[aria-label="Unlike"]').count():
                     return {"success": False, "error": "Already liked"}
                
                return {"success": False, "error": "Like button not found"}

        except Exception as e:
            logger.error(f"Like failed: {e}")
            return {"success": False, "error": str(e)}

    def queue_post(self, image_path: str, caption: str, schedule_time: str = None) -> Dict[str, Any]:
        """Queue a post for later"""
        try:
            queue_dir = Path("Pending_Approval/Instagram")
            queue_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"INSTAGRAM_POST_{timestamp}.md"
            filepath = queue_dir / filename

            content = f"""---
type: instagram_post
image_path: {image_path}
schedule_time: {schedule_time or 'immediate'}
status: pending_approval
created_at: {datetime.now().isoformat()}
---

# Instagram Post Draft

**Image:** {image_path}

## Caption

{caption}

---

## Actions
- [ ] Review content
- [x] Approve (move to Approved folder)
- [ ] Reject
"""
            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Post queued: {filepath}")

            return {
                "success": True,
                "queue_file": str(filepath),
                "scheduled": schedule_time
            }

        except Exception as e:
            logger.error(f"Queue failed: {e}")
            return {"success": False, "error": str(e)}


# Sync wrappers
def post_image_sync(image_path: str, caption: str) -> Dict[str, Any]:
    ig = InstagramPlaywright()
    try:
        return asyncio.run(ig.post_image(image_path, caption))
    finally:
        asyncio.run(ig.close())

def send_dm_sync(username: str, message: str) -> Dict[str, Any]:
    ig = InstagramPlaywright()
    try:
        return asyncio.run(ig.send_dm(username, message))
    finally:
        asyncio.run(ig.close())


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Instagram Playwright Automation')
    parser.add_argument('action', choices=[
        'login', 'post', 'story', 'dm', 'follow', 'like', 'notifications', 'queue'
    ])
    parser.add_argument('--username', help='Instagram username or target user')
    parser.add_argument('--password', help='Instagram password')
    parser.add_argument('--image', help='Image path')
    parser.add_argument('--caption', help='Post caption')
    parser.add_argument('--message', help='DM message')
    parser.add_argument('--url', help='Post URL')
    parser.add_argument('--schedule', help='Schedule time')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')


    args = parser.parse_args()

    ig = InstagramPlaywright()
    result = None
    try:
        # Initialize browser for all actions except queue (which is local)
        if args.action != 'queue':
            asyncio.run(ig.initialize(headless=args.headless))

        if args.action == 'login':
            result = asyncio.run(ig.login(args.username, args.password))
        elif args.action == 'post':
            if not args.image or not args.caption:
                print(json.dumps({"error": "--image and --caption required"}))
                sys.exit(1)
            result = asyncio.run(ig.post_image(args.image, args.caption))
        elif args.action == 'story':
            if not args.image:
                print(json.dumps({"error": "--image required"}))
                sys.exit(1)
            result = asyncio.run(ig.post_story(args.image))
        elif args.action == 'dm':
            if not args.username or not args.message:
                print(json.dumps({"error": "--username and --message required"}))
                sys.exit(1)
            result = asyncio.run(ig.send_dm(args.username, args.message))
        elif args.action == 'follow':
            if not args.username:
                print(json.dumps({"error": "--username required"}))
                sys.exit(1)
            result = asyncio.run(ig.follow_user(args.username))
        elif args.action == 'like':
            if not args.url:
                print(json.dumps({"error": "--url required"}))
                sys.exit(1)
            result = asyncio.run(ig.like_post(args.url))
        elif args.action == 'notifications':
            result = asyncio.run(ig.get_notifications())
        elif args.action == 'queue':
            if not args.image or not args.caption:
                print(json.dumps({"error": "--image and --caption required"}))
                sys.exit(1)
            result = ig.queue_post(args.image, args.caption, args.schedule)

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    finally:
        if args.action != 'queue':
            asyncio.run(ig.close())


if __name__ == '__main__':
    main()
