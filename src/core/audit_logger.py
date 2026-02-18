#!/usr/bin/env python3
"""
Comprehensive Audit Logger
Logs all AI Employee activities for compliance and analysis
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import traceback
import codecs

# Register custom codec for reading files with emoji content
try:
    codecs.lookup('cp15040')
except LookupError:
    import codecs  # Ensure codecs is imported
    codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp15040' else None)


class AuditLogger:
    """Comprehensive audit logging system"""

    def __init__(self):
        self.vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\Desktop\\hakathone zero\\AI_Employee_Vault")
        self.logs_path = self.vault_path / "Audit_Logs"
        self.logs_path.mkdir(exist_ok=True)

        # Setup daily log file
        self.daily_log_file = self.logs_path / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"

        # Setup error log
        self.error_log_file = self.logs_path / "errors.jsonl"

        # Configure structured logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / "system.log"),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def log_action(self, action_type: str, actor: str, details: Dict[str, Any], status: str = "success"):
        """
        Log a specific action

        Args:
            action_type: Type of action (e.g., 'email_processed', 'linkedin_posted')
            actor: Who performed the action (e.g., 'AI_Employee', 'Claude_Code')
            details: Additional details about the action
            status: Status of the action (success, failed, pending)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "status": status,
            "details": details
        }

        try:
            with open(self.daily_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            self.logger.info(f"{action_type}: {status}")
        except Exception as e:
            print(f"Failed to write audit log: {e}")

    def log_email_processed(self, email_id: str, sender: str, subject: str, action_taken: str):
        """Log email processing"""
        self.log_action(
            action_type="email_processed",
            actor="AI_Employee",
            details={
                "email_id": email_id,
                "sender": sender,
                "subject": subject[:100],  # Truncate long subjects
                "action_taken": action_taken
            }
        )

    def log_linkedin_post(self, content_preview: str, engagement: Dict[str, Any] = None):
        """Log LinkedIn post"""
        self.log_action(
            action_type="linkedin_posted",
            actor="AI_Employee",
            details={
                "content_preview": content_preview[:100],
                "engagement": engagement or {}
            }
        )

    def log_social_media_post(self, platform: str, content: str, post_id: str = None):
        """Log social media post"""
        self.log_action(
            action_type="social_media_posted",
            actor="AI_Employee",
            details={
                "platform": platform,
                "content_preview": content[:100],
                "post_id": post_id
            }
        )

    def log_task_created(self, task_id: str, task_description: str, platform: str = "general"):
        """Log task creation"""
        self.log_action(
            action_type="task_created",
            actor="AI_Employee",
            details={
                "task_id": task_id,
                "task_description": task_description[:100],
                "platform": platform
            }
        )

    def log_task_completed(self, task_id: str, completion_notes: str = ""):
        """Log task completion"""
        self.log_action(
            action_type="task_completed",
            actor="AI_Employee",
            details={
                "task_id": task_id,
                "completion_notes": completion_notes[:100]
            }
        )

    def log_approval_requested(self, item_id: str, item_type: str, reason: str):
        """Log approval request"""
        self.log_action(
            action_type="approval_requested",
            actor="AI_Employee",
            details={
                "item_id": item_id,
                "item_type": item_type,
                "reason": reason[:100]
            }
        )

    def log_approval_granted(self, item_id: str, approved_by: str):
        """Log approval grant"""
        self.log_action(
            action_type="approval_granted",
            actor=approved_by,
            details={"item_id": item_id}
        )

    def log_error(self, error_type: str, error_message: str, stack_trace: str = None, context: Dict = None):
        """
        Log an error

        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Full stack trace
            context: Additional context
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context or {}
        }

        try:
            with open(self.error_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            self.logger.error(f"{error_type}: {error_message}")
        except Exception as e:
            print(f"Failed to write error log: {e}")

    def log_mcp_action(self, mcp_server: str, action: str, parameters: Dict[str, Any], result: Dict[str, Any]):
        """Log MCP server action"""
        self.log_action(
            action_type="mcp_action",
            actor=f"MCP_{mcp_server}",
            details={
                "mcp_server": mcp_server,
                "action": action,
                "parameters": parameters,
                "result_status": "success" if result.get("success", False) else "failed"
            }
        )

    def log_watcher_event(self, watcher_type: str, event_type: str, event_data: Dict[str, Any]):
        """Log watcher event"""
        self.log_action(
            action_type="watcher_event",
            actor=f"Watcher_{watcher_type}",
            details={
                "watcher_type": watcher_type,
                "event_type": event_type,
                "event_data": event_data
            }
        )

    def log_system_startup(self, components: List[str]):
        """Log system startup"""
        self.log_action(
            action_type="system_startup",
            actor="System",
            details={
                "components_started": components,
                "startup_time": datetime.now().isoformat()
            }
        )

    def log_system_shutdown(self, reason: str = "Normal shutdown"):
        """Log system shutdown"""
        self.log_action(
            action_type="system_shutdown",
            actor="System",
            details={
                "reason": reason,
                "shutdown_time": datetime.now().isoformat()
            }
        )

    def get_daily_summary(self, date: datetime = None) -> Dict[str, Any]:
        """Get daily activity summary"""
        if date is None:
            date = datetime.now()

        log_file = self.logs_path / f"audit_{date.strftime('%Y%m%d')}.jsonl"

        if not log_file.exists():
            return {"error": "No logs found for date"}

        summary = {
            "date": date.strftime("%Y-%m-%d"),
            "total_actions": 0,
            "actions_by_type": {},
            "actions_by_status": {},
            "errors": 0
        }

        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        summary["total_actions"] += 1

                        action_type = entry.get("action_type", "unknown")
                        summary["actions_by_type"][action_type] = summary["actions_by_type"].get(action_type, 0) + 1

                        status = entry.get("status", "unknown")
                        summary["actions_by_status"][status] = summary["actions_by_status"].get(status, 0) + 1

                        if action_type == "error" or status == "failed":
                            summary["errors"] += 1

        except Exception as e:
            self.logger.error(f"Failed to generate daily summary: {e}")

        return summary

    def get_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive audit report for date range"""
        report = {
            "period_start": start_date.strftime("%Y-%m-%d"),
            "period_end": end_date.strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_actions": 0,
                "actions_by_type": {},
                "errors": 0,
                "mcp_actions": 0,
                "emails_processed": 0,
                "tasks_completed": 0,
                "posts_created": 0
            },
            "detailed_logs": []
        }

        current_date = start_date
        while current_date <= end_date:
            daily_file = self.logs_path / f"audit_{current_date.strftime('%Y%m%d')}.jsonl"

            if daily_file.exists():
                try:
                    with open(daily_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                entry = json.loads(line)
                                report["summary"]["total_actions"] += 1

                                action_type = entry.get("action_type")
                                report["summary"]["actions_by_type"][action_type] = report["summary"]["actions_by_type"].get(action_type, 0) + 1

                                # Count specific action types
                                if action_type == "email_processed":
                                    report["summary"]["emails_processed"] += 1
                                elif action_type == "task_completed":
                                    report["summary"]["tasks_completed"] += 1
                                elif action_type == "social_media_posted":
                                    report["summary"]["posts_created"] += 1
                                elif action_type == "mcp_action":
                                    report["summary"]["mcp_actions"] += 1

                                if entry.get("status") == "failed":
                                    report["summary"]["errors"] += 1

                                # Add to detailed logs
                                report["detailed_logs"].append({
                                    "date": current_date.strftime("%Y-%m-%d"),
                                    "action": entry
                                })

                except Exception as e:
                    self.logger.error(f"Failed to process {daily_file}: {e}")

            current_date += datetime.timedelta(days=1)

        return report

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        cutoff_date = datetime.now() - datetime.timedelta(days=days_to_keep)

        try:
            for log_file in self.logs_path.glob("audit_*.jsonl"):
                # Extract date from filename
                filename = log_file.name
                date_str = filename.replace("audit_", "").replace(".jsonl", "")

                try:
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    if file_date < cutoff_date:
                        log_file.unlink()
                        self.logger.info(f"Deleted old log file: {log_file}")
                except ValueError:
                    continue

        except Exception as e:
            self.logger.error(f"Failed to cleanup logs: {e}")


def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Audit Logger')
    parser.add_argument('action', choices=[
        'daily_summary',
        'audit_report',
        'cleanup'
    ], help='Action to perform')

    parser.add_argument('--date', help='Date for summary (YYYY-MM-DD)')
    parser.add_argument('--start-date', help='Start date for report (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for report (YYYY-MM-DD)')
    parser.add_argument('--days-to-keep', type=int, default=30, help='Days to keep logs')

    args = parser.parse_args()

    logger = AuditLogger()

    if args.action == 'daily_summary':
        if args.date:
            date = datetime.datetime.strptime(args.date, "%Y-%m-%d")
        else:
            date = datetime.datetime.now()

        summary = logger.get_daily_summary(date)
        print(json.dumps(summary, indent=2))

    elif args.action == 'audit_report':
        if not args.start_date or not args.end_date:
            print(json.dumps({"error": "--start-date and --end-date required"}))
            sys.exit(1)

        start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")

        report = logger.get_audit_report(start_date, end_date)
        print(json.dumps(report, indent=2))

    elif args.action == 'cleanup':
        logger.cleanup_old_logs(args.days_to_keep)
        print(f"Cleaned up logs older than {args.days_to_keep} days")


if __name__ == '__main__':
    import datetime
    main()
