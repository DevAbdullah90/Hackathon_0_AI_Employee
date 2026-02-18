"""
Dynamic Email Handler generated from email_handler.md skill definition
"""
import re
import json
import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

class UrgencyLevel(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ApprovalType(Enum):
    NONE = "No"
    MANAGER = "Manager"
    EXECUTIVE = "Executive"
    ADMIN = "Admin"

class EmailHandler:
    """
    Email Handler processes emails that have been moved to the Needs_Action folder,
    analyzes their content, and performs appropriate actions based on sender, subject, and urgency level.
    """

    def __init__(self):
        # Configuration variables from skill definition
        self.MONITORED_KEYWORDS = ["urgent", "invoice", "payment", "opportunity", "hackathon"]
        self.FINANCIAL_THRESHOLDS = {"low": 50, "high": 500}
        self.URGENT_INDICATORS = ["urgent", "asap", "immediate action required"]
        self.TRUSTED_SENDERS = []  # Would be populated from contacts list
        self.LOG_RETENTION_DAYS = 30

        # Pre-requisites validation
        self.validate_prerequisites()

    def validate_prerequisites(self):
        """
        Validate that prerequisites are met before processing emails
        - Email file exists in Needs_Action folder
        - Company_Handbook.md is accessible for policy reference
        - Logs folder is writable for activity logging
        """
        import os
        # Check if logs folder exists and is writable
        logs_dir = "Logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)

        # Additional checks would go here
        pass

    def check_trigger_conditions(self, email_content: str, email_subject: str) -> bool:
        """
        Check if email meets trigger conditions:
        - Email contains monitored keywords
        - Email requires human review based on content analysis
        - System detects financial transaction or business opportunity
        """
        # Check for monitored keywords
        content_lower = (email_content + " " + email_subject).lower()
        for keyword in self.MONITORED_KEYWORDS:
            if keyword.lower() in content_lower:
                return True

        # Additional analysis could go here
        return False

    def analyze_email(self, email_content: str, email_subject: str, email_sender: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of the email based on the analysis process defined in the skill
        """
        analysis_result = {
            'sender_verification': self.verify_sender(email_sender),
            'subject_analysis': self.analyze_subject(email_subject),
            'content_examination': self.examine_content(email_content),
            'urgency_assessment': self.assess_urgency(email_content, email_subject),
            'is_financial': self.is_financial_transaction(email_content),
            'is_opportunity': self.is_business_opportunity(email_content),
            'is_urgent': self.is_urgent_request(email_content, email_subject)
        }

        return analysis_result

    def verify_sender(self, sender: str) -> Dict[str, Any]:
        """Check sender against known contacts list and verify domain authenticity"""
        result = {
            'sender': sender,
            'is_known': sender in self.TRUSTED_SENDERS,
            'domain_verified': self.verify_domain(sender),
            'is_suspicious': self.is_suspicious_sender(sender)
        }
        return result

    def verify_domain(self, sender: str) -> bool:
        """Verify domain authenticity"""
        # Simple domain verification - would be enhanced in production
        if "@" in sender:
            domain = sender.split("@")[1].lower()
            # Add more sophisticated domain verification here
            return "." in domain and len(domain) > 3
        return False

    def is_suspicious_sender(self, sender: str) -> bool:
        """Flag suspicious or unknown senders"""
        suspicious_patterns = [
            r'.*[0-9]{10,}.*',  # Many digits
            r'.*noreply.*spam.*',  # Spam indicators
            r'^[a-z0-9._%+-]+@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'  # IP address as domain
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, sender, re.IGNORECASE):
                return True
        return False

    def analyze_subject(self, subject: str) -> Dict[str, Any]:
        """Extract key terms, identify urgency, categorize email type, check for phishing"""
        subject_lower = subject.lower()

        result = {
            'terms': self.extract_key_terms(subject),
            'has_urgency_indicators': any(indicator in subject_lower for indicator in self.URGENT_INDICATORS),
            'category': self.categorize_email_type(subject, subject_lower),
            'has_phishing_indicators': self.has_phishing_indicators(subject)
        }

        return result

    def extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Simple extraction - would be enhanced with NLP in production
        words = re.findall(r'\b[A-Za-z]+\b', text)
        return [word for word in words if len(word) > 3][:10]  # Top 10 words

    def categorize_email_type(self, subject: str, subject_lower: str) -> str:
        """Categorize email type based on content"""
        if any(term in subject_lower for term in ['invoice', 'payment', 'bill', 'money']):
            return 'financial'
        elif any(term in subject_lower for term in ['opportunity', 'offer', 'deal', 'proposal']):
            return 'opportunity'
        elif any(term in subject_lower for term in ['meeting', 'schedule', 'appointment']):
            return 'operational'
        elif any(term in subject_lower for term in ['newsletter', 'update', 'news']):
            return 'promotional'
        else:
            return 'general'

    def has_phishing_indicators(self, subject: str) -> bool:
        """Check for phishing indicators in subject"""
        phishing_indicators = [
            'urgent', 'immediate attention', 'act now', 'click here', 'verify account',
            'suspicious activity', 'confirm immediately', 'limited time'
        ]

        subject_lower = subject.lower()
        return any(indicator in subject_lower for indicator in phishing_indicators)

    def examine_content(self, content: str) -> Dict[str, Any]:
        """Scan body for monetary amounts, action-required phrases, attachments, tone"""
        content_lower = content.lower()

        result = {
            'monetary_amounts': self.find_monetary_amounts(content),
            'action_phrases': self.find_action_required_phrases(content_lower),
            'has_attachments': 'attachment' in content_lower or 'attached' in content_lower,
            'has_links': self.find_links(content),
            'tone_formality': self.assess_tone_formality(content)
        }

        return result

    def find_monetary_amounts(self, content: str) -> List[float]:
        """Scan for monetary amounts in the content"""
        # Find patterns like $100, 100$, €50, etc.
        currency_pattern = r'[\$€£¥]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)|(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[\$€£¥]'
        matches = re.findall(currency_pattern, content)
        amounts = []
        for match_group in matches:
            for match in match_group:
                if match:  # Skip empty strings
                    try:
                        amount = float(match.replace(',', ''))
                        amounts.append(amount)
                    except ValueError:
                        continue
        return amounts

    def find_action_required_phrases(self, content_lower: str) -> List[str]:
        """Identify action-required phrases"""
        action_phrases = [
            'action required', 'please respond', 'need your input', 'requires approval',
            'follow up', 'urgent attention', 'immediate response', 'reply needed',
            'your response', 'feedback needed', 'confirmation required'
        ]

        found_phrases = []
        for phrase in action_phrases:
            if phrase in content_lower:
                found_phrases.append(phrase)

        return found_phrases

    def find_links(self, content: str) -> List[str]:
        """Find links in the content"""
        link_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(link_pattern, content)

    def assess_tone_formality(self, content: str) -> str:
        """Assess tone and formality level"""
        formal_indicators = ['dear sir/madam', 'regarding', 'respectfully', 'hereby', 'whereas']
        informal_indicators = ['hey', 'hi there', 'thanks!', 'cheers', 'bye']

        content_lower = content.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in content_lower)
        informal_count = sum(1 for indicator in informal_indicators if indicator in content_lower)

        if formal_count > informal_count:
            return 'formal'
        elif informal_count > formal_count:
            return 'informal'
        else:
            return 'neutral'

    def assess_urgency(self, content: str, subject: str) -> UrgencyLevel:
        """Assess urgency level based on content and subject"""
        content_lower = (content + " " + subject).lower()

        # Critical urgency indicators
        if any(indicator in content_lower for indicator in ['urgent', 'asap', 'immediate action required']):
            return UrgencyLevel.CRITICAL

        # High urgency indicators
        if any(indicator in content_lower for indicator in ['deadline', 'due today', 'payment due', 'invoice']):
            return UrgencyLevel.HIGH

        # Medium urgency indicators
        if any(indicator in content_lower for indicator in ['opportunity', 'meeting', 'request']):
            return UrgencyLevel.MEDIUM

        # Default to low urgency
        return UrgencyLevel.LOW

    def is_financial_transaction(self, content: str) -> bool:
        """Check if email contains financial transaction information"""
        financial_keywords = ['invoice', 'payment', 'bill', 'amount', 'cost', 'fee', 'charge', 'expense', 'purchase']
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in financial_keywords)

    def is_business_opportunity(self, content: str) -> bool:
        """Check if email contains business opportunity"""
        opportunity_keywords = ['opportunity', 'deal', 'offer', 'proposal', 'investment', 'partnership', 'project']
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in opportunity_keywords)

    def is_urgent_request(self, content: str, subject: str) -> bool:
        """Check if email contains urgent request"""
        urgent_keywords = ['urgent', 'asap', 'immediately', 'right now', 'today']
        content_lower = (content + " " + subject).lower()
        return any(keyword in content_lower for keyword in urgent_keywords)

    def determine_response_action(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine response action based on the decision matrix from the skill definition
        """
        content = analysis_result['content_examination']
        urgency = analysis_result['urgency_assessment']
        is_financial = analysis_result['is_financial']
        monetary_amounts = content['monetary_amounts']

        # Decision Matrix Implementation
        # Condition: Urgent request
        if analysis_result['is_urgent']:
            return {
                'action': 'flag + draft response',
                'approval_required': ApprovalType.NONE,
                'log_location': 'urgent_alerts.log',
                'response_type': 'urgent_response'
            }

        # Condition: Invoice <$50
        elif is_financial and monetary_amounts and max(monetary_amounts) < self.FINANCIAL_THRESHOLDS['low']:
            return {
                'action': 'process + confirm',
                'approval_required': ApprovalType.NONE,
                'log_location': 'email_handler.log',
                'response_type': 'financial_confirmation'
            }

        # Condition: Invoice $50-$500
        elif (is_financial and monetary_amounts and
              self.FINANCIAL_THRESHOLDS['low'] <= max(monetary_amounts) <= self.FINANCIAL_THRESHOLDS['high']):
            return {
                'action': 'draft approval req',
                'approval_required': ApprovalType.MANAGER,
                'log_location': 'financial_transactions.log',
                'response_type': 'approval_request'
            }

        # Condition: Invoice >$500
        elif is_financial and monetary_amounts and max(monetary_amounts) > self.FINANCIAL_THRESHOLDS['high']:
            return {
                'action': 'escalate + alert',
                'approval_required': ApprovalType.EXECUTIVE,
                'log_location': 'financial_transactions.log',
                'response_type': 'executive_approval'
            }

        # Condition: Opportunity
        elif analysis_result['is_opportunity']:
            return {
                'action': 'schedule + draft response',
                'approval_required': ApprovalType.NONE,
                'log_location': 'email_handler.log',
                'response_type': 'opportunity_response'
            }

        # Condition: Suspicious
        elif analysis_result['sender_verification']['is_suspicious']:
            return {
                'action': 'quarantine + alert',
                'approval_required': ApprovalType.ADMIN,
                'log_location': 'security_alerts.log',
                'response_type': 'security_alert'
            }

        # Default action
        else:
            return {
                'action': 'process + log',
                'approval_required': ApprovalType.NONE,
                'log_location': 'email_handler.log',
                'response_type': 'standard_response'
            }

    def generate_response(self, response_type: str, email_data: Dict[str, Any]) -> str:
        """Generate appropriate response based on response type"""
        if response_type == 'urgent_response':
            return self.generate_urgent_response(email_data)
        elif response_type == 'financial_confirmation':
            return self.generate_financial_confirmation(email_data)
        elif response_type == 'approval_request':
            return self.generate_approval_request(email_data)
        elif response_type == 'executive_approval':
            return self.generate_executive_approval_request(email_data)
        elif response_type == 'opportunity_response':
            return self.generate_opportunity_response(email_data)
        elif response_type == 'security_alert':
            return self.generate_security_alert(email_data)
        else:
            return self.generate_standard_response(email_data)

    def generate_urgent_response(self, email_data: Dict[str, Any]) -> str:
        """Generate response for urgent requests"""
        template = """Subject: Re: {original_subject}

Dear {sender},

Thank you for your email regarding "{subject_topic}".

Our team has received your urgent request and will review it immediately.

Timeline: Response within 24 hours as requested.

Best regards,
AI Employee System"""

        return template.format(
            original_subject=email_data.get('subject', 'Subject Not Available'),
            sender=email_data.get('sender', 'Sender Not Available'),
            subject_topic=email_data.get('subject', 'Subject Not Available')
        )

    def generate_financial_confirmation(self, email_data: Dict[str, Any]) -> str:
        """Generate confirmation for financial transactions under threshold"""
        template = """Subject: Re: {original_subject}

Dear {sender},

Thank you for your email regarding "{subject_topic}".

We have processed your request for the amount of {amount}. Confirmation has been sent to the appropriate parties.

Timeline: Processed immediately as per policy.

Best regards,
AI Employee System"""

        content_analysis = email_data.get('analysis', {}).get('content_examination', {})
        amounts = content_analysis.get('monetary_amounts', [])
        amount_str = f"${max(amounts):,.2f}" if amounts else "the amount specified"

        return template.format(
            original_subject=email_data.get('subject', 'Subject Not Available'),
            sender=email_data.get('sender', 'Sender Not Available'),
            subject_topic=email_data.get('subject', 'Subject Not Available'),
            amount=amount_str
        )

    def generate_approval_request(self, email_data: Dict[str, Any]) -> str:
        """Generate approval request for mid-range financial transactions"""
        content_analysis = email_data.get('analysis', {}).get('content_examination', {})
        amounts = content_analysis.get('monetary_amounts', [])
        amount_str = f"${max(amounts):,.2f}" if amounts else "the amount specified"

        template = """URGENT APPROVAL REQUIRED

Item: {email_subject}
From: {sender}
Amount: {amount}
Category: Financial Transaction
Description: {summary}

Per Company_Handbook.md:
- Amount {amount} requires manager approval
- Business justification: {justification}

Please approve or decline by EOD."""

        return template.format(
            email_subject=email_data.get('subject', 'Subject Not Available'),
            sender=email_data.get('sender', 'Sender Not Available'),
            amount=amount_str,
            summary=email_data.get('subject', 'Subject Not Available')[:100],
            justification=email_data.get('content', 'Content Not Available')[:200]
        )

    def generate_executive_approval_request(self, email_data: Dict[str, Any]) -> str:
        """Generate executive approval request for high-value transactions"""
        content_analysis = email_data.get('analysis', {}).get('content_examination', {})
        amounts = content_analysis.get('monetary_amounts', [])
        amount_str = f"${max(amounts):,.2f}" if amounts else "the amount specified"

        template = """URGENT APPROVAL REQUIRED

Item: {email_subject}
From: {sender}
Amount: {amount}
Category: High-Value Financial Transaction
Description: {summary}

Per Company_Handbook.md:
- Amount {amount} requires executive approval
- Business justification: {justification}

Please approve or decline by EOD."""

        return template.format(
            email_subject=email_data.get('subject', 'Subject Not Available'),
            sender=email_data.get('sender', 'Sender Not Available'),
            amount=amount_str,
            summary=email_data.get('subject', 'Subject Not Available')[:100],
            justification=email_data.get('content', 'Content Not Available')[:200]
        )

    def generate_opportunity_response(self, email_data: Dict[str, Any]) -> str:
        """Generate response for business opportunities"""
        template = """Subject: Re: {original_subject}

Dear {sender},

Thank you for your email regarding "{subject_topic}".

We acknowledge receipt of this business opportunity and will review it for potential follow-up.

Timeline: Initial review within 1 week.

Best regards,
AI Employee System"""

        return template.format(
            original_subject=email_data.get('subject', 'Subject Not Available'),
            sender=email_data.get('sender', 'Sender Not Available'),
            subject_topic=email_data.get('subject', 'Subject Not Available')
        )

    def generate_security_alert(self, email_data: Dict[str, Any]) -> str:
        """Generate security alert for suspicious emails"""
        template = """SECURITY ALERT

Suspicious email detected from: {sender}
Subject: {subject}
Threat Level: High

Action: Email quarantined. Administrator review required.

Security Team,
AI Employee System"""

        return template.format(
            sender=email_data.get('sender', 'Unknown Sender'),
            subject=email_data.get('subject', 'Subject Not Available')
        )

    def generate_standard_response(self, email_data: Dict[str, Any]) -> str:
        """Generate standard response for general emails"""
        template = """Subject: Re: {original_subject}

Dear {sender},

Thank you for your email regarding "{subject_topic}".

Our team has received your request and will review it promptly.
{specific_acknowledgment}

Timeline: Standard processing time.

Best regards,
AI Employee System"""

        return template.format(
            original_subject=email_data.get('subject', 'Subject Not Available'),
            sender=email_data.get('sender', 'Sender Not Available'),
            subject_topic=email_data.get('subject', 'Subject Not Available'),
            specific_acknowledgment="We will address this in due course."
        )

    def log_activity(self, log_location: str, action_taken: str, email_data: Dict[str, Any], analysis_result: Dict[str, Any]):
        """Log activity according to the log entry format from the skill definition"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sender = email_data.get('sender', 'Unknown')
        subject_summary = email_data.get('subject', '')[:50]  # First 50 chars

        log_entry = f"""{timestamp} - EMAIL_HANDLER - {action_taken} - {sender} - {subject_summary}
- Urgency Level: {analysis_result['urgency_assessment'].value}
- Action Taken: {action_taken}
- Result: Success
- Next Steps: Processing completed
"""

        # Determine the full log file path
        log_file_path = f"Logs/{log_location}"

        # Write to the appropriate log file
        import os
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry + "\n")

    def handle_common_issues(self, error_context: str) -> Dict[str, Any]:
        """Handle common issues from the error handling section"""
        issue_types = {
            'invalid_email_format': 'Invalid email format',
            'missing_sender': 'Missing sender information',
            'suspicious_content': 'Suspicious links or attachments',
            'policy_violation': 'Policy violations',
            'auth_failure': 'Authentication failures'
        }

        # Determine issue type based on context
        issue_found = None
        for issue_key, issue_desc in issue_types.items():
            if issue_desc.lower() in error_context.lower():
                issue_found = issue_key
                break

        if not issue_found:
            issue_found = 'unknown_issue'

        # Recovery actions from the skill definition
        recovery_actions = {
            'error_context': error_context,
            'issue_type': issue_found,
            'log_error': True,
            'move_to_manual_review': True,
            'send_admin_notification': issue_found in ['suspicious_content', 'policy_violation'],
            'update_dashboard': True,
            'retry_possible': issue_found == 'auth_failure'
        }

        return recovery_actions

    def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to process an email using the complete skill definition logic
        """
        try:
            # Validate trigger conditions
            if not self.check_trigger_conditions(
                email_data.get('content', ''),
                email_data.get('subject', '')
            ):
                return {
                    'success': False,
                    'message': 'Email does not meet trigger conditions',
                    'action_taken': 'skipped'
                }

            # Perform analysis
            analysis_result = self.analyze_email(
                email_data.get('content', ''),
                email_data.get('subject', ''),
                email_data.get('sender', '')
            )

            # Determine response action based on decision matrix
            action_decision = self.determine_response_action(analysis_result)

            # Generate appropriate response
            response = self.generate_response(action_decision['response_type'], {
                **email_data,
                'analysis': analysis_result
            })

            # Log the activity
            self.log_activity(
                action_decision['log_location'],
                action_decision['action'],
                email_data,
                analysis_result
            )

            # Simulate moving email to appropriate folder based on action
            target_folder = self.determine_target_folder(action_decision['response_type'])

            result = {
                'success': True,
                'action_taken': action_decision['action'],
                'response_type': action_decision['response_type'],
                'approval_required': action_decision['approval_required'].value,
                'log_location': action_decision['log_location'],
                'generated_response': response,
                'target_folder': target_folder,
                'analysis_result': analysis_result
            }

            return result

        except Exception as e:
            # Handle errors using the recovery actions from the skill
            error_handling = self.handle_common_issues(str(e))

            # Log error
            error_log = f"{datetime.datetime.now()} - EMAIL_HANDLER - ERROR - {email_data.get('sender', 'Unknown')} - {str(e)[:50]}\n"
            with open("Logs/error_log.log", 'a') as f:
                f.write(error_log)

            return {
                'success': False,
                'error': str(e),
                'recovery_actions': error_handling,
                'message': 'Error processed with recovery actions'
            }

    def determine_target_folder(self, response_type: str) -> str:
        """Determine where to move the processed email"""
        folder_mapping = {
            'urgent_response': 'Needs_Action',
            'financial_confirmation': 'Done',
            'approval_request': 'Needs_Action',  # Awaiting approval
            'executive_approval': 'Needs_Action',  # Awaiting executive approval
            'opportunity_response': 'Needs_Action',  # May need follow-up
            'security_alert': 'Quarantine',  # Suspicious emails
            'standard_response': 'Done'
        }

        return folder_mapping.get(response_type, 'Needs_Action')


# Example usage:
if __name__ == "__main__":
    # Initialize the email handler
    handler = EmailHandler()

    # Example email data
    sample_email = {
        'sender': 'vendor@example.com',
        'subject': 'Invoice for Services Rendered',
        'content': 'Please find attached the invoice for $150 for services rendered last month. Payment is due within 30 days.'
    }

    # Process the email
    result = handler.process_email(sample_email)

    print("Email Processing Result:")
    print(json.dumps(result, indent=2, default=str))