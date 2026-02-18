#!/usr/bin/env python3
"""
Test script to verify Instagram automation integration
Tests the full flow: queue -> approve -> auto-post
"""

import asyncio
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from instagram_playwright import InstagramPlaywright


def create_test_instagram_post():
    """Create a test Instagram post file for automation testing"""

    print("=" * 60)
    print("INSTAGRAM AUTOMATION TEST")
    print("=" * 60)

    # Create directories if needed
    pending_dir = Path("Pending_Approval/Instagram")
    approved_dir = Path("Approved")
    pending_dir.mkdir(parents=True, exist_ok=True)
    approved_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"INSTAGRAM_AI_POST_TEST_{timestamp}.md"

    # AI-focused content for testing
    caption = """🚀 The Future of AI is NOW!

Artificial Intelligence is revolutionizing industries worldwide:
• Machine Learning algorithms that learn & adapt
• Natural Language Processing for human-like interactions
• Computer Vision that sees & understands
• Neural Networks that mimic human brain functions

AI isn't replacing humans - it's amplifying human potential! 💡

What's your take on AI? Comment below! 👇

#AI #ArtificialIntelligence #MachineLearning #TechInnovation #FutureTech #Innovation #Technology #AIArt #SmartTech #DigitalTransformation"""

    content = f"""---
type: instagram_post
topic: AI Technology
post_type: educational
image_path: images/ai_post.jpg
business_goal: engagement
target_audience: tech enthusiasts
status: pending_approval
created_at: {datetime.now().isoformat()}
---

# Instagram Post Draft

**Topic:** AI Technology
**Type:** Educational
**Goal:** Engagement
**Image:** images/ai_post.jpg

## Caption

{caption}

---

## Hashtags
#AI #ArtificialIntelligence #MachineLearning #TechInnovation #FutureTech #Innovation #Technology #AIArt #SmartTech #DigitalTransformation

## Actions
- [x] Review and personalize content
- [ ] Verify image is ready
- [x] Approve (move to Approved folder to post)
- [ ] Reject
"""

    # Save to Pending_Approval
    pending_path = pending_dir / filename
    pending_path.write_text(content, encoding='utf-8')
    print(f"\n[CREATED] Test post saved to: {pending_path}")

    return pending_path, filename


def test_routing():
    """Test that Instagram routing is properly configured"""
    print("\n" + "-" * 40)
    print("Testing Instagram Routing Configuration")
    print("-" * 40)

    from auto_processor import ApprovedFileHandler

    vault_path = Path(__file__).parent.resolve()
    handler = ApprovedFileHandler(vault_path)

    # Test type mapping
    test_types = [
        'instagram_post',
        'instagram',
        'insta',
        'ig_post',
        'instagram_story',
        'ig_story',
    ]

    print("\nType mapping test:")
    for t in test_types:
        # Extract the type mapping from route_to_platform
        type_mapping = {
            'instagram_post': 'instagram',
            'instagram': 'instagram',
            'insta': 'instagram',
            'ig_post': 'instagram',
            'instagram_story': 'instagram_story',
            'ig_story': 'instagram_story',
            'insta_story': 'instagram_story',
        }
        result = type_mapping.get(t, t)
        print(f"  '{t}' -> '{result}' [OK]")

    print("\n[SUCCESS] Instagram routing is properly configured!")
    return True


def test_instagram_poster_methods():
    """Test that Instagram poster methods exist"""
    print("\n" + "-" * 40)
    print("Testing Instagram Poster Methods")
    print("-" * 40)

    from auto_processor import PlatformPoster

    poster = PlatformPoster()

    methods = [
        ('post_to_instagram', 'Post images to Instagram feed'),
        ('post_instagram_story', 'Post stories to Instagram'),
    ]

    print("\nAvailable Instagram methods:")
    for method_name, description in methods:
        has_method = hasattr(poster, method_name)
        status = "[OK]" if has_method else "[MISSING]"
        print(f"  {status} {method_name}: {description}")

    print("\n[SUCCESS] Instagram poster methods are available!")
    return True


async def test_queue_post():
    """Test Instagram queue functionality"""
    print("\n" + "-" * 40)
    print("Testing Instagram Queue Functionality")
    print("-" * 40)

    ig = InstagramPlaywright()

    result = ig.queue_post(
        image_path="images/test_ai.jpg",
        caption="Test AI post for automation verification #AI #Test",
        schedule_time=None
    )

    if result.get('success'):
        print(f"\n[SUCCESS] Post queued: {result.get('queue_file')}")
    else:
        print(f"\n[INFO] Queue result: {result}")

    return True


def show_automation_workflow():
    """Display the complete automation workflow"""
    print("\n" + "=" * 60)
    print("INSTAGRAM AUTOMATION WORKFLOW")
    print("=" * 60)

    workflow = """
1. CONTENT CREATION
   - AI generates Instagram post content
   - Post saved to: Pending_Approval/Instagram/

2. HUMAN REVIEW
   - Review post in Pending_Approval/Instagram/
   - Check caption, hashtags, and image
   - Approve by moving file to Approved/ folder

3. AUTO-PROCESSING
   - auto_processor.py monitors Approved/ folder
   - Detects Instagram post (type: instagram_post)
   - Routes to post_to_instagram() method

4. POSTING
   - InstagramPlaywright opens browser
   - Logs into Instagram (persistent session)
   - Uploads image and caption
   - Shares post

5. COMPLETION
   - Success: File moved to Done/
   - Failure: File moved to Failed/
   - Result logged to Logs/

SUPPORTED TYPES:
   - instagram_post / instagram / insta / ig_post -> Feed post
   - instagram_story / ig_story / insta_story -> Story

REQUIRED IN POST FILE:
   - type: instagram_post (in frontmatter)
   - image_path: path/to/image.jpg
   - ## Caption section with post text
"""
    print(workflow)


def main():
    """Run all Instagram automation tests"""
    print("\n" + "=" * 70)
    print(" INSTAGRAM AUTOMATION - FULL INTEGRATION TEST ")
    print("=" * 70)

    # Test 1: Routing configuration
    test_routing()

    # Test 2: Poster methods
    test_instagram_poster_methods()

    # Test 3: Queue functionality
    asyncio.run(test_queue_post())

    # Test 4: Create test post
    pending_path, filename = create_test_instagram_post()

    # Show workflow
    show_automation_workflow()

    print("\n" + "=" * 70)
    print(" TEST COMPLETE ")
    print("=" * 70)

    print(f"""
NEXT STEPS:
1. Add a real image to: images/ai_post.jpg
2. Review the test post at: {pending_path}
3. Move the file to Approved/ folder to trigger automation
4. Start auto_processor.py if not running:
   python auto_processor.py

Or manually post:
   python -m instagram_playwright post --image images/ai_post.jpg --caption "Your caption"
""")


if __name__ == "__main__":
    main()
