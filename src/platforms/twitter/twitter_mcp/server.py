#!/usr/bin/env python3
"""
Twitter/X MCP Server
Implements Model Context Protocol for Twitter/X integration
Supports posting, reading, and generating Twitter content
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import tweepy
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    logger.warning("Tweepy library not installed. Install with: pip install tweepy")
    TWEEPY_AVAILABLE = False


# Initialize server
server = Server("twitter-mcp-server")

# Global Twitter client
twitter_client = None
twitter_api = None


def get_twitter_client():
    """Initialize and return Twitter client"""
    global twitter_client, twitter_api

    if not TWEEPY_AVAILABLE:
        return None, None

    if twitter_client is None:
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        if all([api_key, api_secret, access_token, access_token_secret]):
            try:
                twitter_client = tweepy.Client(
                    bearer_token=bearer_token,
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret
                )

                auth = tweepy.OAuthHandler(api_key, api_secret)
                auth.set_access_token(access_token, access_token_secret)
                twitter_api = tweepy.API(auth)

                logger.info("Twitter API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")

    return twitter_client, twitter_api


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Twitter tools"""
    return [
        Tool(
            name="twitter_post_tweet",
            description="Post a tweet to Twitter/X",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The tweet text (max 280 characters)"},
                    "media_path": {"type": "string", "description": "Optional path to media file"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="twitter_reply_to_tweet",
            description="Reply to a specific tweet",
            inputSchema={
                "type": "object",
                "properties": {
                    "tweet_id": {"type": "string", "description": "ID of tweet to reply to"},
                    "text": {"type": "string", "description": "Reply text content"}
                },
                "required": ["tweet_id", "text"]
            }
        ),
        Tool(
            name="twitter_get_mentions",
            description="Get recent mentions of the authenticated user",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max mentions to retrieve", "default": 10}
                }
            }
        ),
        Tool(
            name="twitter_get_direct_messages",
            description="Get recent direct messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max DMs to retrieve", "default": 10}
                }
            }
        ),
        Tool(
            name="twitter_search_tweets",
            description="Search for tweets by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 10}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="twitter_get_home_timeline",
            description="Get the home timeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max tweets", "default": 20}
                }
            }
        ),
        Tool(
            name="twitter_get_followers",
            description="Get list of followers",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max followers", "default": 20}
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Twitter tool calls"""
    client, api = get_twitter_client()

    if not TWEEPY_AVAILABLE:
        return [TextContent(
            type="text",
            text="Error: Tweepy library not installed. Run: pip install tweepy"
        )]

    if not client:
        return [TextContent(
            type="text",
            text="Twitter API not configured. Set environment variables:\n" +
                 "TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET"
        )]

    try:
        if name == "twitter_post_tweet":
            return await _post_tweet(client, api, arguments)
        elif name == "twitter_reply_to_tweet":
            return await _reply_to_tweet(client, arguments)
        elif name == "twitter_get_mentions":
            return await _get_mentions(client, arguments)
        elif name == "twitter_get_direct_messages":
            return await _get_direct_messages(api, arguments)
        elif name == "twitter_search_tweets":
            return await _search_tweets(client, arguments)
        elif name == "twitter_get_home_timeline":
            return await _get_home_timeline(api, arguments)
        elif name == "twitter_get_followers":
            return await _get_followers(api, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _post_tweet(client, api, args: Dict[str, Any]) -> List[TextContent]:
    """Post a tweet"""
    text = args.get('text', '')
    media_path = args.get('media_path')

    if len(text) > 280:
        return [TextContent(type="text", text=f"Tweet too long ({len(text)} chars). Max is 280.")]

    media_ids = None
    if media_path and api:
        try:
            media = api.media_upload(media_path)
            media_ids = [media.media_id]
        except Exception as e:
            logger.warning(f"Failed to upload media: {e}")

    try:
        response = client.create_tweet(text=text, media_ids=media_ids)
        tweet_id = response.data['id']
        return [TextContent(
            type="text",
            text=f"Tweet posted successfully!\nID: {tweet_id}\nURL: https://twitter.com/i/web/status/{tweet_id}"
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Failed to post tweet: {str(e)}")]


async def _reply_to_tweet(client, args: Dict[str, Any]) -> List[TextContent]:
    """Reply to a tweet"""
    tweet_id = args.get('tweet_id')
    text = args.get('text', '')

    try:
        response = client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
        reply_id = response.data['id']
        return [TextContent(
            type="text",
            text=f"Reply posted!\nID: {reply_id}\nURL: https://twitter.com/i/web/status/{reply_id}"
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Failed to reply: {str(e)}")]


async def _get_mentions(client, args: Dict[str, Any]) -> List[TextContent]:
    """Get mentions"""
    limit = args.get('limit', 10)

    try:
        # Get authenticated user ID
        me = client.get_me()
        user_id = me.data.id

        mentions = client.get_users_mentions(
            id=user_id,
            max_results=min(limit, 100),
            tweet_fields=['created_at', 'author_id', 'text']
        )

        if not mentions.data:
            return [TextContent(type="text", text="No recent mentions found.")]

        result = f"Found {len(mentions.data)} mentions:\n\n"
        for mention in mentions.data:
            result += f"- [{mention.created_at}] {mention.text[:100]}...\n"

        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Failed to get mentions: {str(e)}")]


async def _get_direct_messages(api, args: Dict[str, Any]) -> List[TextContent]:
    """Get direct messages"""
    limit = args.get('limit', 10)

    try:
        messages = api.get_direct_messages(count=limit)

        if not messages:
            return [TextContent(type="text", text="No direct messages found.")]

        result = f"Found {len(messages)} DMs:\n\n"
        for dm in messages:
            sender_id = dm.message_create['sender_id']
            text = dm.message_create['message_data']['text']
            result += f"- From {sender_id}: {text[:100]}...\n"

        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Failed to get DMs: {str(e)}")]


async def _search_tweets(client, args: Dict[str, Any]) -> List[TextContent]:
    """Search tweets"""
    query = args.get('query', '')
    limit = args.get('limit', 10)

    try:
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(limit, 100),
            tweet_fields=['created_at', 'author_id', 'text']
        )

        if not tweets.data:
            return [TextContent(type="text", text=f"No tweets found for: {query}")]

        result = f"Found {len(tweets.data)} tweets for '{query}':\n\n"
        for tweet in tweets.data:
            result += f"- {tweet.text[:150]}...\n\n"

        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Search failed: {str(e)}")]


async def _get_home_timeline(api, args: Dict[str, Any]) -> List[TextContent]:
    """Get home timeline"""
    limit = args.get('limit', 20)

    try:
        tweets = api.home_timeline(count=limit)

        if not tweets:
            return [TextContent(type="text", text="No tweets in timeline.")]

        result = f"Home timeline ({len(tweets)} tweets):\n\n"
        for tweet in tweets:
            result += f"- @{tweet.user.screen_name}: {tweet.text[:100]}...\n"

        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Failed to get timeline: {str(e)}")]


async def _get_followers(api, args: Dict[str, Any]) -> List[TextContent]:
    """Get followers"""
    limit = args.get('limit', 20)

    try:
        followers = api.get_followers(count=limit)

        if not followers:
            return [TextContent(type="text", text="No followers found.")]

        result = f"Followers ({len(followers)}):\n\n"
        for follower in followers:
            result += f"- @{follower.screen_name}: {follower.name} ({follower.followers_count} followers)\n"

        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Failed to get followers: {str(e)}")]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
