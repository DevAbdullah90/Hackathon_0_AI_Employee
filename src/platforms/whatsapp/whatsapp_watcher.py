#!/usr/bin/env python3
"""
WhatsApp Watcher
Monitors WhatsApp for business opportunities and messages
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppWatcher:
    """Watches WhatsApp for business opportunities and messages"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_folder = self.vault_path / 'Logs'

        # Initialize WhatsApp MCP connection
        self.mcp_client = None
        self._initialize_mcp()

    def _initialize_mcp(self):
        """Initialize WhatsApp MCP connection"""
        try:
            # For now, we'll simulate monitoring by checking for pending messages
            # In a real implementation, this would connect to WhatsApp Web or API
            logger.info("WhatsApp watcher initialized")
        except Exception as e:
            logger.error(f"Error initializing WhatsApp watcher: {e}")

    def check_pending_messages(self) -> List[Dict[str, Any]]:
        """Check for pending WhatsApp messages in the system"""
        messages = []

        try:
            # Look for WhatsApp message files in Output directory
            output_dir = Path("Output/WhatsApp")
            if not output_dir.exists():
                return messages

            for file in output_dir.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)

                    # Check if this is a pending message that needs attention
                    if data.get('status') == 'pending':
                        messages.append({
                            'platform': 'whatsapp',
                            'type': 'pending_message',
                            'phone': data.get('phone'),
                            'message': data.get('message'),
                            'timestamp': datetime.fromtimestamp(data.get('timestamp', time.time())).isoformat(),
                            'filename': str(file),
                            'priority': self._determine_priority(data.get('message', '')),
                            'status': 'pending'
                        })
                except Exception as e:
                    logger.error(f"Error reading WhatsApp message file {file}: {e}")

            logger.info(f"Found {len(messages)} pending WhatsApp messages")

        except Exception as e:
            logger.error(f"Error checking pending WhatsApp messages: {e}")

        return messages

    def check_new_incoming_messages(self) -> List[Dict[str, Any]]:
        """Simulate checking for new incoming WhatsApp messages"""
        # Since we don't have a real WhatsApp API connection for incoming messages,
        # we'll simulate by looking for any new activity indicators
        # In a real implementation, this would use WhatsApp Business API or WhatsApp Web

        messages = []

        try:
            # For simulation purposes, we'll look for any recent WhatsApp-related activity
            # This could be extended to integrate with WhatsApp Business API in the future
            logger.info("Checking for new WhatsApp messages (simulated)")

            # Placeholder for real implementation
            # This would connect to WhatsApp Business API or WhatsApp Web to read incoming messages

        except Exception as e:
            logger.error(f"Error checking new WhatsApp messages: {e}")

        return messages

    def search_business_opportunities(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Search for WhatsApp business opportunities"""
        opportunities = []

        if not keywords:
            keywords = ['business', 'opportunity', 'meeting', 'collaboration',
                       'partnership', 'project', 'consultation', 'service']

        try:
            # In a real implementation, this would search WhatsApp groups, broadcasts, etc.
            # For now, we'll check for any WhatsApp messages containing these keywords
            pending_messages = self.check_pending_messages()

            for msg in pending_messages:
                message_text = msg.get('message', '').lower()
                if any(keyword in message_text for keyword in keywords):
                    opportunities.append({
                        'platform': 'whatsapp',
                        'type': 'business_opportunity',
                        'search_keyword': 'business opportunity',
                        'phone': msg.get('phone'),
                        'message': msg.get('message'),
                        'timestamp': msg.get('timestamp'),
                        'priority': 'high'
                    })

            logger.info(f"Found {len(opportunities)} WhatsApp business opportunities")

        except Exception as e:
            logger.error(f"Error searching WhatsApp opportunities: {e}")

        return opportunities

    def _determine_priority(self, text: str) -> str:
        """Determine priority based on keywords"""
        text = text.lower()

        high_priority_keywords = ['urgent', 'asap', 'payment', 'invoice', 'problem',
                                 'issue', 'error', 'broken', 'help', 'need', 'looking',
                                 'recommend', 'quote', 'price', 'important']
        low_priority_keywords = ['thanks', 'thank you', 'great', 'awesome', 'love', 'hello']

        if any(keyword in text for keyword in high_priority_keywords):
            return 'high'
        elif any(keyword in text for keyword in low_priority_keywords):
            return 'low'
        else:
            return 'medium'

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create action file in Needs_Action folder"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            platform = item['platform']
            message_type = item['type']

            # Create filename with platform prefix
            filename = f"WHATSAPP_{timestamp}_{message_type.replace(' ', '_').replace('-', '_')}.md"
            filepath = self.needs_action / filename

            content = self._generate_whatsapp_content(item)
            filepath.write_text(content)
            logger.info(f"Created WhatsApp action file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating WhatsApp action file: {e}")
            return None

    def _generate_whatsapp_content(self, item: Dict[str, Any]) -> str:
        """Generate content for WhatsApp action file"""
        platform = item['platform'].capitalize()
        message_type = item['type'].replace('_', ' ').title()

        content = f"""---
type: communication
platform: {platform}
message_type: {item['type']}
priority: {item['priority']}
received: {item.get('timestamp', datetime.now().isoformat())}
status: pending
---

## {platform} {message_type}

**Platform**: {platform}
**Type**: {message_type}
**Priority**: {item['priority']}
**Received**: {item.get('timestamp', datetime.now().isoformat())}

"""

        if item['type'] == 'pending_message':
            content += f"""## Pending Message Details

**Phone Number**: {item.get('phone')}
**Message**: {item.get('message', 'No message text')}

## Suggested Actions
- [ ] Review message content
- [ ] Verify sender information
- [ ] Process message appropriately
- [ ] Update message status in system
"""

        elif item['type'] == 'business_opportunity':
            content += f"""## Business Opportunity Details

**Phone Number**: {item.get('phone')}
**Message**: {item.get('message', 'No message text')}
**Opportunity Type**: Business Opportunity

## Suggested Actions
- [ ] Review opportunity details
- [ ] Assess business potential
- [ ] Determine follow-up strategy
- [ ] Schedule outreach if appropriate
"""

        elif item['type'] == 'incoming_message':
            content += f"""## Incoming Message Details

**Phone Number**: {item.get('phone')}
**Message**: {item.get('message', 'No message text')}
**Timestamp**: {item.get('timestamp')}

## Suggested Actions
- [ ] Read message in context
- [ ] Respond appropriately
- [ ] Log interaction
- [ ] Create follow-up task if needed
"""

        return content

    def run_continuous(self, check_interval: int = 300):
        """Run watcher continuously"""
        logger.info(f"Starting WhatsApp watcher (interval: {check_interval}s)")

        while True:
            try:
                # Check for WhatsApp activity
                pending_msgs = self.check_pending_messages()
                for msg in pending_msgs:
                    self.create_action_file(msg)

                new_msgs = self.check_new_incoming_messages()
                for msg in new_msgs:
                    self.create_action_file(msg)

                # Check for business opportunities periodically
                if datetime.now().minute % 15 == 0:  # Every 15 minutes
                    opportunities = self.search_business_opportunities()
                    for opportunity in opportunities:
                        self.create_action_file(opportunity)

                logger.info("WhatsApp check complete, sleeping...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("WhatsApp watcher stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in WhatsApp watcher: {e}")
                time.sleep(60)

    def run_once(self):
        """Run a single check"""
        try:
            logger.info("Running WhatsApp check")

            all_items = []

            # Check for pending messages
            pending_msgs = self.check_pending_messages()
            all_items.extend(pending_msgs)

            # Check for new incoming messages
            new_msgs = self.check_new_incoming_messages()
            all_items.extend(new_msgs)

            # Check for business opportunities occasionally
            last_opportunity_check = self.vault_path / '.last_whatsapp_opportunity_check'
            should_check_opportunities = True

            if last_opportunity_check.exists():
                last_time = datetime.fromtimestamp(last_opportunity_check.stat().st_mtime)
                if (datetime.now() - last_time).seconds < 1800:  # Check every 30 min
                    should_check_opportunities = False

            if should_check_opportunities:
                opportunities = self.search_business_opportunities()
                all_items.extend(opportunities)
                last_opportunity_check.touch()

            files_created = []
            for item in all_items:
                filepath = self.create_action_file(item)
                if filepath:
                    files_created.append(str(filepath))

            logger.info(f"Created {len(files_created)} WhatsApp action files")
            return files_created

        except Exception as e:
            logger.error(f"Error in WhatsApp run_once: {e}")
            return []


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher')
    parser.add_argument('--vault', type=str, help='Path to vault', default=None)
    parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    vault_path = args.vault or os.getcwd()

    watcher = WhatsAppWatcher(vault_path)

    if args.once:
        result = watcher.run_once()
        print(json.dumps(result, indent=2))
    else:
        watcher.run_continuous()


if __name__ == "__main__":
    main()