#!/usr/bin/env python3
"""
Vault Sync Manager for AI Employee
Implements secure synchronization between cloud and local vaults
"""

import os
import json
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VaultSyncManager:
    """Manages secure synchronization between cloud and local vaults"""

    def __init__(self, vault_path: str, remote_repo: str = None):
        self.vault_path = Path(vault_path)
        self.remote_repo = remote_repo
        self.gitignore_rules = [
            # Sensitive files
            ".env",
            "*.env",
            "*.key",
            "*.pem",
            "*.crt",
            "credentials.json",
            "tokens.json",
            "whatsapp_session/*",
            "banking_creds/*",
            "secrets/*",

            # Obsidian specific
            ".obsidian/workspace.json",
            ".obsidian/graph.json",
            "*.swp",
            "*.tmp",
            ".DS_Store",
            "Thumbs.db",

            # Temp files
            "*.tmp",
            "*.temp",
            "temp/",
            "cache/"
        ]

        # Safe file extensions to sync
        self.allowed_extensions = {
            '.md', '.txt', '.json', '.py', '.js', '.html', '.css',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.csv', '.xlsx'
        }

        # Initialize git if not already
        self._init_git()

    def _init_git(self):
        """Initialize git repository in vault if not present"""
        git_dir = self.vault_path / '.git'
        if not git_dir.exists():
            try:
                subprocess.run(['git', 'init'], cwd=self.vault_path, check=True)

                # Create initial .gitignore
                self._create_gitignore()

                # Create initial commit
                subprocess.run(['git', 'add', '.'], cwd=self.vault_path, check=True)
                subprocess.run(['git', 'commit', '-m', 'Initial vault setup'], cwd=self.vault_path, check=True)

                logger.info("Git repository initialized in vault")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to initialize git: {e}")
            except FileNotFoundError:
                logger.warning("Git not found. Vault sync requires git to be installed.")
        else:
            # Update .gitignore if repository already exists
            self._create_gitignore()

    def _create_gitignore(self):
        """Create .gitignore file with security rules"""
        gitignore_path = self.vault_path / '.gitignore'
        gitignore_content = '\n'.join(self.gitignore_rules) + '\n'

        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)

        logger.info(".gitignore created with security rules")

    def sync_to_remote(self) -> bool:
        """Sync vault changes to remote repository"""
        if not self.remote_repo:
            logger.warning("No remote repository configured for sync")
            return False

        try:
            # Add all allowed files
            subprocess.run(['git', 'add', '.'], cwd=self.vault_path, check=True)

            # Check for changes
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  cwd=self.vault_path,
                                  capture_output=True,
                                  text=True)

            if not result.stdout.strip():
                logger.info("No changes to sync")
                return True

            # Commit changes
            commit_msg = f"Vault sync update {datetime.now().isoformat()}"
            subprocess.run(['git', 'commit', '-m', commit_msg],
                          cwd=self.vault_path,
                          check=True)

            # Add remote if not already added
            try:
                subprocess.run(['git', 'remote', 'set-url', 'origin', self.remote_repo],
                              cwd=self.vault_path,
                              check=True)
            except subprocess.CalledProcessError:
                subprocess.run(['git', 'remote', 'add', 'origin', self.remote_repo],
                              cwd=self.vault_path,
                              check=True)

            # Push to remote
            subprocess.run(['git', 'push', '-u', 'origin', 'main'],
                          cwd=self.vault_path,
                          check=True)

            logger.info(f"Successfully synced vault to remote: {self.remote_repo}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync to remote: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during sync: {e}")
            return False

    def sync_from_remote(self) -> bool:
        """Sync changes from remote repository to local vault"""
        if not self.remote_repo:
            logger.warning("No remote repository configured for sync")
            return False

        try:
            # Add remote if not already added
            try:
                subprocess.run(['git', 'remote', 'set-url', 'origin', self.remote_repo],
                              cwd=self.vault_path,
                              check=True)
            except subprocess.CalledProcessError:
                subprocess.run(['git', 'remote', 'add', 'origin', self.remote_repo],
                              cwd=self.vault_path,
                              check=True)

            # Fetch and merge changes
            subprocess.run(['git', 'fetch', 'origin'], cwd=self.vault_path, check=True)
            subprocess.run(['git', 'merge', 'origin/main'], cwd=self.vault_path, check=True)

            logger.info(f"Successfully synced vault from remote: {self.remote_repo}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync from remote: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during sync: {e}")
            return False

    def is_safe_to_sync(self, file_path: Path) -> bool:
        """Check if a file is safe to sync based on security rules"""
        # Check file extension
        if file_path.suffix.lower() not in self.allowed_extensions:
            return False

        # Check against gitignore patterns
        file_str = str(file_path.relative_to(self.vault_path)).replace('\\', '/')

        for pattern in self.gitignore_rules:
            if '*' in pattern:
                # Handle wildcard patterns
                import fnmatch
                if fnmatch.fnmatch(file_str, pattern):
                    return False
            else:
                # Handle exact matches
                if file_str == pattern or file_str.startswith(pattern.rstrip('/*')):
                    return False

        return True

    def get_syncable_files(self) -> List[Path]:
        """Get list of files that are safe to sync"""
        syncable_files = []

        for file_path in self.vault_path.rglob('*'):
            if file_path.is_file() and self.is_safe_to_sync(file_path):
                syncable_files.append(file_path)

        return syncable_files

    def validate_sync_security(self) -> Dict[str, Any]:
        """Validate that sync configuration is secure"""
        issues = []

        # Check for sensitive files that might be accidentally included
        for file_path in self.vault_path.rglob('*'):
            if file_path.is_file() and not self.is_safe_to_sync(file_path):
                issues.append(f"Potentially unsafe file: {file_path}")

        # Check git status
        try:
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  cwd=self.vault_path,
                                  capture_output=True,
                                  text=True)

            # Check for untracked files that might be sensitive
            for line in result.stdout.split('\n'):
                if line.startswith('??'):  # Untracked file
                    file_name = line[3:].strip()
                    full_path = self.vault_path / file_name
                    if full_path.is_file() and not self.is_safe_to_sync(full_path):
                        issues.append(f"Untracked sensitive file: {full_path}")

        except Exception as e:
            issues.append(f"Could not validate git status: {e}")

        return {
            'is_secure': len(issues) == 0,
            'issues': issues,
            'syncable_files_count': len(self.get_syncable_files())
        }


