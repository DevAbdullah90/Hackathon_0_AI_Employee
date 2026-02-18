import asyncio
import os
from pathlib import Path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.platforms.linkedin.linkedin_poster import LinkedInPoster

async def check_session():
    print("Checking LinkedIn session...")
    poster = LinkedInPoster()
    
    # Print paths being used
    print(f"Session path: {poster.session_path}")
    print(f"Cookies path: {poster.cookies_path}")
    
    # Check if files exist
    if os.path.exists(poster.session_path):
        print("Session directory exists")
    else:
        print("Session directory DOES NOT exist")
        
    if os.path.exists(poster.cookies_path):
        print(f"Cookies file exists (size: {os.path.getsize(poster.cookies_path)} bytes)")
        with open(poster.cookies_path, 'r') as f:
            print(f"Content preview: {f.read()[:100]}...")
    else:
        print("Cookies file DOES NOT exist")
        
    # Attempt to init browser and check login
    print("\nInitializing browser...")
    await poster._init_browser(headless=False) # Run headed to see
    
    logged_in = await poster._check_login_status()
    print(f"Logged in status: {logged_in}")
    
    if not logged_in:
        print("Not logged in. Please log in manually in the browser window that opens.")
        print("Waiting 60 seconds for manual login...")
        await asyncio.sleep(60)
        
        logged_in = await poster._check_login_status()
        print(f"Logged in status after wait: {logged_in}")
        
        if logged_in:
            await poster._save_cookies()
            print("Saved cookies after manual login")
            
    await poster._close_browser()

if __name__ == "__main__":
    asyncio.run(check_session())
