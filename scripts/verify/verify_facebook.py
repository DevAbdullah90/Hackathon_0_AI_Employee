#!/usr/bin/env python3
"""
Verify Facebook Integration
Tests login and posting capabilities
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.platforms.facebook.facebook_poster import FacebookPoster

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyFacebook")

async def test_facebook():
    print("--- Testing Facebook Integration ---")
    
    poster = FacebookPoster()
    
    # 1. Test Login
    print("\n1. Testing Login...")
    if not poster.email or not poster.password:
        print("❌ SKIPPING: Facebook credentials not set in .env")
        return

    # Initialize browser (headless=False to see what happens)
    await poster._init_browser(headless=False)
    
    success = await poster.login()
    if success:
        print("✅ Login Successful")
    else:
        print("❌ Login Failed")
        await poster._close_browser()
        return

    # 2. Test Posting (Auto-confirm)
    print("\n2. Testing Post...")
    # response = input("Do you want to post a test message? (y/n): ")
    response = 'y'
    
    if response.lower() == 'y':
        content = "Hello from AI Employee! 🤖 #AutomatedTest"
        result = await poster.post(content)
        
        if result['success']:
            print(f"✅ Post Successful: {result.get('timestamp')}")
        else:
            print(f"❌ Post Failed: {result.get('error')}")
    
    await poster._close_browser()

if __name__ == "__main__":
    try:
        asyncio.run(test_facebook())
    except KeyboardInterrupt:
        print("\nTest cancelled.")
