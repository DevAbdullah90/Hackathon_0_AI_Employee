#!/usr/bin/env python3
"""
Smart Scheduler - Automated Task Orchestration System
Runs periodic tasks automatically without human intervention
"""

import os
import sys
import time
import signal
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

try:
    import schedule
except ImportError:
    print("Installing schedule...")
    os.system("pip install schedule")
    import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SmartScheduler:
    """Intelligent scheduler for AI Employee tasks"""

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path(os.getcwd())
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(exist_ok=True)

        # Schedule configuration
        self.config = {
            'needs_action_check': {
                'interval_hours': 1,
                'description': 'Check Needs_Action and create plans'
            },
            'linkedin_watch': {
                'interval_hours': 6,
                'description': 'Run LinkedIn watcher for opportunities'
            },
            'daily_briefing': {
                'time': '08:00',
                'description': 'Generate daily briefing'
            },
            'weekly_report': {
                'day': 'sunday',
                'time': '22:00',
                'description': 'Generate CEO weekly report'
            },
            'twitter_watch': {
                'interval_hours': 3,
                'description': 'Check Twitter mentions and DMs'
            },
            'whatsapp_watch': {
                'interval_hours': 2,
                'description': 'Check WhatsApp for business opportunities'
            },
            'email_watch': {
                'interval_hours': 1,
                'description': 'Check email for business opportunities'
            },
            'daily_whatsapp_update': {
                'time': '09:00',
                'description': 'Send daily business update via WhatsApp'
            }
        }

        logger.info("Smart Scheduler initialized")
        self.log_system_startup()

    def log_system_startup(self):
        """Log scheduler startup"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'scheduler_started',
            'config': self.config
        }
        self._write_log(log_entry)

    def log_task_execution(self, task_name: str, status: str, details: Dict[str, Any] = None):
        """Log task execution"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'task_execution',
            'task_name': task_name,
            'status': status,
            'details': details or {}
        }
        self._write_log(log_entry)

    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to JSONL file"""
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = self.logs_folder / f"scheduler_{timestamp}.jsonl"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')

    def check_needs_action(self):
        """Check Needs_Action folder and create plans"""
        logger.info("[TASK] Checking Needs_Action folder...")

        try:
            needs_action = self.vault_path / 'Needs_Action'

            if not needs_action.exists():
                logger.info("  No Needs_Action folder found")
                return

            files = list(needs_action.glob("*.md"))

            if not files:
                logger.info("  No files in Needs_Action to process")
                return

            logger.info(f"  Found {len(files)} files to process")

            # Run plan_creator.py if it exists
            plan_script = self.vault_path / 'src' / 'core' / 'plan_creator.py'
            if plan_script.exists():
                logger.info("  Running plan_creator.py...")
                result = subprocess.run(
                    ['python', str(plan_script)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    logger.info("  [SUCCESS] Plans created successfully")
                    self.log_task_execution(
                        'check_needs_action',
                        'success',
                        {'files_processed': len(files)}
                    )
                else:
                    logger.error(f"  [FAILED] Plan creation failed: {result.stderr}")
                    self.log_task_execution(
                        'check_needs_action',
                        'failed',
                        {'error': result.stderr}
                    )
            else:
                logger.warning("  plan_creator.py not found")

        except Exception as e:
            logger.error(f"  [ERROR] Error in check_needs_action: {e}", exc_info=True)
            self.log_task_execution(
                'check_needs_action',
                'failed',
                {'error': str(e)}
            )

    def run_linkedin_watcher(self):
        """Run LinkedIn watcher for opportunities"""
        logger.info("[TASK] Running LinkedIn watcher...")

        try:
            watcher_script = self.vault_path / 'src' / 'platforms' / 'linkedin' / 'linkedin_watcher.py'

            if watcher_script.exists():
                result = subprocess.run(
                    ['python', str(watcher_script), '--once'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    logger.info("  [SUCCESS] LinkedIn watcher completed")
                    self.log_task_execution('linkedin_watcher', 'success')
                else:
                    logger.error(f"  [FAILED] LinkedIn watcher failed: {result.stderr}")
                    self.log_task_execution('linkedin_watcher', 'failed', {'error': result.stderr})
            else:
                logger.warning("  linkedin_watcher.py not found")

        except Exception as e:
            logger.error(f"  [ERROR] Error in linkedin_watcher: {e}", exc_info=True)
            self.log_task_execution('linkedin_watcher', 'failed', {'error': str(e)})


    def run_twitter_watcher(self):
        """Run Twitter watcher for mentions and DMs"""
        logger.info("[TASK] Running Twitter watcher...")

        try:
            watcher_script = self.vault_path / 'src' / 'platforms' / 'twitter' / 'watcher.py'

            if watcher_script.exists():
                result = subprocess.run(
                    ['python', str(watcher_script), '--once'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    logger.info("  [SUCCESS] Twitter watcher completed")
                    self.log_task_execution('twitter_watcher', 'success')
                else:
                    logger.error(f"  [FAILED] Twitter watcher failed: {result.stderr}")
                    self.log_task_execution('twitter_watcher', 'failed', {'error': result.stderr})
            else:
                logger.warning("  twitter/watcher.py not found")

        except Exception as e:
            logger.error(f"  [ERROR] Error in twitter_watcher: {e}", exc_info=True)
            self.log_task_execution('twitter_watcher', 'failed', {'error': str(e)})

    def generate_daily_briefing(self):
        """Generate daily briefing"""
        logger.info("[TASK] Generating daily briefing...")

        try:
            # This would call ceo_briefing_generator with daily parameters
            # For now, log that it ran
            briefing_script = self.vault_path / 'src' / 'generators' / 'ceo_briefing_generator.py'

            if briefing_script.exists():
                result = subprocess.run(
                    ['python', str(briefing_script), 'generate_and_save'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    logger.info("  [SUCCESS] Daily briefing generated")
                    self.log_task_execution('daily_briefing', 'success')
                else:
                    logger.error(f"  [FAILED] Daily briefing failed: {result.stderr}")
                    self.log_task_execution('daily_briefing', 'failed', {'error': result.stderr})
            else:
                logger.warning("  ceo_briefing_generator.py not found")

        except Exception as e:
            logger.error(f"  [ERROR] Error in daily_briefing: {e}", exc_info=True)
            self.log_task_execution('daily_briefing', 'failed', {'error': str(e)})

    def generate_weekly_report(self):
        """Generate CEO weekly report"""
        logger.info("[TASK] Generating CEO weekly report...")

        try:
            report_script = self.vault_path / 'src' / 'generators' / 'ceo_briefing_generator.py'

            if report_script.exists():
                # Weekly report is same as daily but with 7-day range
                result = subprocess.run(
                    ['python', str(report_script), 'generate_and_save'],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes for weekly report
                )

                if result.returncode == 0:
                    logger.info("  [SUCCESS] Weekly CEO report generated")
                    self.log_task_execution('weekly_report', 'success')
                else:
                    logger.error(f"  [FAILED] Weekly report failed: {result.stderr}")
                    self.log_task_execution('weekly_report', 'failed', {'error': result.stderr})
            else:
                logger.warning("  ceo_briefing_generator.py not found")

        except Exception as e:
            logger.error(f"  [ERROR] Error in weekly_report: {e}", exc_info=True)
            self.log_task_execution('weekly_report', 'failed', {'error': str(e)})

    def run_whatsapp_watcher(self):
        """Run WhatsApp watcher for business opportunities"""
        logger.info("[TASK] Running WhatsApp watcher...")

        try:
            watcher_script = self.vault_path / 'src' / 'platforms' / 'whatsapp' / 'whatsapp_watcher.py'

            if watcher_script.exists():
                result = subprocess.run(
                    ['python', str(watcher_script), '--once'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    logger.info("  [SUCCESS] WhatsApp watcher completed")
                    self.log_task_execution('whatsapp_watcher', 'success')
                else:
                    logger.error(f"  [FAILED] WhatsApp watcher failed: {result.stderr}")
                    self.log_task_execution('whatsapp_watcher', 'failed', {'error': result.stderr})
            else:
                logger.warning("  whatsapp_watcher.py not found")

        except Exception as e:
            logger.error(f"  [ERROR] Error in whatsapp_watcher: {e}", exc_info=True)
            self.log_task_execution('whatsapp_watcher', 'failed', {'error': str(e)})

    def run_email_watcher(self):
        """Run Email watcher for business opportunities"""
        logger.info("[TASK] Running Email watcher...")

        try:
            watcher_script = self.vault_path / 'src' / 'platforms' / 'email' / 'email_watcher.py'

            if watcher_script.exists():
                result = subprocess.run(
                    ['python', str(watcher_script), '--once'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    logger.info("  [SUCCESS] Email watcher completed")
                    self.log_task_execution('email_watcher', 'success')
                else:
                    logger.error(f"  [FAILED] Email watcher failed: {result.stderr}")
                    self.log_task_execution('email_watcher', 'failed', {'error': result.stderr})
            else:
                logger.warning("  email_watcher.py not found")

        except Exception as e:
            logger.error(f"  [ERROR] Error in email_watcher: {e}", exc_info=True)
            self.log_task_execution('email_watcher', 'failed', {'error': str(e)})

    def run_daily_whatsapp_update(self):
        """Run daily WhatsApp update script"""
        logger.info("[TASK] Running daily WhatsApp update...")
        
        try:
            update_script = self.vault_path / 'src' / 'platforms' / 'whatsapp' / 'daily_whatsapp_update.py'
            
            if update_script.exists():
                result = subprocess.run(
                    ['python', str(update_script)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    logger.info("  [SUCCESS] Daily WhatsApp update completed")
                    self.log_task_execution('daily_whatsapp_update', 'success')
                else:
                    logger.error(f"  [FAILED] Daily WhatsApp update failed: {result.stderr}")
                    self.log_task_execution('daily_whatsapp_update', 'failed', {'error': result.stderr})
            else:
                logger.warning("  daily_whatsapp_update.py not found")
                
        except Exception as e:
            logger.error(f"  [ERROR] Error in daily_whatsapp_update: {e}", exc_info=True)
            self.log_task_execution('daily_whatsapp_update', 'failed', {'error': str(e)})

    def run_instagram_watcher(self):
        """Run Instagram watcher/check notifications"""
        logger.info("[TASK] Running Instagram watcher...")
        
        try:
            # We use the main instagram_playwright.py script with 'notifications' arg
            ig_script = self.vault_path / 'src' / 'platforms' / 'instagram' / 'instagram_playwright.py'
            
            if ig_script.exists():
                result = subprocess.run(
                    ['python', str(ig_script), 'notifications'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    logger.info("  [SUCCESS] Instagram watcher completed")
                    # Optionally log the JSON output
                    try:
                        output_json = json.loads(result.stdout)
                        count = output_json.get('count', 0)
                        logger.info(f"    Found {count} notifications")
                    except:
                        pass
                        
                    self.log_task_execution('instagram_watcher', 'success')
                else:
                    logger.error(f"  [FAILED] Instagram watcher failed: {result.stderr}")
                    self.log_task_execution('instagram_watcher', 'failed', {'error': result.stderr})
            else:
                logger.warning("  instagram_playwright.py not found")
                
        except Exception as e:
            logger.error(f"  [ERROR] Error in instagram_watcher: {e}", exc_info=True)
            self.log_task_execution('instagram_watcher', 'failed', {'error': str(e)})

    def run_facebook_check(self):
        """Run Facebook login check (as watcher)"""
        logger.info("[TASK] Running Facebook check...")
        
        try:
            poster_script = self.vault_path / 'src' / 'platforms' / 'facebook' / 'facebook_poster.py'
            
            if poster_script.exists():
                # Run with 'login' action to verify auth
                result = subprocess.run(
                    ['python', str(poster_script), 'login'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    logger.info("  [SUCCESS] Facebook check completed")
                    self.log_task_execution('facebook_check', 'success')
                else:
                    logger.error(f"  [FAILED] Facebook check failed: {result.stderr}")
                    self.log_task_execution('facebook_check', 'failed', {'error': result.stderr})
            else:
                logger.warning("  facebook_poster.py not found")
                
        except Exception as e:
            logger.error(f"  [ERROR] Error in facebook_check: {e}", exc_info=True)
            self.log_task_execution('facebook_check', 'failed', {'error': str(e)})

    def setup_schedules(self):
        """Set up all scheduled tasks"""
        logger.info("Setting up scheduled tasks...")

        # --- SPECIAL TEST SCHEDULE FOR 01:10 ---
        test_time = "01:10"

        # LinkedIn Check
        schedule.every().day.at(test_time).do(self.run_linkedin_watcher)
        logger.info(f"  [TEST] Scheduled: LinkedIn watcher at {test_time}")

        # Facebook Check
        schedule.every().day.at(test_time).do(self.run_facebook_check)
        logger.info(f"  [TEST] Scheduled: Facebook check at {test_time}")

        # WhatsApp Check
        schedule.every().day.at(test_time).do(self.run_whatsapp_watcher)
        logger.info(f"  [TEST] Scheduled: WhatsApp watcher at {test_time}")

        # Email Check
        schedule.every().day.at(test_time).do(self.run_email_watcher)
        logger.info(f"  [TEST] Scheduled: Email watcher at {test_time}")
        
        # ----------------------------------------

        # Every hour: Check Needs_Action
        schedule.every(self.config['needs_action_check']['interval_hours']).hours.do(
            self.check_needs_action
        )
        logger.info("  [OK] Scheduled: Check Needs_Action (every hour)")

        # Daily 9 AM: WhatsApp update
        schedule.every().day.at(self.config['daily_whatsapp_update']['time']).do(
            self.run_daily_whatsapp_update
        )
        logger.info(f"  [OK] Scheduled: Daily WhatsApp update (daily at {self.config['daily_whatsapp_update']['time']})")

    def run_pending(self):
        """Run any pending scheduled tasks"""
        schedule.run_pending()

    def run_continuous(self):
        """Run scheduler continuously"""
        logger.info("=" * 60)
        logger.info("SMART SCHEDULER - Starting Automated Task Orchestration")
        logger.info("=" * 60)

        # Set up all schedules
        self.setup_schedules()

        # Run once on startup
        logger.info("\nRunning initial task check...")
        self.check_needs_action()

        # Set up graceful shutdown
        def signal_handler(sig, frame):
            logger.info("\n[STOP] Shutting down Smart Scheduler...")
            logger.info("[OK] Smart Scheduler stopped gracefully")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("\n[SCHEDULER] Running. Tasks will execute at scheduled times.")
        logger.info("Press Ctrl+C to stop\n")

        try:
            while True:
                self.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Smart Scheduler')
    parser.add_argument('vault_path', nargs='?', help='Path to vault', default=None)
    args = parser.parse_args()

    scheduler = SmartScheduler(args.vault_path)
    scheduler.run_continuous()


if __name__ == "__main__":
    main()
