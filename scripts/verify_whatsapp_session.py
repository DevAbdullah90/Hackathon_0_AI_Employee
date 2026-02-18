import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright

async def verify_session():
    # Define absolute path for session
    project_root = Path(__file__).parent.parent
    session_path = project_root / 'whatsapp_session_v2'
    
    print(f"Verifying WhatsApp Session...")
    print(f"Session Path: {session_path}")
    
    if not session_path.exists():
        print("Session directory does not exist. Creating it...")
        session_path.mkdir(parents=True, exist_ok=True)
    else:
        print("Session directory exists.")

    print("\nLaunching browser...")
    print("Please scan the QR code if prompted.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        print("Navigating to WhatsApp Web...")
        await page.goto("https://web.whatsapp.com/")
        
        print("Waiting for login...")
        print("Keep this window open until you see your chats.")
        
        # Wait for chat list or QR code
        try:
            # Wait up to 5 minutes for user to login
            print("Waiting for chat interface (Timeout: 5 minutes)...")
            await page.wait_for_selector('div[contenteditable="true"][data-tab]', timeout=300000)
            print("\nSUCCESS! Login detected (Chat input found).")
            print("Session saved.")
            
            # Wait a bit to ensure everything syncs
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"\nTimeout or error: {e}")
            print("If you were stuck on 'Loading your chats', try refreshing the page (Ctrl+R).")
            print("If you saw the QR code but couldn't scan in time, try again.")
            
        finally:
            print("Closing browser...")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_session())
