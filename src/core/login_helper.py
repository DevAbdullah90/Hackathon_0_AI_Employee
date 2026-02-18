#!/usr/bin/env python3
"""
Login Helper - Open browsers to login to Instagram & WhatsApp
=============================================================
Run this script to login to platforms that need browser authentication.
"""

import os
import sys
import asyncio
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))

async def login_instagram():
    """Open browser to login to Instagram"""
    print("\n" + "="*50)
    print("INSTAGRAM LOGIN")
    print("="*50)

    try:
        from playwright.async_api import async_playwright

        session_path = os.getenv('INSTAGRAM_SESSION_PATH', './instagram_session')
        username = os.getenv('INSTAGRAM_USERNAME', '')
        password = os.getenv('INSTAGRAM_PASSWORD', '')

        print(f"Username: {username}")
        print(f"Session will be saved to: {session_path}")
        print("\nOpening browser...")

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                args=['--no-sandbox'],
                viewport={'width': 430, 'height': 932},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
            )

            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto('https://www.instagram.com/accounts/login/')
            await page.wait_for_timeout(3000)

            # Check if already logged in
            login_form = await page.query_selector('input[name="username"]')

            if login_form:
                print("\nLogin form detected. Please login manually in the browser.")
                print("The script will wait for you to complete login...")

                # Auto-fill if credentials available
                if username and password:
                    print("Auto-filling credentials...")
                    await page.fill('input[name="username"]', username)
                    await page.wait_for_timeout(500)
                    await page.fill('input[name="password"]', password)
                    print("Credentials filled. Click 'Log in' button.")

                # Wait for user to login (max 5 minutes)
                print("\nWaiting for login (max 5 minutes)...")
                for i in range(60):
                    await page.wait_for_timeout(5000)
                    # Check if logged in
                    home = await page.query_selector('svg[aria-label="Home"]')
                    if home:
                        print("\nLOGIN SUCCESSFUL!")
                        break
                    if i % 6 == 0:
                        print(f"  Still waiting... ({i*5}s)")
            else:
                print("Already logged in!")

            print("\nClosing browser and saving session...")
            await context.close()

        print("Instagram session saved!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

async def login_whatsapp():
    """Open browser to scan WhatsApp QR code"""
    print("\n" + "="*50)
    print("WHATSAPP LOGIN (QR CODE)")
    print("="*50)

    try:
        from playwright.async_api import async_playwright

        session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')

        print(f"Session will be saved to: {session_path}")
        print("\nOpening browser...")
        print("Please scan the QR code with your phone's WhatsApp app.")

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                args=['--no-sandbox'],
                viewport={'width': 1280, 'height': 900}
            )

            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto('https://web.whatsapp.com/')
            await page.wait_for_timeout(3000)

            # Check if QR code is present
            qr_code = await page.query_selector('canvas[aria-label="Scan me!"]')

            if qr_code:
                print("\nQR CODE DISPLAYED - Please scan with your phone!")
                print("Open WhatsApp on your phone > Settings > Linked Devices > Link a Device")
                print("\nWaiting for QR scan (max 5 minutes)...")

                # Wait for user to scan QR
                for i in range(60):
                    await page.wait_for_timeout(5000)
                    # Check if logged in (QR gone, chats visible)
                    qr = await page.query_selector('canvas[aria-label="Scan me!"]')
                    if not qr:
                        # Verify we're in chat view
                        chat_list = await page.query_selector('[data-testid="chat-list"]')
                        if chat_list:
                            print("\nLOGIN SUCCESSFUL! WhatsApp connected.")
                            break
                    if i % 6 == 0:
                        print(f"  Still waiting for QR scan... ({i*5}s)")
            else:
                # Check if already logged in
                chat_list = await page.query_selector('[data-testid="chat-list"]')
                if chat_list:
                    print("Already logged in to WhatsApp!")
                else:
                    print("Unknown state - please check the browser.")

            print("\nKeeping browser open for 10 more seconds...")
            await page.wait_for_timeout(10000)

            print("Closing browser and saving session...")
            await context.close()

        print("WhatsApp session saved!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

async def login_linkedin():
    """Open browser to login to LinkedIn"""
    print("\n" + "="*50)
    print("LINKEDIN LOGIN")
    print("="*50)

    try:
        from playwright.async_api import async_playwright

        session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session')
        cookies_path = os.getenv('LINKEDIN_COOKIES_PATH', './linkedin_cookies.json')
        email = os.getenv('LINKEDIN_EMAIL', '')
        password = os.getenv('LINKEDIN_PASSWORD', '')

        print(f"Email: {email}")
        print(f"Session path: {session_path}")
        print("\nOpening browser...")

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                args=['--no-sandbox'],
                viewport={'width': 1280, 'height': 900}
            )

            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto('https://www.linkedin.com/feed/')
            await page.wait_for_timeout(3000)

            # Check if need to login
            login_btn = await page.query_selector('a[data-tracking-control-name="guest_homepage-basic_sign-in-button"]')
            login_form = await page.query_selector('input#username')

            if login_btn or login_form:
                print("Login required...")
                await page.goto('https://www.linkedin.com/login')
                await page.wait_for_timeout(2000)

                if email and password:
                    print("Auto-filling credentials...")
                    await page.fill('input#username', email)
                    await page.wait_for_timeout(300)
                    await page.fill('input#password', password)
                    print("Credentials filled. Click 'Sign in' or press Enter.")

                print("\nWaiting for login (max 3 minutes)...")
                for i in range(36):
                    await page.wait_for_timeout(5000)
                    feed = await page.query_selector('.share-box-feed-entry__trigger')
                    if feed:
                        print("\nLOGIN SUCCESSFUL!")
                        break
                    if i % 6 == 0:
                        print(f"  Still waiting... ({i*5}s)")
            else:
                print("Already logged in!")

            # Save cookies
            import json
            cookies = await context.cookies()
            Path(cookies_path).write_text(json.dumps(cookies, indent=2))
            print(f"Cookies saved to {cookies_path}")

            print("\nClosing browser...")
            await context.close()

        print("LinkedIn session saved!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    """Main menu"""
    print("="*60)
    print("PLATFORM LOGIN HELPER")
    print("="*60)
    print("\nThis will open browsers to login to platforms.")
    print("\nOptions:")
    print("  1. Login to Instagram")
    print("  2. Login to WhatsApp (QR scan)")
    print("  3. Login to LinkedIn")
    print("  4. Login to ALL platforms")
    print("  0. Exit")

    choice = input("\nEnter choice (1-4, or 0 to exit): ").strip()

    if choice == '1':
        await login_instagram()
    elif choice == '2':
        await login_whatsapp()
    elif choice == '3':
        await login_linkedin()
    elif choice == '4':
        print("\nLogging into all platforms...")
        await login_instagram()
        await login_whatsapp()
        await login_linkedin()
        print("\n" + "="*60)
        print("ALL LOGINS COMPLETE!")
        print("="*60)
    elif choice == '0':
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    # Check if specific platform passed as argument
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        if platform == 'instagram' or platform == 'ig':
            asyncio.run(login_instagram())
        elif platform == 'whatsapp' or platform == 'wa':
            asyncio.run(login_whatsapp())
        elif platform == 'linkedin' or platform == 'li':
            asyncio.run(login_linkedin())
        elif platform == 'all':
            async def all_logins():
                await login_instagram()
                await login_whatsapp()
                await login_linkedin()
            asyncio.run(all_logins())
        else:
            print(f"Unknown platform: {platform}")
            print("Usage: python login_helper.py [instagram|whatsapp|linkedin|all]")
    else:
        asyncio.run(main())
