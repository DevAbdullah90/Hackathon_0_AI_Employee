#!/usr/bin/env python3
"""
Daily WhatsApp Update Script
Sends a daily business update to the target phone number
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.getcwd())

from src.generators.social_content_generator import SocialContentGenerator
from src.platforms.whatsapp.whatsapp_poster import WhatsAppPoster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/daily_whatsapp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting daily WhatsApp update...")
    
    # Get target phone
    target_phone = os.getenv("WHATSAPP_TARGET_PHONE")
    if not target_phone:
        logger.error("WHATSAPP_TARGET_PHONE not set in .env")
        return

    try:
        # Generate content
        logger.info("Generating daily update content...")
        generator = SocialContentGenerator()
        
        # You can customize the topic based on day of week if needed
        day_of_week = datetime.now().strftime("%A")
        topic = f"daily business update for {day_of_week}"
        
        result = generator.generate_whatsapp_message(topic=topic)
        message = result['content']
        
        logger.info(f"Generated message: {message}")
        
        # Send message
        logger.info(f"Sending to {target_phone}...")
        poster = WhatsAppPoster()
        post_result = poster.post_message(target_phone, message)
        
        if post_result['success']:
            logger.info("Daily update sent successfully")
        else:
            logger.error(f"Failed to send update: {post_result.get('error')}")
            
    except Exception as e:
        logger.error(f"Error in daily update: {e}", exc_info=True)

if __name__ == "__main__":
    main()
