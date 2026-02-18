from playwright.sync_api import sync_playwright
import time
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_instagram_sync():
    print("--- Testing Instagram Integration (Sync) ---")
    
    session_path = os.getenv('INSTAGRAM_SESSION_PATH', './instagram_session_v2')
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("❌ Credentials missing in .env")
        return

    print(f"Session path: {session_path}")

    with sync_playwright() as p:
        print("Launching browser...")
        try:
            # Using the config that worked in minimal script + user_agent
            context = p.chromium.launch_persistent_context(
                user_data_dir=session_path,
                headless=False,
                args=[
                    '--disable-notifications',
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled'
                ],
                no_viewport=True,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        except Exception as e:
            print(f"❌ Browser Launch Failed: {e}")
            return

        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            print("Navigating to Instagram...")
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            time.sleep(3)

            # Check Login
            print("Checking login status...")
            is_logged_in = False
            if page.locator('svg[aria-label="Home"]').count() > 0 or \
               page.locator('svg[aria-label="Search"]').count() > 0 or \
               page.locator('img[alt*="profile picture"]').count() > 0:
                is_logged_in = True
            
            else:
                print("ℹ️ Logging in...")
                page.goto("https://www.instagram.com/accounts/login/")
                
                # Wait for username input
                try:
                    page.wait_for_selector('input[name="username"]', timeout=10000)
                except:
                    print(f"⚠️ specific input not found at {page.url} ({page.title()})")
                    screenshot_path = str(Path(r"C:\Users\hp\.gemini\antigravity\brain\f6d05021-4323-48d1-b6b7-2e863b5f6eb9\instagram_login_fail.png"))
                    print(f"saved screenshot to {screenshot_path}")
                    
                    html_path = str(Path(r"C:\Users\hp\.gemini\antigravity\brain\f6d05021-4323-48d1-b6b7-2e863b5f6eb9\login_page.html"))
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(page.content())
                    print(f"Saved HTML to {html_path}")

                if page.locator('input[name="username"]').count() > 0:
                    page.fill('input[name="username"]', username)
                    page.fill('input[name="password"]', password)
                    time.sleep(1)
                    page.click('button[type="submit"]')
                    print("Credentials submitted. Waiting for login/approval...")
                    
                    # Wait loop
                    start = time.time()
                    while time.time() - start < 300: # 5 mins
                        # Check success
                        if page.locator('svg[aria-label="Home"]').count() > 0 or \
                           page.locator('svg[aria-label="Search"]').count() > 0:
                            print("✅ Login Successful!")
                            is_logged_in = True
                            break
                        
                        # Handle Popups
                        try:
                            if page.locator('button:has-text("Not Now")').is_visible():
                                page.locator('button:has-text("Not Now")').click()
                                print("Dismissed 'Not Now'")
                        except: pass
                        
                        # Log status
                        if int(time.time() - start) % 10 == 0:
                             print(f"Waiting... {page.title()} - {page.url}")
                        
                        time.sleep(2)
                else:
                    print("❌ Login input not found (and not logged in)")

            if not is_logged_in:
                print("❌ Cannot proceed to post: Not logged in")
                context.close()
                return

            # Test Posting
            print("\nTesting Post...")
            image_path = str(Path(r"C:\Users\hp\.gemini\antigravity\brain\f6d05021-4323-48d1-b6b7-2e863b5f6eb9\media__1770748642255.png"))
            
            if not Path(image_path).exists():
                print("❌ Image not found")
            else:
                # Go Home
                page.goto("https://www.instagram.com/")
                time.sleep(3)
                
                # Create
                create_btn = page.locator('svg[aria-label="New post"]').first
                if not create_btn.is_visible():
                     create_btn = page.locator('span:has-text("Create")').first
                
                if create_btn.is_visible():
                    create_btn.click()
                    time.sleep(2)
                    
                    # Upload
                    with page.expect_file_chooser() as fc_info:
                         page.locator('button:has-text("Select from computer")').click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(image_path)
                    time.sleep(3)
                    
                    # Next
                    page.locator('div[role="button"]:has-text("Next")').first.click()
                    time.sleep(2)
                    page.locator('div[role="button"]:has-text("Next")').first.click()
                    time.sleep(2)
                    
                    # Share
                    page.locator('div[role="button"]:has-text("Share")').first.click()
                    print("Clicked Share...")
                    
                    # Wait for success
                    try:
                        page.wait_for_selector('img[alt="Animated checkmark"]', timeout=30000)
                        print("✅ Post Shared Successfully!")
                    except:
                        print("⚠️ Success animation not seen, but might have posted.")
                else:
                    print("❌ Create button not found")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("Closing browser...")
            context.close()

if __name__ == "__main__":
    test_instagram_sync()
