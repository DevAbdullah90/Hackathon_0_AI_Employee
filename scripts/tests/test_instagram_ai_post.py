#!/usr/bin/env python3
"""
Test script to demonstrate Instagram AI-related post functionality
"""

import asyncio
import json
import os
from pathlib import Path

# Add the project root to the path so we can import the Instagram module
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from instagram_playwright import InstagramPlaywright

async def test_instagram_ai_post():
    """
    Test function to demonstrate Instagram posting with AI-related content
    """
    print("Testing Instagram AI-related post functionality...")

    # Initialize the Instagram automation
    ig = InstagramPlaywright()

    # Test data for an AI-related post
    ai_caption = """🚀 The Future of AI is NOW!

Artificial Intelligence is revolutionizing industries worldwide:
• Machine Learning algorithms that learn & adapt
• Natural Language Processing for human-like interactions
• Computer Vision that sees & understands
• Neural Networks that mimic human brain functions

AI isn't replacing humans - it's amplifying human potential! 💡

#AI #ArtificialIntelligence #MachineLearning #TechInnovation #FutureTech #Innovation #Technology #AIArt #SmartTech #DigitalTransformation"""

    # Since we don't have a real image file, let's demonstrate the queuing functionality
    # which is safer than attempting to post without a real image
    result = ig.queue_post(
        image_path="mock_ai_image.txt",  # This would be a real image path in practice
        caption=ai_caption,
        schedule_time=None
    )

    print("Queuing result:")
    print(json.dumps(result, indent=2))

    if result.get('success'):
        print("\n[SUCCESS] AI-related Instagram post has been queued for approval!")
        print("The post will appear in the Pending_Approval/Instagram folder")
        print("After manual approval, it will be moved to Approved folder for processing")
    else:
        print(f"\n[FAILED] Failed to queue post: {result.get('error', 'Unknown error')}")

    # Show how to run the actual posting (commented out for safety)
    print("\n" + "="*60)
    print("To post a real image to Instagram, you would:")
    print("1. Have a real image file (e.g., ai_concept.jpg)")
    print("2. Run: python -m instagram_playwright post --image ai_concept.jpg --caption \"Your caption here\"")
    print("3. The system would then automate the posting process")
    print("="*60)

if __name__ == "__main__":
    print("Instagram AI Post Testing Script")
    print("="*50)

    # Run the test
    asyncio.run(test_instagram_ai_post())

    print("\nNote: Actual posting requires a valid Instagram account and real image file.")
    print("The system is configured with Instagram credentials from .env file.")
    print("Always ensure compliance with Instagram's terms of service when automating.")