#!/usr/bin/env python3
"""
Create Simple Test Posts for User Verification
Creates one Instagram post, one LinkedIn post, and one WhatsApp reply for testing
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

def create_test_posts():
    """Create test posts as requested by user"""
    print("Creating test posts as requested by user...")
    print("1 Instagram post, 1 LinkedIn post, 1 WhatsApp reply")

    vault_path = Path("C:/Users/LENOVO X1 YOGA/OneDrive/Desktop/hakathone zero/AI_Employee_vault")

    # Create in Needs_Action folder to trigger the workflow
    needs_action_path = vault_path / "Needs_Action"
    needs_action_path.mkdir(exist_ok=True)

    timestamp = int(datetime.now().timestamp())

    # 1. Create Instagram post
    instagram_post = f"""---
type: social_post
platform: instagram
scheduled_time: {datetime.now().isoformat()}
status: needs_approval
priority: medium
author: claude_code
category: business_update
tags: ["ai", "automation", "business"]
---

# Platinum Tier Achievement!

We've reached a major milestone in AI employee development! Our system now operates at the Platinum tier with:

Cross-domain integration (Personal + Business)
Odoo Community accounting system
Multi-platform social media management
Cloud + Local work-zone specialization
24/7 autonomous operation

The future of business automation is here! Our AI employee handles everything from accounting to customer engagement.

AI Automation Business Innovation PlatinumTier
"""

    instagram_file = needs_action_path / f"INSTAGRAM_TEST_POST_{timestamp}.md"
    with open(instagram_file, 'w', encoding='utf-8') as f:
        f.write(instagram_post)

    print(f"SUCCESS: Created Instagram test post: {instagram_file.name}")

    # 2. Create LinkedIn post
    linkedin_post = f"""---
type: social_post
platform: linkedin
scheduled_time: {datetime.now().isoformat()}
status: needs_approval
priority: high
author: claude_code
category: business_news
tags: ["ai", "automation", "employee", "business"]
---

Exciting News: AI Employee Platinum Tier Achieved!

We're thrilled to announce that our AI Employee system has reached Platinum Tier status! This represents a major advancement in autonomous business operations.

What's New:
• Full cross-domain integration (Personal + Business operations)
• Integrated Odoo Community accounting system with MCP
• Multi-platform social media management (Facebook, Instagram, Twitter, LinkedIn)
• Cloud + Local work-zone specialization for optimal performance
• 24/7 autonomous operation with human-in-the-loop safety

Key Features:
• Automated accounting and invoicing
• Customer engagement across all channels
• Real-time business intelligence and reporting
• Secure approval workflows for sensitive actions
• Seamless cloud-local synchronization

The future of work is here - where AI handles routine tasks while humans focus on strategy and creativity.

What are your thoughts on AI employees in business operations? We'd love to hear your perspective!

AI ArtificialIntelligence Automation Business Innovation FutureOfWork PlatinumTier Tech
"""

    linkedin_file = needs_action_path / f"LINKEDIN_TEST_POST_{timestamp}.md"
    with open(linkedin_file, 'w', encoding='utf-8') as f:
        f.write(linkedin_post)

    print(f"SUCCESS: Created LinkedIn test post: {linkedin_file.name}")

    # 3. Create WhatsApp reply
    whatsapp_reply = f"""---
type: communication_reply
platform: whatsapp
timestamp: {datetime.now().isoformat()}
status: needs_approval
priority: high
author: claude_code
category: customer_inquiry
tags: ["reply", "customer_service", "urgent"]
---

Hello! Thank you for reaching out about our Platinum Tier AI Employee system.

Yes, we've successfully implemented the full Platinum tier with:
• 24/7 autonomous operation
• Multi-platform social media management
• Integrated accounting via Odoo
• Cloud + Local work-zone specialization
• Human-in-the-loop safety protocols

Would you like to learn more about how this could benefit your business operations?

Best regards,
AI Employee System
"""

    whatsapp_file = needs_action_path / f"WHATSAPP_TEST_REPLY_{timestamp}.md"
    with open(whatsapp_file, 'w', encoding='utf-8') as f:
        f.write(whatsapp_reply)

    print(f"SUCCESS: Created WhatsApp test reply: {whatsapp_file.name}")

    # Create a summary report
    summary = {
        "timestamp": datetime.now().isoformat(),
        "test_posts_created": 3,
        "posts": [
            {"type": "instagram", "file": instagram_file.name, "status": "created"},
            {"type": "linkedin", "file": linkedin_file.name, "status": "created"},
            {"type": "whatsapp", "file": whatsapp_file.name, "status": "created"}
        ],
        "instructions": "These posts are now in Needs_Action folder and will be processed through the approval workflow and MCP servers when they are running with proper credentials."
    }

    summary_file = vault_path / "test_posts_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"REPORT: Test posts summary saved to: {summary_file}")
    print("TARGET: TEST POSTS CREATED SUCCESSFULLY!")
    print("The 3 test posts (Instagram, LinkedIn, WhatsApp) are now in the Needs_Action folder")
    print("They will be processed through the approval workflow when MCP servers are running with credentials")

    return True

if __name__ == "__main__":
    success = create_test_posts()
    if success:
        print("\nALL REQUESTED TEST POSTS HAVE BEEN CREATED!")
        print("1 Instagram post, 1 LinkedIn post, and 1 WhatsApp reply are ready for processing.")
    else:
        print("\nError creating test posts")

    sys.exit(0 if success else 1)