"""
Dynamic Inbox Processor generated from inbox_processor.md skill definition
"""
import os
import json
import datetime
import shutil
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

class ProcessingResult(Enum):
    NEEDS_ACTION = "Needs_Action"
    DONE = "Done"
    QUARANTINE = "Quarantine"
    PENDING = "Pending"

class UrgencyLevel(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class InboxProcessor:
    """
    The Inbox Processor handles incoming items from the Inbox folder and determines their next action
    based on content analysis and predefined rules.
    """

    def __init__(self):
        # Configuration variables from skill definition
        self.MONITORED_KEYWORDS = ["urgent", "invoice", "payment", "opportunity", "hackathon"]
        self.FINANCIAL_KEYWORDS = ["invoice", "payment", "bill", "amount", "cost", "fee", "charge", "expense"]
        self.URGENT_KEYWORDS = ["urgent", "asap", "immediate", "today", "now"]
        self.SECURITY_CHECKS = True

        # Pre-requisites validation
        self.validate_prerequisites()

    def validate_prerequisites(self):
        """
        Validate prerequisites:
        - Inbox folder exists
        - Company_Handbook.md is accessible
        - Logs folder is writable
        - Dashboard is accessible
        """
        # Check if required folders exist
        required_dirs = ["Inbox", "Needs_Action", "Done", "Logs", "Quarantine"]
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

        # Check if Company_Handbook.md exists
        if not os.path.exists("Company_Handbook.md"):
            print("Warning: Company_Handbook.md not found")

    def check_inbox_for_new_items(self) -> List[str]:
        """
        Check Inbox for new items
        """
        inbox_path = "Inbox"
        if not os.path.exists(inbox_path):
            return []

        items = []
        for filename in os.listdir(inbox_path):
            if os.path.isfile(os.path.join(inbox_path, filename)):
                items.append(filename)

        return items

    def analyze_item_content(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze item content and metadata
        """
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))

        # Analyze content
        analysis = {
            'content': content,
            'filename': file_name,
            'file_size': file_size,
            'creation_time': creation_time,
            'contains_urgent': self.contains_keywords(content, self.URGENT_KEYWORDS),
            'contains_financial': self.contains_keywords(content, self.FINANCIAL_KEYWORDS),
            'contains_monitored': self.contains_keywords(content, self.MONITORED_KEYWORDS),
            'suspicious_indicators': self.check_suspicious_content(content),
            'urgency_level': self.assess_urgency(content),
            'item_type': self.classify_item_type(content)
        }

        return analysis

    def contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the specified keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    def check_suspicious_content(self, content: str) -> List[str]:
        """Check for suspicious content indicators"""
        suspicious_patterns = [
            r'[0-9]{10,}',  # Long sequences of numbers
            r'(click here|act now|limited time|urgent attention)',
            r'(verify account|suspicious activity)',
            r'(password|login|account|credentials).*?(information|required)'
        ]

        suspicious_indicators = []
        for pattern in suspicious_patterns:
            import re
            if re.search(pattern, content, re.IGNORECASE):
                suspicious_indicators.append(pattern)

        return suspicious_indicators

    def assess_urgency(self, content: str) -> UrgencyLevel:
        """Assess urgency level based on content"""
        content_lower = content.lower()

        # Check for critical urgency
        critical_indicators = ['urgent', 'asap', 'immediate action', 'critical']
        if any(indicator in content_lower for indicator in critical_indicators):
            return UrgencyLevel.CRITICAL

        # Check for high urgency
        high_indicators = ['today', 'now', 'within 24 hours', 'expedited']
        if any(indicator in content_lower for indicator in high_indicators):
            return UrgencyLevel.HIGH

        # Check for medium urgency
        medium_indicators = ['soon', 'this week', 'needed', 'required']
        if any(indicator in content_lower for indicator in medium_indicators):
            return UrgencyLevel.MEDIUM

        # Default to low urgency
        return UrgencyLevel.LOW

    def classify_item_type(self, content: str) -> str:
        """Classify the type of item based on content"""
        content_lower = content.lower()

        if any(keyword in content_lower for keyword in ['invoice', 'payment', 'bill', 'financial']):
            return 'financial'
        elif any(keyword in content_lower for keyword in ['urgent', 'asap', 'immediate']):
            return 'urgent'
        elif any(keyword in content_lower for keyword in ['opportunity', 'offer', 'deal']):
            return 'opportunity'
        elif any(keyword in content_lower for keyword in ['meeting', 'schedule', 'appointment']):
            return 'operational'
        else:
            return 'routine'

    def apply_workflow_rules(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply workflow rules from Company_Handbook.md to determine next action
        """
        # Default action
        result = {
            'next_action': ProcessingResult.DONE,
            'folder_destination': 'Done',
            'requires_attention': False,
            'requires_approval': False,
            'security_flag': False,
            'priority': 'normal'
        }

        # Rule: Items containing "urgent" → Prioritize and route to Needs_Action
        if analysis['contains_urgent']:
            result.update({
                'next_action': ProcessingResult.NEEDS_ACTION,
                'folder_destination': 'Needs_Action',
                'requires_attention': True,
                'priority': 'high'
            })

        # Rule: Items containing "invoice" → Flag for financial review
        elif analysis['contains_financial']:
            result.update({
                'next_action': ProcessingResult.NEEDS_ACTION,
                'folder_destination': 'Needs_Action',
                'requires_attention': True,
                'requires_approval': True,
                'priority': 'medium'
            })

        # Rule: Items with payment references → Check against financial limits
        elif self.contains_keywords(analysis['content'], ['payment', 'transaction', 'transfer']):
            result.update({
                'next_action': ProcessingResult.NEEDS_ACTION,
                'folder_destination': 'Needs_Action',
                'requires_attention': True,
                'requires_approval': True,
                'priority': 'medium'
            })

        # Rule: Suspicious content → Quarantine
        if analysis['suspicious_indicators']:
            result.update({
                'next_action': ProcessingResult.QUARANTINE,
                'folder_destination': 'Quarantine',
                'security_flag': True,
                'requires_attention': True,
                'priority': 'critical'
            })

        # Rule: Routine communications → Move to Done or archive
        if analysis['item_type'] == 'routine' and not analysis['contains_monitored']:
            result.update({
                'next_action': ProcessingResult.DONE,
                'folder_destination': 'Done',
                'requires_attention': False,
                'priority': 'low'
            })

        return result

    def move_item_to_folder(self, source_path: str, destination_folder: str) -> bool:
        """
        Move item to appropriate folder (Needs_Action, Done, etc.)
        """
        try:
            destination_path = os.path.join(destination_folder, os.path.basename(source_path))
            shutil.move(source_path, destination_path)
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False

    def log_action(self, analysis: Dict[str, Any], action_result: Dict[str, Any], original_path: str):
        """
        Log the action in the system logs
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"""{timestamp} - INBOX_PROCESSOR - PROCESSED - {analysis['filename']} - {action_result['folder_destination']}
- Content Type: {analysis['item_type']}
- Urgency Level: {analysis['urgency_level'].value}
- Contains Urgent: {analysis['contains_urgent']}
- Contains Financial: {analysis['contains_financial']}
- Security Flag: {action_result['security_flag']}
- Priority: {action_result['priority']}
- Result: Success
"""

        # Write to log file
        log_file_path = "Logs/inbox_processor.log"
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry + "\n")

    def update_dashboard_statistics(self, action_result: Dict[str, Any]):
        """
        Update dashboard statistics
        """
        # Read current dashboard
        dashboard_path = "Dashboard.md"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()

            # Update statistics based on action
            if action_result['folder_destination'] == 'Needs_Action':
                # Increment Needs_Action counter
                import re
                stats_match = re.search(r'- 📋 Tasks in Need Action: (\d+)', dashboard_content)
                if stats_match:
                    current_count = int(stats_match.group(1))
                    new_count = current_count + 1
                    dashboard_content = re.sub(
                        r'- 📋 Tasks in Need Action: \d+',
                        f'- 📋 Tasks in Need Action: {new_count}',
                        dashboard_content
                    )

            # Write updated dashboard
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)

    def process_single_item(self, filename: str) -> Dict[str, Any]:
        """
        Process a single item from the inbox
        """
        inbox_path = "Inbox"
        file_path = os.path.join(inbox_path, filename)

        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f"File {filename} does not exist",
                'item_processed': filename
            }

        try:
            # Step 1: Analyze item content and metadata
            analysis = self.analyze_item_content(file_path)

            # Step 2: Apply workflow rules
            action_result = self.apply_workflow_rules(analysis)

            # Step 3: Move item to appropriate folder
            move_success = self.move_item_to_folder(file_path, action_result['folder_destination'])

            if move_success:
                # Step 4: Log the action
                self.log_action(analysis, action_result, file_path)

                # Step 5: Update dashboard statistics
                self.update_dashboard_statistics(action_result)

                return {
                    'success': True,
                    'item_processed': filename,
                    'analysis': analysis,
                    'action_taken': action_result,
                    'destination_folder': action_result['folder_destination']
                }
            else:
                return {
                    'success': False,
                    'error': "Failed to move item",
                    'item_processed': filename
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'item_processed': filename
            }

    def process_inbox(self) -> Dict[str, Any]:
        """
        Main method to process all items in the inbox
        """
        items = self.check_inbox_for_new_items()

        if not items:
            return {
                'success': True,
                'message': 'No new items in inbox',
                'items_processed': 0
            }

        results = []
        successful_count = 0

        for item in items:
            result = self.process_single_item(item)
            results.append(result)
            if result['success']:
                successful_count += 1

        return {
            'success': True,
            'items_processed': len(items),
            'successful_processing': successful_count,
            'failed_processing': len(items) - successful_count,
            'processing_results': results
        }


# Example usage:
if __name__ == "__main__":
    # Initialize the inbox processor
    processor = InboxProcessor()

    # Process all items in the inbox
    result = processor.process_inbox()

    print("Inbox Processing Result:")
    print(json.dumps(result, indent=2, default=str))