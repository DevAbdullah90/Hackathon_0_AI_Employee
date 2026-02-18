# AI Employee Automation Guide

## Overview

This system automates posting to **WhatsApp**, **LinkedIn**, **Twitter**, and **Email** with human approval workflow.

## Quick Start

### 1. Install Dependencies
```bash
pip install watchdog pyyaml python-dotenv tweepy playwright
playwright install chromium
```

### 2. Configure Credentials
Edit `.env` file with your credentials:

```env
# Twitter (already configured)
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret

# Email (add App Password for Gmail)
EMAIL_USERNAME=your@gmail.com
EMAIL_PASSWORD=your_app_password

# LinkedIn/WhatsApp (login once to save session)
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your_password
```

### 3. Start the System
Double-click `start_automation.bat` or run:
```bash
python auto_processor.py
python draft_generator.py  # In another terminal
```

## Workflow

```
Email/WhatsApp arrives
        ↓
[Needs_Action/] folder
        ↓
Draft Generator creates reply
        ↓
[Pending_Approval/] folder
        ↓
Human reviews & approves
        ↓
Move to [Approved/] folder
        ↓
Auto Processor posts/sends
        ↓
[Done/] folder (success) or [Failed/] (error)
```

## File Formats

### LinkedIn Post
```markdown
---
type: linkedin_post
status: pending_approval
---

# LinkedIn Post

## Post Content

Your post content here...
```

### Twitter Post
```markdown
---
type: twitter_post
status: pending_approval
---

# Twitter Post

## Tweet

Your tweet (max 280 chars)...
```

### WhatsApp Message
```markdown
---
type: whatsapp
phone: +1234567890
to: Contact Name
---

# WhatsApp Message

## Message

Your message here...
```

### Email
```markdown
---
type: email
to: recipient@email.com
subject: Email Subject
---

# Email

## Email Body

Your email content...
```

## Platform Setup

### Twitter/X
1. Create app at developer.twitter.com
2. Get API keys and tokens
3. Add to `.env` file
4. Test: `python mcp/twitter-mcp/twitter_mcp.py user_info`

### LinkedIn
1. First run will open browser
2. Login to LinkedIn manually
3. Session cookies are saved automatically
4. Test: `python linkedin_poster.py profile`

### WhatsApp
1. First run opens WhatsApp Web
2. Scan QR code with your phone
3. Session is saved for future use
4. Test: `python mcp/whatsapp-mcp/whatsapp_mcp.py get_unread`

### Email (Gmail)
1. Enable 2-Step Verification in Google Account
2. Generate App Password: Security → App Passwords
3. Add to `.env`: `EMAIL_PASSWORD=your_app_password`
4. Test: `python mcp/email-mcp/email_mcp.py get_unread`

## Testing

Run all tests:
```bash
python test_automation.py
```

Test individual platforms:
```bash
# Twitter
python mcp/twitter-mcp/twitter_mcp.py post_tweet --text "Test tweet"

# LinkedIn
python linkedin_poster.py post --content "Test post"

# WhatsApp
python mcp/whatsapp-mcp/whatsapp_mcp.py send_message --phone "+1234567890" --message "Test"

# Email
python mcp/email-mcp/email_mcp.py send --to "test@email.com" --subject "Test" --body "Test email"
```

## Folder Structure

```
AI_Employee_vault/
├── Approved/           # Human-approved files (auto-posted)
├── Pending_Approval/   # AI-generated drafts for review
│   ├── Emails/
│   ├── WhatsApp/
│   ├── LinkedIn/
│   └── Twitter/
├── Needs_Action/       # Incoming items requiring response
├── Done/               # Successfully processed
├── Failed/             # Failed to process
├── Logs/               # System logs
├── Skills/             # AI skill definitions
└── mcp/                # Platform integrations
    ├── email-mcp/
    ├── twitter-mcp/
    └── whatsapp-mcp/
```

## Skills

The AI uses skill files to generate appropriate content:

- `Skills/email_drafter_skill.md` - Email reply templates
- `Skills/whatsapp_reply_skill.md` - WhatsApp reply templates
- `Skills/linkedin_post_skill.md` - LinkedIn post templates
- `Skills/twitter_tweet_skill.md` - Tweet templates

## Troubleshooting

### Twitter: "Authentication failed"
- Verify API keys in `.env`
- Ensure app has "Read and Write" permissions
- Regenerate tokens if needed

### Email: "Authentication failed"
- Use App Password, not regular password
- Enable 2-Step Verification first
- Check EMAIL_SMTP_SERVER is correct

### WhatsApp: "Not logged in"
- Delete `whatsapp_session/` folder
- Run again and scan QR code
- Keep phone connected to internet

### LinkedIn: "Not logged in"
- Delete `linkedin_session/` folder
- Delete `linkedin_cookies.json`
- Run login: `python linkedin_poster.py login`

## Security Notes

1. Never commit `.env` to version control
2. Use App Passwords instead of real passwords
3. Review all drafts before approving
4. Monitor logs for unusual activity
5. Keep session folders secure

## Support

- Check `Logs/` folder for error details
- Run `python test_automation.py` to diagnose issues
- Each platform MCP has `--help` for usage info