class ClaimByMoveRule:
    """Implements the claim-by-move rule to prevent double-work"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'

        # Create required directories
        self.needs_action.mkdir(exist_ok=True)
        self.in_progress.mkdir(exist_ok=True)

    def claim_task(self, task_file: Path, agent_name: str) -> Path:
        """
        Claim a task by moving it to the agent's in-progress folder
        Returns the new location if successful, None if already claimed
        """
        agent_progress = self.in_progress / agent_name
        agent_progress.mkdir(exist_ok=True)

        destination = agent_progress / task_file.name

        try:
            # Attempt to move the file atomically
            shutil.move(str(task_file), str(destination))
            logger.info(f"Agent {agent_name} claimed task: {task_file.name}")
            return destination
        except FileNotFoundError:
            # File was already moved by another agent
            logger.warning(f"Task {task_file.name} already claimed by another agent")
            return None
        except Exception as e:
            logger.error(f"Error claiming task {task_file.name}: {e}")
            return None

    def release_task(self, task_file: Path, destination_folder: str) -> Path:
        """Release a completed task to the specified destination folder"""
        dest_path = self.vault_path / destination_folder
        dest_path.mkdir(exist_ok=True)

        final_destination = dest_path / task_file.name

        try:
            shutil.move(str(task_file), str(final_destination))
            logger.info(f"Task released to {destination_folder}: {task_file.name}")
            return final_destination
        except Exception as e:
            logger.error(f"Error releasing task {task_file.name}: {e}")
            return task_file

    def get_available_tasks(self) -> List[Path]:
        """Get list of unclaimed tasks in Needs_Action"""
        tasks = []
        for file_path in self.needs_action.glob('*.md'):
            tasks.append(file_path)
        return tasks


class DashboardUpdater:
    """Manages the single-writer rule for Dashboard.md (Local ownership)"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        self.updates_path = self.vault_path / 'Updates'

        # Create updates directory
        self.updates_path.mkdir(exist_ok=True)

    def create_initial_dashboard(self):
        """Create initial dashboard if it doesn't exist"""
        if not self.dashboard_path.exists():
            initial_content = f"""# AI Employee Dashboard

## Bank Balance
**Current:** $0.00

## Pending Messages
- No pending messages

## Active Business Projects
- No active projects

## System Status
- All systems operational

## Last Updated
{datetime.now().isoformat()}

## Recent Activity
- System initialized
"""
            self.dashboard_path.write_text(initial_content)
            logger.info("Initial dashboard created")

    def merge_updates_from_cloud(self):
        """Merge updates from cloud into local dashboard (Local responsibility)"""
        if not self.dashboard_path.exists():
            self.create_initial_dashboard()

        # Read current dashboard
        dashboard_content = self.dashboard_path.read_text()

        # Process each update file from cloud
        for update_file in self.updates_path.glob('*.json'):
            try:
                update_data = json.loads(update_file.read_text())

                # Apply update to dashboard content
                updated_content = self._apply_update_to_dashboard(dashboard_content, update_data)

                # Write updated dashboard
                self.dashboard_path.write_text(updated_content)

                # Mark update as processed by moving to processed directory
                processed_dir = self.updates_path / 'Processed'
                processed_dir.mkdir(exist_ok=True)
                shutil.move(str(update_file), processed_dir / update_file.name)

                logger.info(f"Merged update from cloud: {update_file.name}")

            except Exception as e:
                logger.error(f"Error processing update {update_file.name}: {e}")

    def _apply_update_to_dashboard(self, dashboard_content: str, update_data: Dict[str, Any]) -> str:
        """Apply a specific update to the dashboard content"""
        import re

        # Update bank balance if provided
        if 'bank_balance' in update_data:
            dashboard_content = re.sub(
                r'\*\*Current:\*\* \$[\d,\.]+',
                f"**Current:** ${update_data['bank_balance']}",
                dashboard_content
            )

        # Update pending messages if provided
        if 'pending_messages' in update_data:
            messages_section = "## Pending Messages\n"
            for msg in update_data['pending_messages']:
                messages_section += f"- {msg}\n"

            # Replace the pending messages section
            pattern = r'## Pending Messages\n.*?(?=## |\Z)'
            dashboard_content = re.sub(
                pattern,
                messages_section,
                dashboard_content,
                flags=re.DOTALL
            )

        # Add recent activity if provided
        if 'recent_activity' in update_data:
            activity_section = "## Recent Activity\n"
            for activity in update_data['recent_activity']:
                activity_section += f"- {activity}\n"

            # Append to recent activity section
            if "## Recent Activity" in dashboard_content:
                # Replace existing section
                pattern = r'## Recent Activity\n.*?(?=## |\Z)'
                dashboard_content = re.sub(
                    pattern,
                    activity_section,
                    dashboard_content,
                    flags=re.DOTALL
                )
            else:
                # Add new section at the end
                dashboard_content += f"\n{activity_section}"

        # Update last updated timestamp
        last_updated_section = f"## Last Updated\n{datetime.now().isoformat()}\n"
        pattern = r'## Last Updated\n.*?(?=## |\Z)'
        dashboard_content = re.sub(
            pattern,
            last_updated_section,
            dashboard_content,
            flags=re.DOTALL
        )

        return dashboard_content

    def write_update_for_cloud(self, update_data: Dict[str, Any]):
        """Write an update that cloud can process (when local needs to communicate with cloud)"""
        update_file = self.updates_path / f"local_update_{int(time.time())}.json"

        with open(update_file, 'w') as f:
            json.dump(update_data, f, indent=2)

        logger.info(f"Local update written for cloud: {update_file.name}")


def main():
    """Example usage of the vault sync manager"""
    vault_path = "./vault_example"  # Change to your actual vault path
    remote_repo = os.getenv("VAULT_REMOTE_REPO")  # Set your remote repo URL

    # Initialize managers
    sync_manager = VaultSyncManager(vault_path, remote_repo)
    claim_manager = ClaimByMoveRule(vault_path)
    dashboard_manager = DashboardUpdater(vault_path)

    # Validate security
    security_check = sync_manager.validate_sync_security()
    print(f"Sync security check: {'Secure' if security_check['is_secure'] else 'Issues found'}")
    if security_check['issues']:
        print("Issues:", security_check['issues'])

    # Example of claiming a task
    available_tasks = claim_manager.get_available_tasks()
    if available_tasks:
        task = available_tasks[0]
        claimed_task = claim_manager.claim_task(task, "cloud_agent")
        if claimed_task:
            print(f"Task claimed: {claimed_task}")

    # Example of dashboard update
    dashboard_manager.create_initial_dashboard()
    dashboard_manager.merge_updates_from_cloud()

    # Example of syncing
    if remote_repo:
        sync_manager.sync_to_remote()
        sync_manager.sync_from_remote()


if __name__ == "__main__":
    main()