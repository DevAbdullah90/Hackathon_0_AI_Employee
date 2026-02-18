# AI Employee - Silver Tier Implementation

This project implements the Silver Tier requirements for the AI Employee Hackathon as outlined in the haka.md document.

## Silver Tier Requirements Status

✅ **Two or more Watcher scripts**:
- Gmail Watcher (monitors emails and creates action items)
- WhatsApp Watcher (monitors WhatsApp messages for keywords)
- LinkedIn Watcher (monitors LinkedIn for opportunities and generates content)
- Filesystem Watcher (watches for file drops in Inbox folder)

✅ **Automatically Post on LinkedIn about business to generate sales**:
- LinkedIn content generator creates sales-focused posts
- Approval workflow for LinkedIn posts in Pending_Approval folder
- Automated monitoring and opportunity identification

✅ **Claude reasoning loop that creates Plan.md files**:
- Plan creator module (plan_creator.py) generates structured plans
- Automatic scanning of Needs_Action and Inbox folders for planning opportunities
- Plans are saved to the Plans directory with tracking files

✅ **One working MCP server for external action**:
- Email MCP server in mcp/email-mcp directory
- Handles sending emails and creating email drafts
- Integrates with Claude Code via Model Context Protocol

✅ **Human-in-the-loop approval workflow**:
- Pending_Approval, Approved, and Rejected folder system
- Approval requirements for sensitive actions (payments, emails, etc.)
- File-based workflow for human approvals

✅ **Basic scheduling via cron or Task Scheduler**:
- Scheduler script (scheduler.py) handles periodic tasks
- Windows batch script (start_scheduler.bat) for easy startup
- Scheduled tasks for email monitoring, WhatsApp monitoring, LinkedIn monitoring, plan generation, and dashboard updates

## System Architecture

The AI Employee system follows the architecture described in haka.md:

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     Gmail       │    WhatsApp     │     LinkedIn    │  Files   │
└────────┬────────┴────────┬────────┴─────────┬────────┴────┬─────┘
         │                 │                  │             │
         ▼                 ▼                  ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Gmail Watcher│ │WhatsApp Watch│ │LinkedIn Watch│            │
│  │  (Python)    │ │ (Playwright) │ │   (Python)   │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Local)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /Needs_Action/  │ /Plans/  │ /Done/  │ /Logs/            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Dashboard.md    │ Company_Handbook.md │ Business_Goals.md│  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ /Pending_Approval/  │  /Approved/  │  /Rejected/         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      CLAUDE CODE                          │ │
│  │   Read → Think → Plan → Write → Request Approval          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
              ┌──────────────────┴───────────────────┐
              ▼                                      ▼
┌────────────────────────────┐    ┌────────────────────────────────┐
│    HUMAN-IN-THE-LOOP       │    │         ACTION LAYER           │
│  ┌──────────────────────┐  │    │  ┌─────────────────────────┐   │
│  │ Review Approval Files│──┼───▶│  │    MCP SERVERS          │   │
│  │ Move to /Approved    │  │    │  │  ┌──────┐ ┌──────────┐  │   │
│  └──────────────────────┘  │    │  │  │Email │ │ Browser  │  │   │
│                            │    │  │  │ MCP  │ │   MCP    │  │   │
│                            │    │  │  └──┬───┘ └────┬─────┘  │   │
└────────────────────────────┘    │  └─────┼──────────┼────────┘   │
                                  │        │          │             │
                                  └────────┼──────────┼────────────┘
                                           │          │
                                           ▼          ▼
                                  ┌────────────────────────────────┐
                                  │     EXTERNAL ACTIONS           │
                                  │  Send Email │ Make Payment     │
                                  │  Post Social│ Update Calendar  │
                                  └────────────────────────────────┘
```

## Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   cd mcp/email-mcp
   npm install
   ```

2. **Start the System**:
   ```bash
   # Using the startup script
   start_system.bat
   ```

3. **Or Start Components Individually**:
   ```bash
   # Start scheduler
   python scheduler.py

   # Start MCP server
   cd mcp/email-mcp
   node index.js
   ```

## Configuration

The system uses the following folder structure:
- `/Inbox` - Incoming items to be processed
- `/Needs_Action` - Items requiring action
- `/Done` - Completed tasks
- `/Pending_Approval` - Items awaiting human approval
- `/Approved` - Approved items
- `/Rejected` - Rejected items
- `/Plans` - Generated plan files
- `/Logs` - System logs
- `/watchers` - Watcher scripts
- `/mcp` - Model Context Protocol servers

## Features

- **Automated Monitoring**: Continuously monitors Gmail, WhatsApp, and LinkedIn
- **Smart Classification**: Identifies urgent items, opportunities, and sales leads
- **Plan Generation**: Creates structured plans from identified opportunities
- **Approval Workflows**: Human-in-the-loop for sensitive actions
- **LinkedIn Engagement**: Monitors and generates sales-focused content
- **Scheduling**: Automated periodic tasks and system maintenance
- **MCP Integration**: External action capabilities via Model Context Protocol

## Next Steps (Gold Tier)

For Gold Tier implementation, consider:
- Cross-domain integration (Personal + Business)
- Accounting system integration (Xero)
- Multi-platform social media posting (Facebook, Instagram, Twitter)
- Advanced audit logging
- Error recovery mechanisms