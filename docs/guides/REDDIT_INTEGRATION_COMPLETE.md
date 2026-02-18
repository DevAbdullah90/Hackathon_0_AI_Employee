# REDDIT INTEGRATION - EXTENDED GOLD TIER

## 🚀 EXPANDED GOLD TIER WITH REDDIT SUPPORT

**Status**: ✅ REDDIT INTEGRATION COMPLETE
**Date**: January 16, 2026
**Module**: `reddit/watcher.py` | `reddit_content_generator.py`

This document describes the additional Reddit integration that extends your Gold Tier AI Employee to monitor and engage with the Reddit platform.

---

## 📱 REDDIT INTEGRATION COMPONENTS

### 1. REDDIT WATCHER
**File**: `reddit/watcher.py` (450+ lines)
**Status**: ✅ Fully Implemented

**Capabilities**:
- ✅ Monitors Reddit mentions of your username
- ✅ Tracks private messages and DMs
- ✅ Finds business opportunities in target subreddits
- ✅ Monitors replies to your posts
- ✅ Keyword-based lead detection
- ✅ Creates action items in /Needs_Action

**Subreddits Monitored**:
- r/smallbusiness
- r/Entrepreneur
- r/business
- r/Productivity
- r/automation
- r/SideProject
- r/startup
- r/consulting
- r/freelance
- r/EntrepreneurRideAlong
- r/saas
- r/indiebiz

**Business Keywords Detected**:
- 'looking for', 'need help', 'recommend'
- 'suggestions', 'problem with', 'hiring'
- 'job opening', 'consultant', 'expert'
- 'advice needed', 'question about'
- 'best tool for', 'solution for', 'struggling with'

**Tracked Activity Types**:
1. **Mentions** - When your username is mentioned
2. **Direct Messages** - Private messages to your account
3. **Post Replies** - Comments on your posts
4. **Opportunities** - Posts/comments seeking help in target subreddits

**Usage**:
```bash
# Run once to check for activity
python reddit/watcher.py --once

# Run continuously (checks every 10 minutes)
python reddit/watcher.py

# With custom vault path
python reddit/watcher.py --vault /path/to/vault
```

### 2. REDDIT CONTENT GENERATOR
**File**: `reddit_content_generator.py` (20KB+)
**Status**: ✅ Fully Implemented

**Capabilities**:
- ✅ Generates 4 types of Reddit posts:
  - Case studies
  - Tips/advice posts
  - Questions for engagement
  - Discussion starters
- ✅ Generates 4 types of comments:
  - Helpful responses
  - Follow-up questions
  - Appreciation comments
  - Collaborative responses
- ✅ Templates personalized with business context
- ✅ Weekly post batch generation
- ✅ Saves to organized directories

**Post Types**:

1. **Case Study Posts**
   ```
   [Case Study] How we helped [client] increase [metric] by [%]
   ```
   - Share success stories
   - Provide social proof
   - Generate leads

2. **Tips & Advice Posts**
   ```
   5 tips for [audience] that [desire]
   ```
   - Position as expert
   - Provide value
   - Build authority

3. **Question Posts**
   ```
   How do you handle [challenge] in [context]?
   ```
   - Drive engagement
   - Research audience
   - Build community

4. **Discussion Posts**
   ```
   Unpopular opinion: [opinion]
   ```
   - Generate conversation
   - Stand out in feed
   - Build brand personality

**Comment Templates**:
- Helpful/Informative
- Question/Follow-up
- Appreciation/Validation
- Collaborative/Resource-sharing

**Usage**:
```bash
# Generate a single post
python reddit_content_generator.py --type post --post-type tips

# Generate a specific type of post
python reddit_content_generator.py --type post --post-type case_study --subreddit Entrepreneur

# Generate a comment
python reddit_content_generator.py --type comment --comment-type helpful

# Generate batch of posts
python reddit_content_generator.py --type batch --count 5
```

---

## 🔗 INTEGRATION WITH GOOGLE TIER SYSTEM

### CEO Briefing Integration
The CEO Briefing Generator (`ceo_briefing_generator.py`) now includes Reddit metrics:

```python
# Reddit activity tracked in weekly CEO briefings:
- reddit_posts (posts created)
- reddit_mentions (username mentions)
- reddit_opportunities (leads generated)
```

### Workflow Orchestrator Integration
The Reddit watcher integrates seamlessly with the existing workflow:

```
Reddit Watcher → Needs_Action → Claude Code → Plans → Approval → Actions → Logs
                     ↓
              Reddit_Data/Activity Logs → CEO Briefing
```

### Audit Logging
All Reddit activities are logged through the AuditLogger:

```python
from audit_logger import AuditLogger

logger = AuditLogger()
logger.log_action("reddit_opportunity_found", "AI_Employee", details)
```

### Directory Structure
```
AI_Employee_Vault/
├── Reddit_Data/           # Activity logs
├── Reddit_Posts/          # Generated posts
├── Reddit_Comments/       # Generated comments
├── Needs_Action/          # Action items (Reddit_* files)
└── Done/                  # Processed Reddit items
```

---

## 📊 BUSINESS VALUE

### Lead Generation
- Monitors 12+ business subreddits
- Detects 13+ business intent keywords
- Creates action items for every opportunity
- Tracks engagement quality

### Brand Building
- Automated content generation
- Consistent posting schedule
- Positioning as industry expert
- Community engagement

### Time Savings
- 24/7 monitoring of Reddit
- Automated response suggestions
- Batch content generation
- One-click action items

### Intelligence
- Weekly Reddit metrics in CEO briefing
- Trend analysis of opportunities
- Engagement tracking
- Subreddit performance comparison

---

