#!/usr/bin/env python3
"""
Test script to post Twitter content directly using the PlatformPoster
"""

import os
import sys
from pathlib import Path

# Add the vault directory to the path
vault_path = Path(__file__).parent.resolve()
sys.path.insert(0, str(vault_path))

from auto_processor import PlatformPoster

def test_twitter_post():
    """Test posting a tweet directly"""

    # Read the tweet content from the approved file
    tweet_file = vault_path / "Approved" / "TWEET_thankyou_sir_zia.md"

    if not tweet_file.exists():
        print(f"Tweet file not found: {tweet_file}")
        return False

    content = tweet_file.read_text(encoding='utf-8')

    # Extract the actual tweet content
    lines = content.split('\n')
    tweet_content = ""
    in_content_section = False

    for line in lines:
        if line.strip().startswith("**Content:**"):
            in_content_section = True
            continue
        elif in_content_section and line.strip().startswith("#"):
            # Found hashtag line, add it to content
            tweet_content += line.strip() + "\n"
        elif in_content_section and line.strip() and not line.strip().startswith("---") and not line.strip().startswith("**"):
            # Regular content line
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("# Tweet - Thank You Sir Zia"):
                tweet_content += clean_line + "\n"

    # Clean up the content
    tweet_content = tweet_content.strip()

    print(f"Attempting to post tweet:")
    print(f"Content: {tweet_content}")
    print(f"Character count: {len(tweet_content)}")

    # Create PlatformPoster instance
    poster = PlatformPoster()

    # Post to Twitter
    result = poster.post_to_twitter(tweet_content, {})

    print(f"Post result: {result}")

    return result.get('success', False)

if __name__ == "__main__":
    success = test_twitter_post()
    if success:
        print("\nTweet posted successfully!")
    else:
        print("\nFailed to post tweet.")