import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.platforms.instagram.instagram_playwright import InstagramPlaywright

async def test_instagram():
    print("--- Testing Instagram Integration ---")
    
    ig = InstagramPlaywright()
    
    try:
        # 1. Initialize
        print("\n1. Initializing Browser...")
        if not await ig.initialize(headless=False):
            print("❌ Failed to initialize browser")
            return

        # 2. Test Login
        print("\n2. Testing Login...")
        if not ig.username or not ig.password:
            print("❌ SKIPPING: Instagram credentials not set in .env")
            return

        # Check if already logged in or needs login
        if await ig._check_login():
            print("ℹ️ Already logged in")
        else:
            print("ℹ️ Logging in...")
            try:
                result = await ig.login()
                print(f"DEBUG: Login Result: {result}")
                
                if not result.get('success'):
                    print(f"❌ Login Failed: {result.get('error')}")
                    if "credentials" in str(result.get('error')).lower():
                         print("⚠️ Please check INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env")
                    return
            except Exception as e:
                print(f"❌ Exception during login: {e}")
                return
        
        print("✅ Login Successful")

        # 3. Test Posting
        print("\n3. Testing Post...")
        
        # Use an artifact image
        image_path = str(Path(r"C:\Users\hp\.gemini\antigravity\brain\f6d05021-4323-48d1-b6b7-2e863b5f6eb9\media__1770748642255.png"))
        
        if not Path(image_path).exists():
            print(f"❌ Image not found at {image_path}")
            return

        print(f"posting image: {image_path}")
        caption = "Hello from AI Employee! 🤖 #AutomatedTest"
        
        # Post image (browser is already open)
        result = await ig.post_image(image_path, caption)
        
        if result.get('success'):
            print(f"✅ Post Successful: {result.get('timestamp')}")
        else:
            print(f"❌ Post Failed: {result.get('error')}")

    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
    finally:
        print("\nClosing browser...")
        await ig.close()

if __name__ == "__main__":
    asyncio.run(test_instagram())
