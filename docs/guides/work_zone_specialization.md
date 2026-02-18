# Work-Zone Specialization Architecture

## Overview
This document describes the architecture for separating cloud and local responsibilities in the AI Employee system.

## Domain Ownership Structure

### Cloud Responsibilities
- **Email Triage**: Monitor and categorize incoming emails
- **Draft Replies**: Generate initial responses to common queries
- **Social Post Drafts**: Create content and schedule posts
- **Initial Processing**: Basic data processing and categorization

### Local Responsibilities
- **Approvals**: Final approval of sensitive actions
- **WhatsApp Session**: Handle real-time messaging
- **Payments/Banking**: Execute financial transactions
- **Final Send/Post Actions**: Execute approved communications
- **Vault Management**: Control access to sensitive data

## File Structure for Communication

### `/Needs_Action/<domain>/`
- **Cloud**: Creates files in `Needs_Action/cloud/` for local processing
- **Local**: Creates files in `Needs_Action/local/` for cloud processing

### `/Plans/<domain>/`
- **Cloud**: Creates planning files for cloud-managed tasks
- **Local**: Creates planning files for local-managed tasks

### `/Pending_Approval/<domain>/`
- **Cloud**: Places draft actions in `Pending_Approval/cloud/`
- **Local**: Reviews and moves to `Approved/` or `Rejected/`

## Claim-by-Move Rule Implementation

### Preventing Double-Work
```python
# Example implementation for claim-by-move rule
import os
import shutil
from pathlib import Path
import time

class ClaimByMoveManager:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.in_progress = self.vault_path / "In_Progress"

    def claim_task(self, task_file, agent_name):
        """
        Claim a task by moving it to the agent's in-progress folder
        First agent to move the file gets ownership
        """
        agent_progress = self.in_progress / agent_name

        # Create agent-specific in-progress directory
        agent_progress.mkdir(parents=True, exist_ok=True)

        # Move the task file to agent's in-progress folder
        destination = agent_progress / task_file.name

        try:
            shutil.move(str(task_file), str(destination))
            return destination
        except FileNotFoundError:
            # Task was already claimed by another agent
            return None

    def release_task(self, task_file, destination_folder):
        """Release a task to a specific folder when complete"""
        destination = self.vault_path / destination_folder
        destination.mkdir(exist_ok=True)

        final_destination = destination / task_file.name
        shutil.move(str(task_file), str(final_destination))
        return final_destination

# Usage example:
# manager = ClaimByMoveManager("/path/to/vault")
# task_to_claim = Path("/Needs_Action/some_task.md")
# claimed_task = manager.claim_task(task_to_claim, "cloud_agent")
# if claimed_task:
#     # Process the task
#     manager.release_task(claimed_task, "Done")
```

## Single-Writer Rule for Dashboard.md

### Local Ownership of Dashboard
- Only the local agent can write to `Dashboard.md`
- Cloud agent writes updates to `/Updates/` which local agent merges

### Merge Process
```python
# Example dashboard merger
import json
from datetime import datetime
from pathlib import Path

class DashboardMerger:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.dashboard_path = self.vault_path / "Dashboard.md"
        self.updates_path = self.vault_path / "Updates"

    def merge_updates(self):
        """Merge updates from cloud into local dashboard"""
        if not self.dashboard_path.exists():
            # Create initial dashboard
            self._create_initial_dashboard()

        dashboard_content = self.dashboard_path.read_text()

        # Process each update file
        for update_file in self.updates_path.glob("*.json"):
            update_data = json.loads(update_file.read_text())

            # Apply update to dashboard content
            dashboard_content = self._apply_update(dashboard_content, update_data)

            # Mark update as processed by moving it
            processed_dir = self.updates_path / "Processed"
            processed_dir.mkdir(exist_ok=True)
            shutil.move(str(update_file), processed_dir / update_file.name)

        # Write updated dashboard
        self.dashboard_path.write_text(dashboard_content)

    def _create_initial_dashboard(self):
        """Create initial dashboard structure"""
        initial_content = """# AI Employee Dashboard

## Bank Balance
**Current:** $0.00

## Pending Messages
- No pending messages

## Active Business Projects
- No active projects

## System Status
- All systems operational

## Last Updated
{}
""".format(datetime.now().isoformat())
        self.dashboard_path.write_text(initial_content)

    def _apply_update(self, dashboard_content, update_data):
        """Apply a specific update to dashboard content"""
        # Example: Update bank balance
        if 'bank_balance' in update_data:
            import re
            dashboard_content = re.sub(
                r'\*\*Current:\*\* \$[\d,\.]+',
                f"**Current:** ${update_data['bank_balance']}",
                dashboard_content
            )

        # Example: Update pending messages
        if 'new_messages' in update_data:
            # Add new messages to pending section
            pass

        return dashboard_content
```

