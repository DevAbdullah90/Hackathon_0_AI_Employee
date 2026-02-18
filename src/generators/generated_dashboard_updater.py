"""
Dynamic Dashboard Updater generated from dashboard_updater.md skill definition
"""
import os
import json
import datetime
import re
import time
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter

class SystemStatus(Enum):
    GREEN = "🟢"
    YELLOW = "🟡"
    RED = "🔴"
    GRAY = "⚪"

class DashboardUpdater:
    """
    The Dashboard Updater maintains real-time statistics and status information on the main dashboard.
    """

    def __init__(self):
        # Configuration variables from skill definition
        self.DASHBOARD_PATH = "Dashboard.md"
        self.LOGS_PATH = "Logs"
        self.UPDATE_INTERVAL = 60  # seconds
        self.MAX_ACTIVITY_LOG_ENTRIES = 10

        # Initialize dashboard if it doesn't exist
        self.initialize_dashboard_if_needed()

    def initialize_dashboard_if_needed(self):
        """Initialize dashboard if it doesn't exist"""
        if not os.path.exists(self.DASHBOARD_PATH):
            default_dashboard = """# 🚀 AI Employee Dashboard


## 📊 Quick Stats
- 📧 Pending emails: 0
- 💬 Unread WhatsApp: 0
- 📋 Tasks in Need Action: 0
- ✅ Tasks Completed: 0
- 📂 Total monitored items: 0

## 📈 System Status
- 🟢 Email Monitoring: Active
- 🟢 WhatsApp Monitoring: Active
- 📬 Inbox Status: Empty
- 📁 Workflow Progress: 0% complete

## 🎯 Today's Priorities
1. Initialize system

## 📅 Recent Activity Log


## ⚠️ Important Notifications


## 🔄 Workflow Status
- Inbox: 0 items
- Needs Action: 0 items
- Done: 0 items
- Next Action: System initialization complete

## 🛠️ System Configuration
- Last System Check: 1970-01-01 00:00:00
"""
            with open(self.DASHBOARD_PATH, 'w', encoding='utf-8') as f:
                f.write(default_dashboard)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect current system metrics from all data collection points
        """
        metrics = {
            'pending_emails': self.get_pending_email_count(),
            'unread_whatsapp': self.get_unread_whatsapp_count(),
            'tasks_needs_action': self.get_tasks_needs_action_count(),
            'tasks_completed': self.get_tasks_done_count(),
            'total_monitored_items': self.get_total_monitored_count(),
            'system_uptime': self.get_system_uptime(),
            'error_count': self.get_error_count(),
            'inbox_count': self.get_inbox_count(),
            'recent_activities': self.get_recent_activities(),
            'priority_indicators': self.get_priority_items(),
            'email_monitoring_status': self.get_email_monitoring_status(),
            'whatsapp_monitoring_status': self.get_whatsapp_monitoring_status()
        }

        return metrics

    def get_pending_email_count(self) -> int:
        """Get current unread email count"""
        # This would typically connect to email API to get actual count
        # For simulation, we'll look for email files in Needs_Action
        needs_action_path = "Needs_Action"
        if not os.path.exists(needs_action_path):
            return 0

        email_files = [f for f in os.listdir(needs_action_path) if f.startswith("EMAIL_")]
        return len(email_files)

    def get_unread_whatsapp_count(self) -> int:
        """Get unread WhatsApp messages count"""
        # This would typically connect to WhatsApp API
        # For simulation, we'll return a value based on log files
        logs_path = self.LOGS_PATH
        if not os.path.exists(logs_path):
            return 0

        # Look for recent WhatsApp activity in log files
        whatsapp_logs = [f for f in os.listdir(logs_path) if "whatsapp" in f.lower()]
        if whatsapp_logs:
            # For demo, return a value based on the most recent log
            return 5  # Placeholder value
        return 0

    def get_tasks_needs_action_count(self) -> int:
        """Get count of tasks in Needs_Action folder"""
        needs_action_path = "Needs_Action"
        if not os.path.exists(needs_action_path):
            return 0

        return len(os.listdir(needs_action_path))

    def get_tasks_done_count(self) -> int:
        """Get count of completed tasks in Done folder"""
        done_path = "Done"
        if not os.path.exists(done_path):
            return 0

        return len(os.listdir(done_path))

    def get_total_monitored_count(self) -> int:
        """Get total count of all processed items"""
        total = 0
        for folder in ["Inbox", "Needs_Action", "Done"]:
            if os.path.exists(folder):
                total += len(os.listdir(folder))

        # Add log entries as proxy for monitored items
        if os.path.exists(self.LOGS_PATH):
            for log_file in os.listdir(self.LOGS_PATH):
                if log_file.endswith('.log'):
                    total += self.count_lines_in_file(os.path.join(self.LOGS_PATH, log_file)) // 10

        return total

    def get_system_uptime(self) -> str:
        """Calculate system uptime"""
        # For demo, return a fixed uptime
        return "Active for 24 hours"

    def get_error_count(self) -> int:
        """Get count of system errors"""
        error_count = 0
        if os.path.exists(self.LOGS_PATH):
            for log_file in os.listdir(self.LOGS_PATH):
                if log_file.endswith('.log'):
                    log_content = self.read_file_safely(os.path.join(self.LOGS_PATH, log_file))
                    error_count += log_content.lower().count('error')

        return error_count

    def get_inbox_count(self) -> int:
        """Get count of items in Inbox folder"""
        inbox_path = "Inbox"
        if not os.path.exists(inbox_path):
            return 0

        return len(os.listdir(inbox_path))

    def get_recent_activities(self) -> List[str]:
        """Get recent activity log entries"""
        activities = []

        # Read recent entries from log files
        if os.path.exists(self.LOGS_PATH):
            for log_file in os.listdir(self.LOGS_PATH):
                if log_file.endswith('.log'):
                    log_content = self.read_file_safely(os.path.join(self.LOGS_PATH, log_file))
                    lines = log_content.strip().split('\n')

                    # Take the most recent entries
                    recent_lines = [line for line in lines if line.strip()][-self.MAX_ACTIVITY_LOG_ENTRIES:]
                    for line in recent_lines[-3:]:  # Take up to 3 recent activities
                        if line.strip():
                            # Clean up the log entry for display
                            clean_line = re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - \w+ - ', '', line)
                            if clean_line:
                                activities.append(f"- {datetime.datetime.now().strftime('%H:%M:%S')}: {clean_line}")

        # Limit to max entries
        return activities[-self.MAX_ACTIVITY_LOG_ENTRIES:]

    def get_priority_items(self) -> List[str]:
        """Get priority item indicators"""
        priorities = []

        # Check for urgent items in Needs_Action
        needs_action_path = "Needs_Action"
        if os.path.exists(needs_action_path):
            for item in os.listdir(needs_action_path):
                if any(keyword in item.lower() for keyword in ['urgent', 'invoice', 'payment']):
                    priorities.append(f"- ⚠️ High priority: {item}")

        return priorities[:5]  # Limit to 5 priority items

    def get_email_monitoring_status(self) -> SystemStatus:
        """Get email monitoring status"""
        # Check if email monitoring is running by looking at recent logs
        gmail_logs = [f for f in os.listdir(self.LOGS_PATH) if 'gmail' in f.lower()] if os.path.exists(self.LOGS_PATH) else []

        if gmail_logs:
            # Check if there are recent entries indicating activity
            latest_log = max(gmail_logs, key=lambda x: os.path.getmtime(os.path.join(self.LOGS_PATH, x))) if gmail_logs else None
            if latest_log:
                log_content = self.read_file_safely(os.path.join(self.LOGS_PATH, latest_log))
                if 'Connected' in log_content or 'Found' in log_content:
                    return SystemStatus.GREEN
                elif 'Warning' in log_content:
                    return SystemStatus.YELLOW

        return SystemStatus.RED

    def get_whatsapp_monitoring_status(self) -> SystemStatus:
        """Get WhatsApp monitoring status"""
        # Check if WhatsApp monitoring is running by looking at recent logs
        whatsapp_logs = [f for f in os.listdir(self.LOGS_PATH) if 'whatsapp' in f.lower()] if os.path.exists(self.LOGS_PATH) else []

        if whatsapp_logs:
            # Check if there are recent entries indicating activity
            latest_log = max(whatsapp_logs, key=lambda x: os.path.getmtime(os.path.join(self.LOGS_PATH, x))) if whatsapp_logs else None
            if latest_log:
                log_content = self.read_file_safely(os.path.join(self.LOGS_PATH, latest_log))
                if 'loaded successfully' in log_content or 'Found' in log_content:
                    return SystemStatus.GREEN
                elif 'Timeout' in log_content or 'Warning' in log_content:
                    return SystemStatus.YELLOW

        return SystemStatus.YELLOW  # Usually yellow as it requires manual QR scan

    def format_data_for_dashboard(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        Format collected metrics for dashboard display
        """
        formatted_data = {}

        # Format Quick Stats
        formatted_data['pending_emails'] = f"- [EMAIL] Pending emails: {metrics['pending_emails']}"
        formatted_data['unread_whatsapp'] = f"- [WHATSAPP] Unread WhatsApp: {metrics['unread_whatsapp']}"
        formatted_data['tasks_needs_action'] = f"- [TASK] Tasks in Need Action: {metrics['tasks_needs_action']}"
        formatted_data['tasks_completed'] = f"- [DONE] Tasks Completed: {metrics['tasks_completed']}"
        formatted_data['total_monitored'] = f"- [FILE] Total monitored items: {metrics['total_monitored_items']}"

        # Format System Status
        formatted_data['email_status'] = f"- {self.get_email_monitoring_status().value} Email Monitoring: {'Active' if self.get_email_monitoring_status() != SystemStatus.RED else 'Inactive'}"
        formatted_data['whatsapp_status'] = f"- {self.get_whatsapp_monitoring_status().value} WhatsApp Monitoring: {'Active' if self.get_whatsapp_monitoring_status() != SystemStatus.RED else 'Inactive'}"
        inbox_status_value = 'Empty' if metrics['inbox_count'] == 0 else f"{metrics['inbox_count']} items"
        formatted_data['inbox_status'] = f"- [INBOX] Inbox Status: {inbox_status_value}"
        workflow_percentage = max(0, min(100, int((metrics['tasks_completed'] / max(1, metrics['tasks_completed'] + metrics['tasks_needs_action'])) * 100)))
        formatted_data['workflow_progress'] = f"- [WF] Workflow Progress: {workflow_percentage}% complete"

        # Format Recent Activity Log
        formatted_data['recent_activity'] = '\n'.join(metrics['recent_activities']) if metrics['recent_activities'] else '- No recent activity'

        # Format Important Notifications
        formatted_data['important_notifications'] = '\n'.join(metrics['priority_indicators']) if metrics['priority_indicators'] else '- No urgent items'

        # Format Workflow Status
        formatted_data['workflow_status'] = f"- Inbox: {metrics['inbox_count']} items\n- Needs Action: {metrics['tasks_needs_action']} items\n- Done: {metrics['tasks_completed']} items\n- Next Action: Process {metrics['tasks_needs_action']} pending items"

        # Format System Configuration
        formatted_data['system_config'] = f"- Last System Check: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return formatted_data

    def update_dashboard_sections(self, formatted_data: Dict[str, str]):
        """
        Update appropriate dashboard sections with new data
        """
        # Read current dashboard
        with open(self.DASHBOARD_PATH, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()

        # Update Quick Stats section
        dashboard_content = self.replace_section_content(
            dashboard_content,
            r'(## 📊 Quick Stats\n)(.*?)(\n\n|$)',
            f"## 📊 Quick Stats\n{formatted_data['pending_emails']}\n{formatted_data['unread_whatsapp']}\n{formatted_data['tasks_needs_action']}\n{formatted_data['tasks_completed']}\n{formatted_data['total_monitored']}\n"
        )

        # Update System Status section
        dashboard_content = self.replace_section_content(
            dashboard_content,
            r'(## 📈 System Status\n)(.*?)(\n\n|$)',
            f"## 📈 System Status\n{formatted_data['email_status']}\n{formatted_data['whatsapp_status']}\n{formatted_data['inbox_status']}\n{formatted_data['workflow_progress']}\n"
        )

        # Update Recent Activity Log section
        dashboard_content = self.replace_section_content(
            dashboard_content,
            r'(## 📅 Recent Activity Log\n)(.*?)(\n\n|$)',
            f"## 📅 Recent Activity Log\n{formatted_data['recent_activity']}\n"
        )

        # Update Important Notifications section
        dashboard_content = self.replace_section_content(
            dashboard_content,
            r'(## ⚠️ Important Notifications\n)(.*?)(\n\n|$)',
            f"## ⚠️ Important Notifications\n{formatted_data['important_notifications']}\n"
        )

        # Update Workflow Status section
        dashboard_content = self.replace_section_content(
            dashboard_content,
            r'(## 🔄 Workflow Status\n)(.*?)(\n\n|$)',
            f"## 🔄 Workflow Status\n{formatted_data['workflow_status']}\n"
        )

        # Update System Configuration section
        dashboard_content = self.replace_section_content(
            dashboard_content,
            r'(## 🛠️ System Configuration\n)(.*?)(\n\n|$)',
            f"## 🛠️ System Configuration\n{formatted_data['system_config']}\n"
        )

        # Write updated dashboard
        with open(self.DASHBOARD_PATH, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

    def replace_section_content(self, content: str, pattern: str, replacement: str) -> str:
        """
        Replace content in a specific section using regex
        """
        import re
        return re.sub(pattern, rf'\g<1>{replacement}', content, flags=re.DOTALL)

    def preserve_historical_data(self):
        """
        Preserve historical data (for demo purposes, we'll just note that this would happen)
        """
        # In a real implementation, this would maintain historical data
        # For now, we just acknowledge the step
        pass

    def log_update_activity(self, metrics: Dict[str, Any]):
        """
        Log update activity to system logs
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"""{timestamp} - DASHBOARD_UPDATER - UPDATE - Dashboard refreshed
- Pending emails: {metrics['pending_emails']}
- Unread WhatsApp: {metrics['unread_whatsapp']}
- Tasks in Need Action: {metrics['tasks_needs_action']}
- Tasks Completed: {metrics['tasks_completed']}
- Error Count: {metrics['error_count']}
- Update successful
"""

        # Write to log file
        log_file_path = os.path.join(self.LOGS_PATH, "dashboard_updates.log")
        os.makedirs(self.LOGS_PATH, exist_ok=True)

        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry + "\n")

    def verify_update_success(self) -> bool:
        """
        Verify that dashboard update was successful
        """
        try:
            # Check if dashboard file exists and has content
            if not os.path.exists(self.DASHBOARD_PATH):
                return False

            with open(self.DASHBOARD_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic verification: check if essential sections exist
            essential_sections = ['## 📊 Quick Stats', '## 📈 System Status', '## 🔄 Workflow Status']
            return all(section in content for section in essential_sections)

        except Exception:
            return False

    def handle_dashboard_file_access_issues(self) -> bool:
        """
        Handle dashboard file access issues
        """
        try:
            # Try to create the dashboard file if it doesn't exist
            if not os.path.exists(self.DASHBOARD_PATH):
                self.initialize_dashboard_if_needed()
                return True

            # Check if we have write permissions
            with open(self.DASHBOARD_PATH, 'a', encoding='utf-8') as f:
                f.write('')  # Test write access

            return True
        except PermissionError:
            print(f"Permission denied accessing {self.DASHBOARD_PATH}")
            return False
        except Exception as e:
            print(f"Error accessing dashboard file: {e}")
            return False

    def manage_update_conflicts(self) -> bool:
        """
        Manage update conflicts (for demo, we'll just return True)
        """
        # In a real implementation, this would handle concurrent updates
        return True

    def retry_failed_updates(self, max_retries: int = 3) -> bool:
        """
        Retry failed updates
        """
        for attempt in range(max_retries):
            try:
                self.update_dashboard()
                if self.verify_update_success():
                    return True
            except Exception as e:
                print(f"Update attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry

        return False

    def maintain_backup_statistics(self):
        """
        Maintain backup of previous dashboard state
        """
        backup_path = f"{self.DASHBOARD_PATH}.backup"
        if os.path.exists(self.DASHBOARD_PATH):
            with open(self.DASHBOARD_PATH, 'r', encoding='utf-8') as original:
                content = original.read()

            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(content)

    def count_lines_in_file(self, file_path: str) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except Exception:
            return 0

    def read_file_safely(self, file_path: str) -> str:
        """Safely read a file, returning empty string if error"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def update_dashboard(self) -> Dict[str, Any]:
        """
        Main method to update the dashboard following the update process
        """
        try:
            # Step 1: Collect current system metrics
            metrics = self.collect_system_metrics()

            # Step 2: Format data for dashboard display
            formatted_data = self.format_data_for_dashboard(metrics)

            # Step 3: Update appropriate dashboard sections
            self.update_dashboard_sections(formatted_data)

            # Step 4: Preserve historical data
            self.preserve_historical_data()

            # Step 5: Log update activity
            self.log_update_activity(metrics)

            # Step 6: Verify update success
            success = self.verify_update_success()

            result = {
                'success': success,
                'metrics_collected': metrics,
                'update_time': datetime.datetime.now().isoformat(),
                'message': 'Dashboard updated successfully' if success else 'Dashboard update failed verification'
            }

            return result

        except Exception as e:
            # Handle errors according to error handling section
            error_result = {
                'success': False,
                'error': str(e),
                'message': 'Dashboard update failed due to error'
            }

            # Log the error
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_log = f"{timestamp} - DASHBOARD_UPDATER - ERROR - {str(e)}\n"
            error_log_path = os.path.join(self.LOGS_PATH, "dashboard_errors.log")

            try:
                with open(error_log_path, 'a', encoding='utf-8') as f:
                    f.write(error_log)
            except:
                pass  # Can't log the error if we can't write to the log file

            return error_result

    def update_triggered_by_event(self, event_type: str) -> Dict[str, Any]:
        """
        Handle updates triggered by specific events
        """
        return self.update_dashboard()


# Example usage:
if __name__ == "__main__":
    # Initialize the dashboard updater
    updater = DashboardUpdater()

    # Update the dashboard
    result = updater.update_dashboard()

    print("Dashboard Update Result:")
    print(json.dumps(result, indent=2, default=str))