## 🔐 REQUIRED CREDENTIALS

Create a `.env` file in your project root:

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=AI Employee Bot v1.0
REDDIT_USERNAME=your_username_here
REDDIT_PASSWORD=your_password_here
```

**How to get credentials:**

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" (for personal use)
4. Name: "AI Employee Bot"
5. Description: "Automated monitoring and engagement"
6. About URL: Your website or blank
7. Redirect URI: http://localhost:8080
8. Click "Create App"
9. Copy Client ID and Client Secret

**Important Notes**:
- Use a dedicated account (not your main personal one)
- Follow Reddit's API terms of service
- Don't spam - focus on providing value
- Respect subreddit rules
- Maintain human-like engagement patterns

---

## 📈 EXAMPLE WORKFLOWS

### Workflow 1: Opportunity Detection → Response

1. **Detection**
   ```
   Reddit watcher finds: "Looking for automation help in r/smallbusiness"
   ```

2. **Action Created**
   ```
   File: Needs_Action/REDDIT_20260116_opportunity.md
   ```

3. **AI Employee Processes**
   - Reads business context
   - Generates helpful response
   - Creates follow-up plan
   - Requests approval if needed

4. **Approval**
   ```
   Human reviews response
   Moves to /Approved folder
   ```

5. **Posting**
   - MCP server posts response
   - Activity logged
   - Follow-up scheduled

### Workflow 2: Weekly Content Creation

1. **Generation**
   ```bash
   python reddit_content_generator.py --type batch --count 5
   ```

2. **Review**
   - Posts saved to Reddit_Posts/
   - Human reviews for quality
   - Schedule approval

3. **Posting**
   - Approved posts moved to queue
   - Scheduler posts at optimal times
   - Engagement tracked

4. **Reporting**
   - Weekly CEO briefing includes:
     * Posts made
     * Engagement received
     * Opportunities generated
     * ROI analysis

---

## 🎯 REDDIT BEST PRACTICES

### DO:
✅ Provide genuine value before promoting
✅ Engage authentically in discussions
✅ Follow each subreddit's rules
✅ Respond to comments on your posts
✅ Use Reddit's native formatting
✅ Cite sources and provide proof
✅ Be transparent about your affiliation

### DON'T:
❌ Don't spam or overpost
❌ Don't be overly promotional
❌ Don't argue with negative comments
❌ Don't use clickbait titles
❌ Don't ignore community feedback
❌ Don't use multiple accounts to promote
❌ Don't post the same content everywhere

---

## 📊 METRICS TO TRACK

**In CEO Weekly Briefing**:

- Reddit Posts Created
- Mentions Received
- Opportunities Generated
- Engagement Rate
- Subreddit Performance
- Traffic Generated
- Leads Converted

**Activity Logs Stored In**:
- `Reddit_Data/activity_YYYYMMDD_HHMMSS.json`

---

## 🔧 TECHNICAL REQUIREMENTS

**Dependencies**:
```bash
pip install praw  # Python Reddit API Wrapper
```

**API Rate Limits**:
- 60 requests/minute (authenticated)
- 600 requests/10 minutes (OAuth)
- Our watcher respects these limits with:
  - 10-minute check intervals (mentions/DMs/posts)
  - Hourly opportunity searches
  - Proper error handling

**File Encoding**:
- UTF-8 for all Reddit content
- Backslash escape for Windows paths
- JSON with proper serialization

---

## ✅ EXTENDED GOLD TIER REQUIREMENTS

### Original Requirements (from haka.md, Gold Tier):
✅ Full cross-domain integration
✅ Xero accounting system
✅ Multiple MCP servers
✅ Weekly business audit
✅ Error recovery & degradation
✅ Comprehensive audit logging

### **NEW** Extended Requirements (with Reddit):
✅ **Reddit monitoring** - 12+ subreddits
✅ **Opportunity detection** - keyword-based
✅ **Content generation** - 4 post types
✅ **Engagement tracking** - mentions & responses
✅ **CEO briefing integration** - Reddit metrics
✅ **Audit logging** - All Reddit activities

---

## 🚀 GETTING STARTED

### Step 1: Get Reddit API Credentials
Follow the credential setup section above.

### Step 2: Configure Environment
```bash
# Create .env file
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=AI Employee Bot v1.0
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

### Step 3: Test Reddit Watcher
```bash
python reddit/watcher.py --once
```

### Step 4: Generate Content
```bash
python reddit_content_generator.py --type batch --count 3
```

### Step 5: Review CEO Briefing
```bash
python ceo_briefing_generator.py generate_and_save
# Check Reports/CEO_Briefing_*.md for Reddit metrics
```

### Step 6: Deploy
Add to scheduler.py or workflow_orchestrator.py for automated monitoring.

---

## 📚 USEFUL SUBREDDITS FOR BUSINESS

**Lead Generation**:
- r/smallbusiness
- r/Entrepreneur
- r/freelance
- r/consulting

**Industry Specific**:
- r/saas
- r/indiebiz
- r/startups
- r/Productivity

**Learning & Sharing**:
- r/business
- r/automation
- r/SideProject
- r/EntrepreneurRideAlong

---

## 🎉 SUMMARY

You now have **complete Reddit integration** for your AI Employee Gold Tier:

- ✅ Watcher monitoring 12+ subreddits
- ✅ Lead/opportunity detection
- ✅ Content generation (posts & comments)
- ✅ CEO briefing integration
- ✅ Audit logging
- ✅ Human-in-the-loop workflow

**This makes your AI Employee even more powerful** with one of the largest business-focused communities on the internet!

---

**Next**: Consider adding other platforms like Discord communities, Slack channels, or industry-specific forums for even more reach!
