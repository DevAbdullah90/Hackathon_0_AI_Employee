import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.platforms.instagram.instagram_playwright import InstagramPlaywright

async def check():
    print("Checking Login Status...")
    ig = InstagramPlaywright()
    if await ig.initialize(headless=True):
        is_logged_in = await ig._check_login()
        print(f"Logged In: {is_logged_in}")
        await ig.close()
    else:
        print("Failed to init browser")

if __name__ == "__main__":
    asyncio.run(check())
