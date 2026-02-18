import os
import sys
from social_content_generator import SocialContentGenerator
from reddit_content_generator import RedditContentGenerator

def test_gemini_integration():
    print("Testing Gemini Integration...")
    
    # Check for API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY not found. Generators will fall back to templates.")
    else:
        print("GEMINI_API_KEY found.")

    print("\n1. Testing Social Content Generator (Twitter)...")
    social_gen = SocialContentGenerator()
    try:
        tweet = social_gen.generate_twitter_post(topic="AI Agents")
        print(f"Result: {tweet}")
    except Exception as e:
        print(f"Error generating tweet: {e}")

    print("\n2. Testing Reddit Content Generator...")
    reddit_gen = RedditContentGenerator()
    try:
        post = reddit_gen.generate_reddit_post(post_type="tips", subreddit="test")
        print(f"Result: {post}")
    except Exception as e:
        print(f"Error generating reddit post: {e}")

if __name__ == "__main__":
    test_gemini_integration()
