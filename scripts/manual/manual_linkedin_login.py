import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("ManualLogin")

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...")
    os.system("pip install playwright")
    os.system("playwright install chromium")
    from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

async def manual_login():
    """
    Opens a browser with the persistent session and waits for user input.
    """
    session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session_v2')
    cookies_path = os.getenv('LINKEDIN_COOKIES_PATH', 'linkedin_cookies_v2.json')
    
    # Ensure directory exists (Playwright needs this)
    Path(session_path).mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Using session path: {session_path}")
    logger.info("Launching browser...")
    
    async with async_playwright() as p:
        # Launch persistent context
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=session_path,
            headless=False,
            # channel='msedge',  <-- Removed to use bundled Chromium (more stable)
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled'
            ],
            viewport=None  # Allow full window management
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        logger.info("Navigating to LinkedIn...")
        await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        
        print("\n" + "="*60)
        print("🔓 MANUAL LOGIN MODE 🔓")
        print("="*60)
        print("1. The browser window should now be open.")
        print("2. Please log in manually (Username/Password or Google).")
        print("3. Deal with any 2FA or CAPTCHA challenges.")
        print("4. WAIT until you see your LinkedIn Feed.")
        print("="*60)
        
        print("\n👉 PRESS Ctrl+C HERE ONCE YOU ARE FULLY LOGGED IN AND SEE THE FEED...")
        
        try:
            while True:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            print("\nCaptured Exit Signal! Saving session...")
            logger.info("Saving cookies...")
            if browser:
                try:
                    cookies = await browser.cookies()
                    with open(cookies_path, 'w') as f:
                        import json
                        json.dump(cookies, f, indent=2)
                    logger.info(f"Cookies saved to {cookies_path}")
                except Exception as e:
                    logger.error(f"Failed to save cookies: {e}")
                
                logger.info("Closing browser...")
                try:
                    await browser.close()
                except:
                    pass
            print("\n✅ Session saved! You can now run the validation script again.")

if __name__ == "__main__":
    try:
        asyncio.run(manual_login())
    except KeyboardInterrupt:
        # This catch is for the asyncio.run wrapper itself
        pass
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