## Vault Sync Configuration (Phase 1)

### Git-based Sync
```bash
# Git configuration for vault sync
# Only sync non-sensitive files

# .gitignore for vault
cat > .gitignore << EOF
# Sensitive files never synced
.env
*.env
*.key
*.pem
*.crt
credentials.json
tokens.json
whatsapp_session/*
banking_creds/*
secrets/

# Obsidian specific
.obsidian/workspace.json
.obsidian/graph.json
*.swp
*.tmp
.DS
.DS_Store
Thumbs.db

# Sync only these
*.md
*.txt
*.csv
*.json
*.py
*.js
*.html
*.css
*.png
*.jpg
*.jpeg
*.gif
*.svg
EOF

# Create sync script
cat > sync_vault.sh << EOF
#!/bin/bash
# Vault sync script for cloud-local synchronization

VAULT_DIR="$HOME/ai_employee_vault"
REMOTE_REPO="your-private-git-repo-url"
BRANCH="main"

cd $VAULT_DIR

# Pull latest changes from remote
git pull origin $BRANCH

# Add all non-sensitive changes
git add *.md *.txt *.json *.py *.js *.html *.css *.png *.jpg *.jpeg *.gif *.svg

# Commit changes with timestamp
git commit -m "Sync update $(date)"

# Push to remote
git push origin $BRANCH

echo "Vault sync completed at $(date)"
EOF

chmod +x sync_vault.sh

# Schedule sync every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * $HOME/ai_employee_vault/sync_vault.sh") | crontab -
```

### Syncthing Alternative (if preferred)
```bash
# Install Syncthing
curl -s https://syncthing.net/release-key.txt | sudo apt-key add -
echo "deb https://apt.syncthing.net/ syncthing stable" | sudo tee /etc/apt/sources.list.d/syncthing.list
sudo apt update
sudo apt install syncthing

# Configure Syncthing to sync only allowed directories
# Create config file with ignore patterns for sensitive files
```

## Security Rules

### Vault Sync Restrictions
- **Never sync**: `.env`, tokens, WhatsApp sessions, banking credentials
- **Always sync**: Markdown files, state files, configuration (non-secret)
- **Cloud never stores**: WhatsApp sessions, banking credentials, payment tokens

### Access Control
```bash
# Example: Restrict sensitive directory access
chmod 700 /path/to/sensitive/data
chmod 600 /path/to/sensitive/*.key
chown ai_employee:ai_employee /path/to/sensitive/data
```

## Communication Protocol

### Cloud-to-Local Communication
1. Cloud writes approval requests to `/Pending_Approval/`
2. Local monitors the folder and processes requests
3. Local moves files to `/Approved/` or `/Rejected/`
4. Cloud monitors approved/rejected folders and acts accordingly

### Local-to-Cloud Communication
1. Local writes status updates to `/Updates/`
2. Cloud periodically polls `/Updates/` and processes updates
3. Cloud updates its internal state based on received updates

## Example Workflow: Email Arrives While Local is Offline

### Phase 1: Cloud Detection
1. Cloud's email watcher detects new email
2. Creates `/Needs_Action/cloud/EMAIL_abc123.md`
3. Cloud AI processes the email and drafts reply
4. Creates `/Pending_Approval/CLOUD_EMAIL_REPLY_abc123.md`

### Phase 2: Local Returns Online
1. Local user sees pending approval file
2. Reviews and approves by moving to `/Approved/`
3. Local executes send via MCP
4. Local logs action and moves task to `/Done/`
5. Updates reflected in dashboard

This architecture ensures secure, distributed operation with clear role separation between cloud and local components.