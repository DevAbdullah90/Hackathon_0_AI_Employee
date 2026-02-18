#!/usr/bin/env python3
"""
Verify WhatsApp Integration
"""
import sys
import argparse
from whatsapp_poster import WhatsAppPoster
from social_content_generator import SocialContentGenerator

def main():
    parser = argparse.ArgumentParser(description='Verify WhatsApp Integration')
    parser.add_argument('--phone', help='Target phone number (e.g. 1234567890)')
    parser.add_argument('--message', help='Message to send')
    
    args = parser.parse_args()
    
    if not args.phone:
        print("Please provide a phone number with country code (e.g., 923001234567)")
        args.phone = input("Enter phone number: ")
        
    print(f"Generating message for {args.phone}...")
    
    if not args.message:
        generator = SocialContentGenerator()
        result = generator.generate_whatsapp_message(topic="AI integration test")
        message = result['content']
        print(f"Generated message: {message}")
    else:
        message = args.message
        
    print(f"Launch WhatsApp Poster...")
    print("NOTE: You may need to scan the QR code if this is your first time.")
    
    poster = WhatsAppPoster()
    result = poster.post_message(args.phone, message)
    
    print("\nResult:")
    print(result)

if __name__ == "__main__":
    main()
