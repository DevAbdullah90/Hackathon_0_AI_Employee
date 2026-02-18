"""
Dynamic Approval Checker generated from approval_checker.md skill definition
"""
import os
import json
import datetime
import re
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

class ApprovalLevel(Enum):
    AUTO_APPROVE = "Auto-approve"
    MANAGER_APPROVAL = "Manager approval"
    EXECUTIVE_APPROVAL = "Executive approval"
    SPECIAL_APPROVAL = "Special approval"

class ApprovalStatus(Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ESCALATED = "Escalated"

@dataclass
class ApprovalResult:
    amount: float
    approval_level: ApprovalLevel
    requires_approval: bool
    approver: str
    status: ApprovalStatus
    reason: str
    notification_sent: bool

class ApprovalChecker:
    """
    The Approval Checker evaluates financial and business requests against company policy limits
    and determines if they require additional approval.
    """

    def __init__(self):
        # Configuration variables from skill definition
        self.AUTO_APPROVE_LIMIT = 50.0  # Under $50 - No approval needed
        self.MANAGER_APPROVE_LIMIT = 500.0  # $50 - $500 - Requires manager approval
        self.EXECUTIVE_APPROVE_LIMIT = float('inf')  # Over $500 - Requires executive approval
        self.SPECIAL_CATEGORIES = [
            'vendor payments', 'subscription renewals', 'equipment purchases',
            'service contracts', 'travel expenses', 'marketing expenditures'
        ]
        self.APPROVED_VENDORS_FILE = "approved_vendors.json"
        self.APPROVAL_LOGS_FILE = "Logs/approval_logs.log"

        # Ensure logs directory exists
        os.makedirs("Logs", exist_ok=True)

    def analyze_request_for_monetary_value(self, content: str) -> List[float]:
        """
        Extract monetary amounts from text
        """
        # Pattern to match currency amounts like $100, $1,000.50, €50, etc.
        currency_pattern = r'(?:[$€£¥]\s*)?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*[a-zA-Z]{0,3})?|(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:[$€£¥])'
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

    def identify_request_category(self, content: str) -> str:
        """
        Identify request type and category
        """
        content_lower = content.lower()

        # Check for special categories
        for category in self.SPECIAL_CATEGORIES:
            if category.lower() in content_lower:
                return category.title()

        # Default categories
        if any(word in content_lower for word in ['invoice', 'payment', 'bill']):
            return 'Financial Transaction'
        elif any(word in content_lower for word in ['purchase', 'buy', 'acquire', 'equipment']):
            return 'Purchase Request'
        elif any(word in content_lower for word in ['travel', 'trip', 'flight', 'hotel', 'expense']):
            return 'Travel Expense'
        elif any(word in content_lower for word in ['subscription', 'renewal', 'membership']):
            return 'Subscription'
        elif any(word in content_lower for word in ['marketing', 'advertising', 'promotion']):
            return 'Marketing Expenditure'
        elif any(word in content_lower for word in ['service', 'contract', 'consultant']):
            return 'Service Contract'
        else:
            return 'General Request'

    def cross_reference_with_vendor(self, content: str) -> Dict[str, Any]:
        """
        Cross-reference with vendor/recipient
        """
        # Extract potential vendor names
        vendor_patterns = [
            r'from\s+([A-Z][a-zA-Z\s]+)',  # "from Company Name"
            r'to\s+([A-Z][a-zA-Z\s]+)',    # "to Company Name"
            r'payment\s+to\s+([A-Z][a-zA-Z\s]+)',  # "payment to Company Name"
        ]

        vendors = []
        for pattern in vendor_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            vendors.extend(matches)

        vendors = list(set(vendors))  # Remove duplicates

        # Check if vendors are approved
        approved_vendors = self.get_approved_vendors()
        result = {
            'mentioned_vendors': vendors,
            'all_approved': all(vendor in approved_vendors for vendor in vendors) if vendors else True,
            'unapproved_vendors': [v for v in vendors if v not in approved_vendors] if vendors else []
        }

        return result

    def check_against_budget_allocations(self, content: str) -> Dict[str, Any]:
        """
        Check against budget allocations
        """
        # For this implementation, we'll return a placeholder
        # In a real system, this would connect to budget tracking systems
        return {
            'budget_check_performed': False,
            'sufficient_funds': True,
            'budget_category': 'General',
            'remaining_allocation': 10000.0  # Placeholder
        }

    def verify_business_justification(self, content: str) -> Dict[str, Any]:
        """
        Verify business justification
        """
        justification_indicators = [
            'business need', 'justification', 'reason for', 'purpose of',
            'required for', 'needed for', 'benefit of', 'ROI', 'return on investment'
        ]

        content_lower = content.lower()
        has_justification = any(indicator in content_lower for indicator in justification_indicators)

        # Extract potential justification text
        justification_text = ""
        sentences = content.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in justification_indicators):
                justification_text = sentence.strip()
                break

        return {
            'has_justification': has_justification,
            'justification_text': justification_text,
            'justification_score': 0.8 if has_justification else 0.3  # Placeholder scoring
        }

    def apply_approval_rules(self, amounts: List[float], category: str, vendor_info: Dict[str, Any]) -> ApprovalResult:
        """
        Apply appropriate approval rules based on amount, category, and vendor
        """
        if not amounts:
            # No monetary amount found, default to auto-approve for non-financial requests
            return ApprovalResult(
                amount=0.0,
                approval_level=ApprovalLevel.AUTO_APPROVE,
                requires_approval=False,
                approver="System",
                status=ApprovalStatus.APPROVED,
                reason="No monetary amount detected",
                notification_sent=False
            )

        max_amount = max(amounts)

        # Check if category requires special approval regardless of amount
        if any(cat.lower() in category.lower() for cat in self.SPECIAL_CATEGORIES):
            return ApprovalResult(
                amount=max_amount,
                approval_level=ApprovalLevel.SPECIAL_APPROVAL,
                requires_approval=True,
                approver="Appropriate Authority",
                status=ApprovalStatus.PENDING,
                reason=f"Category '{category}' requires special approval",
                notification_sent=False
            )

        # Check if vendor is unapproved (requires higher approval)
        if vendor_info['unapproved_vendors']:
            return ApprovalResult(
                amount=max_amount,
                approval_level=ApprovalLevel.MANAGER_APPROVAL,
                requires_approval=True,
                approver="Manager",
                status=ApprovalStatus.PENDING,
                reason=f"Vendor not in approved list: {', '.join(vendor_info['unapproved_vendors'])}",
                notification_sent=False
            )

        # Apply standard financial limits
        if max_amount < self.AUTO_APPROVE_LIMIT:
            return ApprovalResult(
                amount=max_amount,
                approval_level=ApprovalLevel.AUTO_APPROVE,
                requires_approval=False,
                approver="System",
                status=ApprovalStatus.APPROVED,
                reason=f"Amount ${max_amount} below auto-approve threshold of ${self.AUTO_APPROVE_LIMIT}",
                notification_sent=False
            )
        elif self.AUTO_APPROVE_LIMIT <= max_amount < self.MANAGER_APPROVE_LIMIT:
            return ApprovalResult(
                amount=max_amount,
                approval_level=ApprovalLevel.MANAGER_APPROVAL,
                requires_approval=True,
                approver="Manager",
                status=ApprovalStatus.PENDING,
                reason=f"Amount ${max_amount} requires manager approval (between ${self.AUTO_APPROVE_LIMIT} and ${self.MANAGER_APPROVE_LIMIT})",
                notification_sent=False
            )
        else:  # max_amount >= MANAGER_APPROVE_LIMIT
            return ApprovalResult(
                amount=max_amount,
                approval_level=ApprovalLevel.EXECUTIVE_APPROVAL,
                requires_approval=True,
                approver="Executive",
                status=ApprovalStatus.PENDING,
                reason=f"Amount ${max_amount} requires executive approval (exceeds ${self.MANAGER_APPROVE_LIMIT})",
                notification_sent=False
            )

    def verify_request_authenticity(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Verify request authenticity
        """
        # Check for common phishing/fraud indicators
        fraud_indicators = [
            'urgent action required', 'verify account', 'suspicious activity',
            'click here', 'act now', 'limited time', 'wire transfer immediately'
        ]

        content_lower = content.lower()
        has_fraud_indicators = any(indicator in content_lower for indicator in fraud_indicators)

        if has_fraud_indicators:
            return False

        # In a real system, we'd also check:
        # - Sender verification against known contacts
        # - Digital signatures
        # - Communication channel authenticity

        return True

    def validate_expense_codes(self, content: str) -> List[str]:
        """
        Validate expense codes
        """
        # Look for expense codes in the format EC-XXXX or EXP-XXXX
        expense_code_pattern = r'(EC-\w+|EXP-\w+|EXPENSE-\w+)'
        expense_codes = re.findall(expense_code_pattern, content, re.IGNORECASE)

        # In a real system, validate against known expense codes
        return expense_codes

    def maintain_approval_logs(self, request_id: str, approval_result: ApprovalResult, content: str):
        """
        Maintain approval logs
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"""{timestamp} - APPROVAL_CHECKER - {approval_result.approval_level.value} - Request: {request_id[:20]}... - Amount: ${approval_result.amount} - Status: {approval_result.status.value} - Reason: {approval_result.reason}
"""

        with open(self.APPROVAL_LOGS_FILE, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

    def ensure_segregation_of_duties(self, approval_result: ApprovalResult) -> bool:
        """
        Ensure segregation of duties (for this demo, return True)
        """
        # In a real system, this would check that the requester is not the approver
        return True

    def verify_against_company_policies(self, content: str) -> List[str]:
        """
        Verify against company policies
        """
        # Check against common policy violations
        policy_violations = []

        content_lower = content.lower()
        if 'cash advance' in content_lower and 'large amount' in content_lower:
            policy_violations.append('Large cash advance request - violates policy')

        # Add more policy checks as needed

        return policy_violations

    def check_regulatory_requirements(self, content: str) -> List[str]:
        """
        Check regulatory requirements
        """
        # Check for regulatory compliance issues
        regulatory_issues = []

        content_lower = content.lower()
        if any(word in content_lower for word in ['international', 'foreign', 'overseas']):
            regulatory_issues.append('International transaction - may require additional compliance')

        return regulatory_issues

    def validate_approval_hierarchy(self, approval_result: ApprovalResult) -> bool:
        """
        Validate approval hierarchy
        """
        # In a real system, this would check if the designated approver has proper authority
        return True

    def maintain_audit_trail(self, request_id: str, approval_result: ApprovalResult, content: str):
        """
        Maintain audit trail
        """
        # This would maintain a detailed audit trail in a real system
        # For this demo, we'll just log to the same file
        self.maintain_approval_logs(request_id, approval_result, content)

    def send_approval_notification(self, approval_result: ApprovalResult, content: str, request_id: str) -> bool:
        """
        Send approval requests to appropriate authority
        """
        try:
            # Create approval request notification
            notification_content = f"""
APPROVAL REQUEST

Request ID: {request_id}
Amount: ${approval_result.amount}
Category: {self.identify_request_category(content)}
Requested by: System
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Reason: {approval_result.reason}

Please review and approve or reject this request.
"""

            # In a real system, this would send an email or notification to the appropriate approver
            # For this demo, we'll just write to a file
            notification_file = f"Notifications/approval_request_{request_id}.txt"
            os.makedirs("Notifications", exist_ok=True)

            with open(notification_file, 'w', encoding='utf-8') as f:
                f.write(notification_content)

            return True
        except Exception:
            return False

    def update_dashboard_with_status(self, request_id: str, approval_result: ApprovalResult):
        """
        Update dashboard with approval status
        """
        # Read current dashboard
        dashboard_path = "Dashboard.md"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()

            # Update the appropriate section
            # For this demo, we'll just append to the recent activity log
            import re
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            activity_entry = f"- {timestamp}: Approval request for ${approval_result.amount} ({approval_result.approval_level.value})\n"

            # Find and update the recent activity section
            pattern = r'(## 📅 Recent Activity Log\n)(.*?)(\n\n|$)'
            updated_content = re.sub(
                pattern,
                rf'\g<1>{activity_entry}\g<2>\g<3>',
                dashboard_content,
                flags=re.DOTALL
            )

            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

    def escalate_overdue_approvals(self, request_id: str) -> bool:
        """
        Escalate overdue approvals
        """
        # In a real system, this would check for overdue approvals and escalate
        # For this demo, return False (no escalation needed)
        return False

    def get_approved_vendors(self) -> List[str]:
        """
        Get list of approved vendors
        """
        if os.path.exists(self.APPROVED_VENDORS_FILE):
            with open(self.APPROVED_VENDORS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return a default list of approved vendors
            return [
                "Microsoft", "Google", "Amazon", "Adobe", "Salesforce",
                "PayPal", "Stripe", "Bank of America", "Chase", "Wells Fargo"
            ]

    def check_compliance(self, content: str) -> Dict[str, Any]:
        """
        Perform comprehensive compliance check
        """
        policy_violations = self.verify_against_company_policies(content)
        regulatory_issues = self.check_regulatory_requirements(content)
        valid_hierarchy = self.validate_approval_hierarchy(ApprovalResult(
            amount=0, approval_level=ApprovalLevel.AUTO_APPROVE,
            requires_approval=False, approver="", status=ApprovalStatus.APPROVED,
            reason="", notification_sent=False
        ))

        return {
            'policy_violations': policy_violations,
            'regulatory_issues': regulatory_issues,
            'hierarchy_valid': valid_hierarchy,
            'overall_compliance': len(policy_violations) == 0 and len(regulatory_issues) == 0 and valid_hierarchy
        }

    def process_approval_request(self, content: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method to process an approval request following the approval process
        """
        if request_id is None:
            request_id = f"REQ_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Step 1: Analyze request for monetary value
            amounts = self.analyze_request_for_monetary_value(content)

            # Step 2: Identify request category and type
            category = self.identify_request_category(content)

            # Step 3: Cross-reference with vendor/recipient
            vendor_info = self.cross_reference_with_vendor(content)

            # Step 4: Check against budget allocations
            budget_info = self.check_against_budget_allocations(content)

            # Step 5: Verify business justification
            justification_info = self.verify_business_justification(content)

            # Step 6: Verify request authenticity
            is_authentic = self.verify_request_authenticity(content)

            if not is_authentic:
                return {
                    'success': False,
                    'request_id': request_id,
                    'reason': 'Request failed authenticity verification',
                    'amounts_found': amounts,
                    'category': category,
                    'status': 'Blocked - Authentication Failed'
                }

            # Apply approval rules
            approval_result = self.apply_approval_rules(amounts, category, vendor_info)

            # Perform compliance check
            compliance_result = self.check_compliance(content)

            # Update approval result if compliance issues found
            if not compliance_result['overall_compliance']:
                approval_result.requires_approval = True
                approval_result.approval_level = ApprovalLevel.SPECIAL_APPROVAL
                approval_result.reason += " (Compliance issues detected)"

            # Step 4: Generate approval notification if needed (from approval workflow)
            notification_sent = False
            if approval_result.requires_approval:
                notification_sent = self.send_approval_notification(approval_result, content, request_id)
                approval_result.notification_sent = notification_sent

            # Step 5: Update dashboard with approval status
            self.update_dashboard_with_status(request_id, approval_result)

            # Step 6: Log approval requirement in system
            self.maintain_approval_logs(request_id, approval_result, content)
            self.maintain_audit_trail(request_id, approval_result, content)

            result = {
                'success': True,
                'request_id': request_id,
                'amounts_found': amounts,
                'max_amount': max(amounts) if amounts else 0,
                'category': category,
                'approval_result': {
                    'amount': approval_result.amount,
                    'approval_level': approval_result.approval_level.value,
                    'requires_approval': approval_result.requires_approval,
                    'approver': approval_result.approver,
                    'status': approval_result.status.value,
                    'reason': approval_result.reason,
                    'notification_sent': notification_sent
                },
                'vendor_info': vendor_info,
                'budget_info': budget_info,
                'justification_info': justification_info,
                'compliance_check': compliance_result,
                'message': f"Approval check completed. Level: {approval_result.approval_level.value}"
            }

            return result

        except Exception as e:
            return {
                'success': False,
                'request_id': request_id,
                'error': str(e),
                'message': 'Approval check failed due to error'
            }

    def batch_process_requests(self, requests: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process multiple requests in batch
        """
        results = []
        for request in requests:
            content = request.get('content', '')
            req_id = request.get('id', None)
            result = self.process_approval_request(content, req_id)
            results.append(result)

        return results

    def get_approval_statistics(self) -> Dict[str, Any]:
        """
        Get approval statistics for reporting
        """
        if not os.path.exists(self.APPROVAL_LOGS_FILE):
            return {
                'total_requests': 0,
                'auto_approved': 0,
                'manager_approved': 0,
                'executive_approved': 0,
                'rejected': 0
            }

        with open(self.APPROVAL_LOGS_FILE, 'r', encoding='utf-8') as f:
            logs = f.read()

        total_requests = logs.count('APPROVAL_CHECKER')
        auto_approved = logs.count('Auto-approve')
        manager_approved = logs.count('Manager approval')
        executive_approved = logs.count('Executive approval')
        rejected = logs.count('Rejected')

        return {
            'total_requests': total_requests,
            'auto_approved': auto_approved,
            'manager_approved': manager_approved,
            'executive_approved': executive_approved,
            'rejected': rejected,
            'last_updated': datetime.datetime.now().isoformat()
        }


# Example usage:
if __name__ == "__main__":
    # Initialize the approval checker
    checker = ApprovalChecker()

    # Example request content
    sample_request = """
    Invoice for office supplies from Amazon. Total amount: $250.00.
    Business justification: Needed for quarterly office refresh.
    Please process payment to vendor.
    """

    # Process the approval request
    result = checker.process_approval_request(sample_request)

    print("Approval Check Result:")
    print(json.dumps(result, indent=2, default=str))

    # Get approval statistics
    stats = checker.get_approval_statistics()
    print("\nApproval Statistics:")
    print(json.dumps(stats, indent=2, default=str))