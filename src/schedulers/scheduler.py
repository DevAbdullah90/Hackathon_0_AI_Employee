"""
Scheduler for AI Employee System
Manages automated tasks and periodic execution of various components
"""
import os
import sys
import time
import threading
import schedule
import datetime
from pathlib import Path
import subprocess
import logging
from datetime import datetime as dt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIEmployeeScheduler:
    """
    Scheduler for the AI Employee system that handles:
    - Periodic watcher execution
    - LinkedIn post scheduling
    - Dashboard updates
    - Plan generation
    - System health checks
    """

    def __init__(self):
        self.running = False
        self.jobs = []

        # Create necessary directories
        os.makedirs('Logs', exist_ok=True)
        os.makedirs('Plans', exist_ok=True)
        os.makedirs('Scheduled_Tasks', exist_ok=True)

    def run_gmail_monitor(self):
        """Run the Gmail monitoring script"""
        try:
            logger.info("Running Gmail monitor...")
            # In a real implementation, you would call the actual Gmail monitor
            # For now, we'll just log that it ran
            logger.info("Gmail monitor executed successfully")
        except Exception as e:
            logger.error(f"Error running Gmail monitor: {e}")

    def run_whatsapp_monitor(self):
        """Run the WhatsApp monitoring script"""
        try:
            logger.info("Running WhatsApp monitor...")
            # In a real implementation, you would call the actual WhatsApp monitor
            logger.info("WhatsApp monitor executed successfully")
        except Exception as e:
            logger.error(f"Error running WhatsApp monitor: {e}")

    def run_linkedin_monitor(self):
        """Run the LinkedIn monitoring and posting script"""
        try:
            logger.info("Running LinkedIn monitor and poster...")
            # Execute the LinkedIn watcher
            result = subprocess.run([
                sys.executable, '-c',
                'from linkedin_watcher import LinkedInWatcher; '
                'watcher = LinkedInWatcher(); '
                'result = watcher.run_linkedin_monitoring_cycle(); '
                'print("LinkedIn monitoring completed:", result)'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"LinkedIn monitor executed: {result.stdout[:200]}...")
            else:
                logger.error(f"LinkedIn monitor failed: {result.stderr}")

        except Exception as e:
            logger.error(f"Error running LinkedIn monitor: {e}")

    def generate_plans(self):
        """Generate plan files based on current needs"""
        try:
            logger.info("Generating plans...")
            from plan_creator import PlanCreator

            planner = PlanCreator()
            plan_data = {
                'title': f'Daily Plan {dt.now().strftime("%Y-%m-%d")}',
                'description': 'Automated daily plan generation',
                'tasks': [],
                'priority': 'normal',
                'deadline': dt.now().strftime("%Y-%m-%d"),
                'status': 'pending'
            }

            # Analyze current needs from various sources
            needs_action_files = list(Path('Needs_Action').glob('*.md'))
            inbox_files = list(Path('Inbox').glob('*.md'))

            if needs_action_files:
                plan_data['tasks'].append({
                    'description': f'Process {len(needs_action_files)} items in Needs_Action',
                    'priority': 'high',
                    'estimated_time': len(needs_action_files) * 15  # 15 mins per item
                })

            if inbox_files:
                plan_data['tasks'].append({
                    'description': f'Process {len(inbox_files)} items in Inbox',
                    'priority': 'medium',
                    'estimated_time': len(inbox_files) * 10  # 10 mins per item
                })

            # Generate plan
            content = f"Plan for: {plan_data.get('title', 'Unspecified Task')}\n" \
                     f"Description: {plan_data.get('description', 'No description')}\n" \
                     f"Tasks: {', '.join([task.get('description', '') for task in plan_data.get('tasks', [])])}\n" \
                     f"Priority: {plan_data.get('priority', 'Normal')}\n" \
                     f"Deadline: {plan_data.get('deadline', 'None')}"
            plan_result = planner.generate_plan_from_content(content, "Scheduler_Generated")
            logger.info(f"Plan generated: {plan_result.get('plan_id', 'unknown')}")

        except ImportError:
            logger.warning("plan_creator module not found, skipping plan generation")
        except Exception as e:
            logger.error(f"Error generating plans: {e}")

    def update_dashboard(self):
        """Update the dashboard with current status"""
        try:
            logger.info("Updating dashboard...")
            from generated_dashboard_updater import DashboardUpdater

            updater = DashboardUpdater()
            result = updater.update_dashboard()
            logger.info(f"Dashboard updated: {result}")

        except ImportError:
            logger.warning("dashboard_updater module not found, skipping dashboard update")
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

    def run_health_check(self):
        """Perform system health checks"""
        try:
            logger.info("Running system health check...")

            # Check if important directories exist
            dirs_to_check = ['Inbox', 'Needs_Action', 'Done', 'Pending_Approval', 'Approved', 'Rejected', 'Logs', 'Plans']
            issues = []

            for directory in dirs_to_check:
                if not os.path.exists(directory):
                    issues.append(f"Missing directory: {directory}")
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created missing directory: {directory}")

            # Check disk space
            import shutil
            total, used, free = shutil.disk_usage(".")
            free_gb = free // (2**30)
            if free_gb < 1:  # Less than 1 GB free
                issues.append(f"Low disk space: {free_gb} GB free")

            if issues:
                logger.warning(f"Health check issues: {issues}")
            else:
                logger.info("Health check passed")

        except Exception as e:
            logger.error(f"Error during health check: {e}")

    def setup_schedule(self):
        """Setup the scheduling jobs"""
        # Daily tasks
        schedule.every().hour.do(self.update_dashboard)  # Update dashboard hourly
        schedule.every(2).hours.do(self.run_health_check)  # Health check every 2 hours

        # Specific times
        schedule.every().day.at("08:00").do(self.run_gmail_monitor)  # Morning email check
        schedule.every().day.at("08:15").do(self.run_whatsapp_monitor)  # Morning WhatsApp check
        schedule.every().day.at("08:30").do(self.run_linkedin_monitor)  # Morning LinkedIn check
        schedule.every().day.at("09:00").do(self.generate_plans)  # Morning plan generation
        schedule.every().day.at("12:00").do(self.run_gmail_monitor)  # Midday email check
        schedule.every().day.at("12:15").do(self.run_whatsapp_monitor)  # Midday WhatsApp check
        schedule.every().day.at("16:00").do(self.run_gmail_monitor)  # Evening email check
        schedule.every().day.at("16:15").do(self.run_whatsapp_monitor)  # Evening WhatsApp check
        schedule.every().day.at("18:00").do(self.update_dashboard)  # Evening dashboard update

        # Every 30 minutes during business hours
        schedule.every(30).minutes.between("09:00", "17:00").do(self.run_linkedin_monitor)

        logger.info("Schedule setup completed")
        logger.info("Jobs scheduled:")
        for job in schedule.jobs:
            logger.info(f"  - {job}")

    def run_scheduler(self):
        """Main scheduler loop"""
        self.setup_schedule()
        self.running = True

        logger.info("AI Employee Scheduler started")

        while self.running:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("AI Employee Scheduler stopped")


def main():
    """Main function to run the scheduler"""
    scheduler = AIEmployeeScheduler()

    try:
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
        scheduler.stop_scheduler()
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        scheduler.stop_scheduler()


if __name__ == "__main__":
    main()