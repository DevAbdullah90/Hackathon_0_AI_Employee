# AI Employee - Quick Start Guide

## ✅ SYSTEM COMPLETE

Your AI Employee Gold Tier automation system is **100% complete** and ready to run!

## 📦 COMPONENTS CREATED

### 1. Auto Processor (`auto_processor.py`)
- Monitors `Approved/` folder 24/7
- Processes .md files automatically
- Creates logs, moves files to `Done/`, updates Dashboard.md
- Handles existing files on startup

### 2. Smart Scheduler (`smart_scheduler.py`)
- Every hour: Check Needs_Action and create plans
- Every 2 hours: Check Reddit for opportunities
- Every 3 hours: Check Twitter for mentions/DMs
- Every 6 hours: Check LinkedIn for opportunities
- Daily 9 AM: Generate content
- Weekly Sunday 10 PM: Generate CEO report

### 3. Workflow Orchestrator (`workflow_orchestrator.py`)
- Master coordinator running all components
- Manages threads for parallel processing
- Health checks and status reporting
- Graceful shutdown handling

### 4. Start Scripts
- `start_ai_employee.bat` - Windows
- `start_ai_employee.sh` - Linux/Mac

## 🚀 HOW TO START (CHOOSE ONE)

### Option 1: Quick Start (Windows)
```bash
double-click start_ai_employee.bat
```

### Option 2: Command Line
```bash
cd "C:\Users\LENOVO X1 YOGA\Desktop\hakathone zero\AI_Employee_Vault"
python workflow_orchestrator.py
```

### Option 3: Start Components Individually
```bash
# Terminal 1 - Auto Processor
python auto_processor.py

# Terminal 2 - Smart Scheduler
python smart_scheduler.py

# Terminal 3 - Workflow Orchestrator
python workflow_orchestrator.py
```

## 📋 COMPLETE WORKFLOW

```
1. Opportunities Detected
   └─> Reddit/Twitter/LinkedIn Watcher creates files in Pending_Approval/

2. Human Review (Optional)
   └─> Review files in Pending_Approval/
   └─> Move approved files to Approved/

3. Auto Processing
   └─> Auto Processor detects files in Approved/
   └─> Processes them automatically
   └─> Moves to Done/
   └─> Updates Dashboard.md
   └─> Creates logs in Logs/

4. Scheduled Tasks
   └─> Smart Scheduler runs periodic checks
   └─> Generates content, briefings, reports
   └─> Everything logged automatically
```

## 📁 FOLDER STRUCTURE

```
AI_Employee_Vault/
├── Approved/          # Files auto-processed from here
├── Pending_Approval/  # Human reviews here (if needed)
├── Done/             # Processed files moved here
├── Needs_Action/     # Tasks created by watchers
├── Logs/             # All logs (JSONL format)
├── Plans/            # AI-generated action plans
├── Reddit_Data/      # Reddit activity logs
├── Reddit_Posts/     # Generated Reddit content
├── LinkedIn_Posts/   # Generated LinkedIn content
├── Reports/          # CEO briefings & reports
└── Dashboard.md      # Real-time system dashboard
```

## 🔐 CREDENTIALS NEEDED

### Reddit API (do this first!)
1. Go to: https://www.reddit.com/prefs/apps
2. Create App → Choose "script"
3. Copy credentials to `.env`:
   ```
   REDDIT_CLIENT_ID=your_id
   REDDIT_CLIENT_SECRET=your_secret
   REDDIT_USER_AGENT=AI Employee Bot v1.0
   REDDIT_USERNAME=your_username
   REDDIT_PASSWORD=your_password
   ```

### Twitter API
1. Go to: https://developer.twitter.com/
2. Get API v2 credentials
3. Add to `.env`:
   ```
   TWITTER_API_KEY=your_key
   TWITTER_API_SECRET=your_secret
   TWITTER_ACCESS_TOKEN=your_token
   TWITTER_ACCESS_TOKEN_SECRET=your_secret
   ```

## 📊 MONITORING

### Check Logs
```bash
# Real-time log monitoring
tail -f Logs/orchestrator.log

# Today's processed files
cat Logs/auto_processor.log

# Scheduler activities
cat Logs/scheduler.log
```

### Check Dashboard
```bash
# View live dashboard
cat Dashboard.md
```

### System Status
```bash
python workflow_orchestrator.py
# Shows ASCII banner and live component status
```

## 🎯 WORKFLOW EXAMPLE

### Reddit Opportunity Detection to Processing:

1. **Detection (Every 2 hours)**
   ```
   Reddit watcher finds: "Looking for automation help"
   Creates: Pending_Approval/REDDIT_opportunity_123.md
   ```

2. **Auto Review (Optional)**
   ```
   Claude Code reviews and approves automatically
   Moves to: Approved/REDDIT_opportunity_123.md
   ```

3. **Processing (Instant)**
   ```
   Auto Processor detects file in Approved/
   Creates log: Logs/processed_20260116_123456.json
   Moves to: Done/REDDIT_opportunity_123.md
   Updates: Dashboard.md with action taken
   ```

4. **Response Generation (Next cycle)**
   ```
   Content generator creates helpful reply
   Posts via Reddit MCP (if configured)
   Logs full interaction
   ```

## 🛠️ TROUBLESHOOTING

### "Module not found"
```bash
pip install schedule watchdog pyyaml
```

### "Permission denied" (Windows)
```bash
# Run as Administrator
# Or check file permissions
```

### "Encoding errors" (special chars)
```bash
# Set UTF-8
set PYTHONUTF8=1
```

### System not starting
```bash
# Check logs
python -c "import workflow_orchestrator; w = workflow_orchestrator.WorkflowOrchestrator()"
```

## 📈 SUCCESS METRICS

After 1 week, check:
- [ ] Files processed in Done/ (should be many)
- [ ] Opportunities in Pending_Approval/
- [ ] Logs created in Logs/
- [ ] Briefings in Reports/
- [ ] Content in Reddit_Posts/
- [ ] No errors in logs

## 🎉 NEXT STEPS

1. ✅ Configure Reddit credentials in .env
2. ✅ Run: `python workflow_orchestrator.py`
3. ✅ Watch system start and monitor logs
4. ✅ Review first CEO briefing (next Sunday 10 PM)
5. ✅ Check Dashboard.md for real-time updates

## 🆘 SUPPORT

- Full documentation: DEPLOYMENT_GUIDE.md
- Reddit guide: REDDIT_INTEGRATION_COMPLETE.md
- Gold tier details: GOLD_TIER_COMPLETE.md
- System logs: Logs/

============================================================

SYSTEM STATUS: ✅ READY FOR PRODUCTION

Run: python workflow_orchestrator.py

============================================================
