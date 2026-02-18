#!/usr/bin/env python3
"""
Send Instagram DM
Sends a direct message to a target user
"""
import sys
import asyncio
from dotenv import load_dotenv
from instagram_playwright import InstagramPlaywright

# Load environment variables
load_dotenv()

async def main():
    if len(sys.argv) < 3:
        print("Usage: python send_instagram_dm.py <username> <message>")
        return

    target_user = sys.argv[1]
    message = " ".join(sys.argv[2:])
    
    print(f"Sending DM to: {target_user}")
    print(f"Message: {message}")
    print("--------------------------------")
    
    ig = InstagramPlaywright()
    
    # Init browser (headless by default, but you can change to False if needed for debugging)
    # Note: send_dm will handle login check automatically using saved session
    result = await ig.send_dm(target_user, message)
    
    if result.get('success'):
        print("\n✅ DM Sent Successfully!")
        print(f"Timestamp: {result.get('timestamp')}")
    else:
        print("\n❌ DM Failed.")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
