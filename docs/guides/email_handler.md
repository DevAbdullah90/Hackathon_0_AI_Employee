# Email Handler Skill

## Description
The Email Handler processes emails that have been moved to the Needs_Action folder, analyzes their content, and performs appropriate actions based on sender, subject, and urgency level.

## Trigger Conditions
- An email file appears in the Needs_Action folder
- The email contains monitored keywords ("urgent", "invoice", "payment", "opportunity", "hackathon")
- Email requires human review based on content analysis
- System detects a financial transaction or business opportunity

## Pre-requisites
- Email file exists in Needs_Action folder
- Company_Handbook.md is accessible for policy reference
- Logs folder is writable for activity logging

## Analysis Process

### 1. Sender Verification
- Check sender against known contacts list
- Verify domain authenticity
- Flag suspicious or unknown senders
- Cross-reference with trusted vendor list

### 2. Subject Analysis
- Extract key terms from subject line
- Identify urgency indicators
- Categorize email type (financial, operational, promotional, etc.)
- Check for phishing indicators

### 3. Content Examination
- Scan body for monetary amounts
- Identify action-required phrases
- Check for attachments and links
- Analyze tone and formality level

### 4. Urgency Assessment
- **Critical (Immediate)**: Words like "urgent", "ASAP", "immediate action required"
- **High (Within 24hrs)**: Payment deadlines, invoice due dates
- **Medium (Within 1 week)**: Opportunities, meeting requests
- **Low (Standard)**: Newsletters, routine updates

## Response Actions

### For Financial Transactions
- If amount < $50: Auto-process with confirmation
- If $50 ≤ amount ≤ $500: Prepare approval request
- If amount > $500: Escalate to executive approval
- Log transaction in financial tracking system

### For Business Opportunities
- Create calendar event if time-sensitive
- Draft initial response acknowledging receipt
- Schedule follow-up if needed
- Add to opportunity tracking list

### For Urgent Requests
- Flag for immediate attention
- Send notification to responsible party
- Prepare draft response if template exists
- Escalate if no response within timeframe

## Response Generation

### Draft Reply Structure
```
Subject: Re: [Original Subject]

Dear [Sender Name/Sender],

Thank you for your email regarding "[Subject Topic]".

Our team has received your request and will review it promptly.
[Specific acknowledgment based on content]

Timeline: [Expected response time based on urgency]

Best regards,
AI Employee System
```

### Approval Request Template
```
URGENT APPROVAL REQUIRED

Item: [Email Subject]
From: [Sender]
Amount: [If financial]
Category: [Type of request]
Description: [Brief summary]

Per Company_Handbook.md:
- Amount $X requires [manager/executive] approval
- Business justification: [Extracted from email]

Please approve or decline by [deadline].
```

## Logging Process

### Log Entry Format
```
TIMESTAMP - EMAIL_HANDLER - [ACTION_TYPE] - [SENDER] - [SUBJECT_SUMMARY]
- Urgency Level: [Critical/High/Medium/Low]
- Action Taken: [Processed/Drafted/Approved/Escalated]
- Result: [Success/Pending/Failure]
- Next Steps: [Follow-up required/Completed/Waiting Approval]
```

### Log File Locations
- Primary: `Logs/YYYY-MM-DD_email_handler.log`
- Financial: `Logs/financial_transactions.log`
- Urgent: `Logs/urgent_alerts.log`

## Decision Matrix

| Condition | Action | Approval Required | Log Location |
|-----------|--------|------------------|--------------|
| Urgent request | Flag + Draft response | No | urgent_alerts.log |
| Invoice <$50 | Process + Confirm | No | email_handler.log |
| Invoice $50-$500 | Draft approval req | Yes (Manager) | financial_transactions.log |
| Invoice >$500 | Escalate + Alert | Yes (Executive) | financial_transactions.log |
| Opportunity | Schedule + Draft response | No | email_handler.log |
| Suspicious | Quarantine + Alert | Yes (Admin) | security_alerts.log |

## Error Handling

### Common Issues
- Invalid email format
- Missing sender information
- Suspicious links or attachments
- Policy violations
- Authentication failures

### Recovery Actions
- Log error with full context
- Move to manual review queue
- Send admin notification
- Update dashboard with error count
- Retry mechanism for transient failures

## Integration Points
- Dashboard Updater: Update stats after processing
- Approval Checker: For financial transactions
- Plan Creator: For opportunity follow-ups
- Inbox Processor: For routing decisions

## Success Criteria
- Email processed within defined SLA
- Appropriate approval obtained when needed
- Proper logging maintained
- Dashboard updated with status
- Follow-up scheduled if required

## Configuration Variables
- MONITORED_KEYWORDS: List of keywords to watch
- FINANCIAL_THRESHOLDS: Approval limits ($50, $500)
- URGENT_INDICATORS: Words that trigger high priority
- TRUSTED_SENDERS: List of verified contacts
- LOG_RETENTION_DAYS: Days to retain logs

## Output Artifacts
- Processed email moved to Done folder
- Draft replies saved to Drafts folder
- Approval requests sent to managers
- Log entries in appropriate files
- Dashboard statistics updated
- Follow-up tasks created if needed