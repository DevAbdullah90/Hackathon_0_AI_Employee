#!/usr/bin/env python3
"""
Facebook and Instagram MCP Server
Implements Model Context Protocol for social media integration
Supports posting, reading, and generating social media content
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

# Initialize server
server = Server("facebook-instagram-mcp-server")


def get_config() -> Dict[str, str]:
    """Get social media API configuration from environment"""
    return {
        'facebook_access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', ''),
        'facebook_page_id': os.getenv('FACEBOOK_PAGE_ID', ''),
        'instagram_user_id': os.getenv('INSTAGRAM_USER_ID', ''),
        'instagram_username': os.getenv('INSTAGRAM_USERNAME', ''),
        'instagram_password': os.getenv('INSTAGRAM_PASSWORD', ''),
    }


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Facebook/Instagram tools"""
    return [
        Tool(
            name="facebook_post_message",
            description="Post a message to Facebook Page",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The message to post"},
                    "link": {"type": "string", "description": "Optional link to include"}
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="facebook_post_photo",
            description="Post a photo to Facebook Page",
            inputSchema={
                "type": "object",
                "properties": {
                    "photo_url": {"type": "string", "description": "URL of the photo"},
                    "caption": {"type": "string", "description": "Photo caption"}
                },
                "required": ["photo_url"]
            }
        ),
        Tool(
            name="instagram_post_photo",
            description="Post a photo to Instagram (via Graph API)",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "Public URL of image"},
                    "caption": {"type": "string", "description": "Post caption with hashtags"}
                },
                "required": ["image_url", "caption"]
            }
        ),
        Tool(
            name="instagram_post_carousel",
            description="Post multiple images as carousel to Instagram",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of image URLs (2-10)"
                    },
                    "caption": {"type": "string", "description": "Post caption"}
                },
                "required": ["image_urls", "caption"]
            }
        ),
        Tool(
            name="facebook_get_page_insights",
            description="Get Facebook Page analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "description": "Metric (reach, engagement, impressions)"},
                    "period": {"type": "string", "description": "Period (day, week, month)", "default": "week"}
                }
            }
        ),
        Tool(
            name="facebook_get_messages",
            description="Get recent Facebook Page messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max messages", "default": 10}
                }
            }
        ),
        Tool(
            name="instagram_get_direct_messages",
            description="Get Instagram DMs (requires special permissions)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max DMs", "default": 10}
                }
            }
        ),
        Tool(
            name="generate_social_summary",
            description="Generate social media activity summary for CEO briefing",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "description": "facebook, instagram, or both", "default": "both"},
                    "period": {"type": "string", "description": "Time period", "default": "week"}
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Facebook/Instagram tool calls"""
    config = get_config()

    if not config['facebook_access_token']:
        return [TextContent(
            type="text",
            text="Note: Facebook/Instagram API not configured. Using simulated data.\n\n" +
                 _get_simulated_response(name, arguments)
        )]

    try:
        if name == "facebook_post_message":
            return await _facebook_post_message(config, arguments)
        elif name == "facebook_post_photo":
            return await _facebook_post_photo(config, arguments)
        elif name == "instagram_post_photo":
            return await _instagram_post_photo(config, arguments)
        elif name == "instagram_post_carousel":
            return await _instagram_post_carousel(config, arguments)
        elif name == "facebook_get_page_insights":
            return await _facebook_get_insights(config, arguments)
        elif name == "facebook_get_messages":
            return await _facebook_get_messages(config, arguments)
        elif name == "instagram_get_direct_messages":
            return await _instagram_get_dms(config, arguments)
        elif name == "generate_social_summary":
            return await _generate_social_summary(config, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def _get_simulated_response(name: str, arguments: Dict[str, Any]) -> str:
    """Return simulated data when API is not configured"""
    if name == "facebook_post_message":
        return f"[SIMULATED] Facebook post:\n\"{arguments.get('message', 'No message')}\""

    elif name == "instagram_post_photo":
        return f"[SIMULATED] Instagram post:\nImage: {arguments.get('image_url', 'No URL')}\nCaption: {arguments.get('caption', 'No caption')}"

    elif name == "facebook_get_page_insights":
        return """[SIMULATED] Facebook Insights (This Week):
- Page Reach: 1,234
- Post Engagements: 567
- New Page Likes: +23
- Top Post: "AI Employee Update" - 234 reactions"""

    elif name == "generate_social_summary":
        return """[SIMULATED] Social Media Summary

Facebook:
- Posts: 5
- Reach: 3,456
- Engagement: 4.2%

Instagram:
- Posts: 3
- Reach: 2,100
- Engagement: 5.8%

Top Content: Business automation tips"""

    return f"[SIMULATED] {name} executed with: {arguments}"


async def _facebook_post_message(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Post message to Facebook"""
    try:
        import requests
        url = f"https://graph.facebook.com/v18.0/{config['facebook_page_id']}/feed"
        data = {
            'message': args.get('message', ''),
            'access_token': config['facebook_access_token']
        }
        if 'link' in args:
            data['link'] = args['link']

        response = requests.post(url, data=data)
        result = response.json()

        if 'id' in result:
            return [TextContent(type="text", text=f"Posted to Facebook!\nPost ID: {result['id']}")]
        return [TextContent(type="text", text=f"Post failed: {result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _facebook_post_photo(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Post photo to Facebook"""
    try:
        import requests
        url = f"https://graph.facebook.com/v18.0/{config['facebook_page_id']}/photos"
        data = {
            'url': args.get('photo_url', ''),
            'caption': args.get('caption', ''),
            'access_token': config['facebook_access_token']
        }
        response = requests.post(url, data=data)
        result = response.json()

        if 'id' in result:
            return [TextContent(type="text", text=f"Photo posted!\nID: {result['id']}")]
        return [TextContent(type="text", text=f"Failed: {result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _instagram_post_photo(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Post photo to Instagram via Graph API"""
    try:
        import requests

        # Create media container
        container_url = f"https://graph.facebook.com/v18.0/{config['instagram_user_id']}/media"
        container_data = {
            'image_url': args.get('image_url', ''),
            'caption': args.get('caption', ''),
            'access_token': config['facebook_access_token']
        }
        container_resp = requests.post(container_url, data=container_data)
        container_result = container_resp.json()

        if 'id' not in container_result:
            return [TextContent(type="text", text=f"Container creation failed: {container_result}")]

        # Publish
        publish_url = f"https://graph.facebook.com/v18.0/{config['instagram_user_id']}/media_publish"
        publish_data = {
            'creation_id': container_result['id'],
            'access_token': config['facebook_access_token']
        }
        publish_resp = requests.post(publish_url, data=publish_data)
        publish_result = publish_resp.json()

        if 'id' in publish_result:
            return [TextContent(type="text", text=f"Posted to Instagram!\nMedia ID: {publish_result['id']}")]
        return [TextContent(type="text", text=f"Publish failed: {publish_result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _instagram_post_carousel(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Post carousel to Instagram"""
    try:
        import requests
        image_urls = args.get('image_urls', [])

        if len(image_urls) < 2 or len(image_urls) > 10:
            return [TextContent(type="text", text="Carousel needs 2-10 images")]

        children_ids = []
        for img_url in image_urls:
            resp = requests.post(
                f"https://graph.facebook.com/v18.0/{config['instagram_user_id']}/media",
                data={
                    'image_url': img_url,
                    'is_carousel_item': 'true',
                    'access_token': config['facebook_access_token']
                }
            )
            result = resp.json()
            if 'id' in result:
                children_ids.append(result['id'])

        if not children_ids:
            return [TextContent(type="text", text="Failed to create carousel items")]

        # Create carousel
        carousel_resp = requests.post(
            f"https://graph.facebook.com/v18.0/{config['instagram_user_id']}/media",
            data={
                'media_type': 'CAROUSEL',
                'children': ','.join(children_ids),
                'caption': args.get('caption', ''),
                'access_token': config['facebook_access_token']
            }
        )
        carousel_result = carousel_resp.json()

        if 'id' not in carousel_result:
            return [TextContent(type="text", text=f"Carousel creation failed: {carousel_result}")]

        # Publish
        publish_resp = requests.post(
            f"https://graph.facebook.com/v18.0/{config['instagram_user_id']}/media_publish",
            data={
                'creation_id': carousel_result['id'],
                'access_token': config['facebook_access_token']
            }
        )
        publish_result = publish_resp.json()

        if 'id' in publish_result:
            return [TextContent(type="text", text=f"Carousel posted!\nID: {publish_result['id']}")]
        return [TextContent(type="text", text=f"Publish failed: {publish_result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _facebook_get_insights(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Get Facebook insights"""
    try:
        import requests
        url = f"https://graph.facebook.com/v18.0/{config['facebook_page_id']}/insights"
        params = {
            'metric': args.get('metric', 'page_impressions'),
            'period': args.get('period', 'week'),
            'access_token': config['facebook_access_token']
        }
        response = requests.get(url, params=params)
        result = response.json()

        if 'data' in result:
            text = "Facebook Insights:\n\n"
            for item in result['data']:
                text += f"- {item.get('name')}: {item.get('values', [{}])[0].get('value', 'N/A')}\n"
            return [TextContent(type="text", text=text)]
        return [TextContent(type="text", text=f"No insights: {result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _facebook_get_messages(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Get Facebook messages"""
    try:
        import requests
        url = f"https://graph.facebook.com/v18.0/{config['facebook_page_id']}/conversations"
        params = {
            'fields': 'messages{message,from,created_time}',
            'access_token': config['facebook_access_token']
        }
        response = requests.get(url, params=params)
        result = response.json()

        if 'data' in result:
            text = "Facebook Messages:\n\n"
            for conv in result['data'][:args.get('limit', 10)]:
                msgs = conv.get('messages', {}).get('data', [])
                for msg in msgs[:2]:
                    text += f"- {msg.get('from', {}).get('name', '?')}: {msg.get('message', '')[:80]}\n"
            return [TextContent(type="text", text=text)]
        return [TextContent(type="text", text="No messages")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _instagram_get_dms(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Get Instagram DMs"""
    return [TextContent(
        type="text",
        text="Instagram DM access requires special API permissions. Use Playwright automation for DM access."
    )]


async def _generate_social_summary(config: Dict, args: Dict[str, Any]) -> List[TextContent]:
    """Generate social summary"""
    platform = args.get('platform', 'both')
    period = args.get('period', 'week')

    summary = f"""# Social Media Summary
**Period:** {period}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

"""
    if platform in ['facebook', 'both']:
        summary += """## Facebook
- Check Page Insights for detailed metrics
- Review inbox for customer messages
- Monitor post engagement

"""
    if platform in ['instagram', 'both']:
        summary += """## Instagram
- Review recent post performance
- Check story analytics
- Monitor DMs for opportunities

"""
    summary += "*Use insight tools for detailed metrics*"

    return [TextContent(type="text", text=summary)]


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
