#!/usr/bin/env python3
"""
Workflow Orchestrator - Complete AI Employee System Integration
Master coordinator that runs all components together
"""

import os
import sys
import time
import signal
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import threading

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
        logging.FileHandler('Logs/orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Master orchestrator for the complete AI Employee system"""

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path(os.getcwd())
        logger.info(f"Initialized with vault path: {self.vault_path}")

        # Ensure directories exist
        self._setup_directories()

        # Component status tracking
        self.component_status = {
            'auto_processor': False,
            'smart_scheduler': False,
            'reddit_watcher': False,
            'twitter_watcher': False,
            'linkedin_watcher': False,
            'whatsapp_watcher': False,
            'email_watcher': False,
            'content_generator': False,
            'ceo_briefing': False
        }

        # Thread tracking
        self.threads = {}

        logger.info("=" * 70)
        logger.info("AI EMPLOYEE WORKFLOW ORCHESTRATOR - MASTER COORDINATOR")
        logger.info("=" * 70)
        logger.info("Initializing complete automation system...")

    def _setup_directories(self):
        """Set up required directory structure"""
        directories = [
            'Approved',
            'Pending_Approval',
            'Done',
            'Needs_Action',
            'Logs',
            'Plans',
            'Reddit_Data',
            'Reddit_Posts',
            'LinkedIn_Posts',
            'Reports'
        ]

        for dir_name in directories:
            (self.vault_path / dir_name).mkdir(exist_ok=True)

        logger.info("[OK] Directory structure verified")

    def start_auto_processor(self):
        """Start the auto processor in a separate thread"""
        def run_processor():
            try:
                processor_script = self.vault_path / 'src' / 'core' / 'auto_processor.py'
                if processor_script.exists():
                    logger.info("[OK] Starting Auto Processor...")
                    subprocess.run(
                        ['python', str(processor_script)],
                        check=True,
                        cwd=str(self.vault_path)
                    )
                else:
                    logger.error("[FAIL] auto_processor.py not found!")
            except Exception as e:
                logger.error(f"[FAIL] Auto processor failed: {e}", exc_info=True)

        thread = threading.Thread(target=run_processor, daemon=True)
        thread.start()
        self.threads['auto_processor'] = thread
        self.component_status['auto_processor'] = True
        logger.info("[OK] Auto Processor started in background thread")

    def start_smart_scheduler(self):
        """Start the smart scheduler in a separate thread"""
        def run_scheduler():
            try:
                scheduler_script = self.vault_path / 'src' / 'schedulers' / 'smart_scheduler.py'
                if scheduler_script.exists():
                    logger.info("[OK] Starting Smart Scheduler...")
                    subprocess.run(
                        ['python', str(scheduler_script), str(self.vault_path)],
                        check=True,
                        cwd=str(self.vault_path)
                    )
                else:
                    logger.error("[FAIL] smart_scheduler.py not found!")
            except Exception as e:
                logger.error(f"[FAIL] Smart scheduler failed: {e}", exc_info=True)

        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        self.threads['smart_scheduler'] = thread
        self.component_status['smart_scheduler'] = True
        logger.info("[OK] Smart Scheduler started in background thread")

    def start_whatsapp_watcher(self):
        """Start the WhatsApp watcher in a separate thread"""
        def run_watcher():
            try:
                watcher_script = self.vault_path / 'src' / 'platforms' / 'whatsapp' / 'whatsapp_watcher.py'
                if watcher_script.exists():
                    logger.info("[OK] Starting WhatsApp Watcher...")
                    subprocess.run(
                        ['python', str(watcher_script)],
                        check=True,
                        cwd=str(self.vault_path)
                    )
                else:
                    logger.error("[FAIL] whatsapp_watcher.py not found!")
            except Exception as e:
                logger.error(f"[FAIL] WhatsApp watcher failed: {e}", exc_info=True)

        thread = threading.Thread(target=run_watcher, daemon=True)
        thread.start()
        self.threads['whatsapp_watcher'] = thread
        self.component_status['whatsapp_watcher'] = True
        logger.info("[OK] WhatsApp Watcher started in background thread")

    def start_email_watcher(self):
        """Start the Email watcher in a separate thread"""
        def run_watcher():
            try:
                watcher_script = self.vault_path / 'src' / 'platforms' / 'email' / 'email_watcher.py'
                if watcher_script.exists():
                    logger.info("[OK] Starting Email Watcher...")
                    subprocess.run(
                        ['python', str(watcher_script), '--vault', str(self.vault_path)],
                        check=True,
                        cwd=str(self.vault_path)
                    )
                else:
                    logger.error("[FAIL] email_watcher.py not found!")
            except Exception as e:
                logger.error(f"[FAIL] Email watcher failed: {e}", exc_info=True)

        thread = threading.Thread(target=run_watcher, daemon=True)
        thread.start()
        self.threads['email_watcher'] = thread
        self.component_status['email_watcher'] = True
        logger.info("[OK] Email Watcher started in background thread")

    def start_periodic_watchers(self):
        """Start periodic watcher checks using schedule library"""
        logger.info("[INFO] Setting up periodic watcher schedules...")

        # Twitter watcher every 3 hours
        def twitter_check():
            logger.info("[SCHEDULE] Running Twitter watcher check...")
            try:
                result = subprocess.run(
                    ['python', 'src/platforms/twitter/watcher.py', '--once'],
                    capture_output=True,
                    text=True,
                    cwd=str(self.vault_path),
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("[OK] Twitter watcher completed")
                else:
                    logger.error(f"[FAIL] Twitter watcher error: {result.stderr}")
            except Exception as e:
                logger.error(f"[FAIL] Twitter watcher exception: {e}")

        schedule.every(3).hours.do(twitter_check)
        logger.info("[OK] Twitter watcher: Every 3 hours")

        # LinkedIn watcher every 6 hours
        def linkedin_check():
            logger.info("[SCHEDULE] Running LinkedIn watcher check...")
            try:
                result = subprocess.run(
                    ['python', 'src/platforms/linkedin/linkedin_watcher.py', '--once'],
                    capture_output=True,
                    text=True,
                    cwd=str(self.vault_path),
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("[OK] LinkedIn watcher completed")
                else:
                    logger.error(f"[FAIL] LinkedIn watcher error: {result.stderr}")
            except Exception as e:
                logger.error(f"[FAIL] LinkedIn watcher exception: {e}")

        schedule.every(6).hours.do(linkedin_check)
        logger.info("[OK] LinkedIn watcher: Every 6 hours")

        # Content generation daily at 9 AM
        def content_generation():
            logger.info("[SCHEDULE] Running content generation...")
            try:
                result = subprocess.run(
                    ['python', 'src/platforms/reddit/reddit_content_generator.py', '--type', 'batch', '--count', '3'],
                    capture_output=True,
                    text=True,
                    cwd=str(self.vault_path),
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("[OK] Content generation completed")
                else:
                    logger.error(f"[FAIL] Content generation error: {result.stderr}")
            except Exception as e:
                logger.error(f"[FAIL] Content generation exception: {e}")

        # WhatsApp watcher every 2 hours
        def whatsapp_check():
            logger.info("[SCHEDULE] Running WhatsApp watcher check...")
            try:
                result = subprocess.run(
                    ['python', 'src/platforms/whatsapp/whatsapp_watcher.py', '--once'],
                    capture_output=True,
                    text=True,
                    cwd=str(self.vault_path),
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("[OK] WhatsApp watcher completed")
                else:
                    logger.error(f"[FAIL] WhatsApp watcher error: {result.stderr}")
            except Exception as e:
                logger.error(f"[FAIL] WhatsApp watcher exception: {e}")

        schedule.every(2).hours.do(whatsapp_check)
        logger.info("[OK] WhatsApp watcher: Every 2 hours")

        # Email watcher every 1 hour
        def email_check():
            logger.info("[SCHEDULE] Running Email watcher check...")
            try:
                result = subprocess.run(
                    ['python', 'src/platforms/email/email_watcher.py', '--once'],
                    capture_output=True,
                    text=True,
                    cwd=str(self.vault_path),
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("[OK] Email watcher completed")
                else:
                    logger.error(f"[FAIL] Email watcher error: {result.stderr}")
            except Exception as e:
                logger.error(f"[FAIL] Email watcher exception: {e}")

        schedule.every().hour.do(email_check)
        logger.info("[OK] Email watcher: Every hour")

        schedule.every().day.at("09:00").do(content_generation)
        logger.info("[OK] Content generation: Daily at 9:00 AM")

    def run_health_check(self):
        """Run system health check"""
        logger.info("[HEALTH CHECK] Running system diagnostics...")

        health_report = {
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }

        # Check if critical directories exist
        critical_dirs = ['Approved', 'Pending_Approval', 'Done', 'Needs_Action', 'Logs']
        for dir_name in critical_dirs:
            dir_path = self.vault_path / dir_name
            health_report['components'][dir_name] = {
                'exists': dir_path.exists(),
                'writable': dir_path.exists() and os.access(dir_path, os.W_OK)
            }

        # Check Python scripts
        critical_scripts = [
            'src/core/auto_processor.py',
            'src/schedulers/smart_scheduler.py',
            'src/core/workflow_orchestrator.py',
            'src/generators/ceo_briefing_generator.py'
        ]

        for script in critical_scripts:
            script_path = self.vault_path / script
            health_report['components'][script] = {
                'exists': script_path.exists(),
                'size': script_path.stat().st_size if script_path.exists() else 0
            }

        # Log the health report
        health_file = self.vault_path / 'Logs' / f"health_{datetime.now().strftime('%Y%m%d')}.json"
        health_file.write_text(json.dumps(health_report, indent=2))

        logger.info("[OK] Health check completed and logged")
        logger.info(f"  Critical directories: {sum(1 for d in critical_dirs if health_report['components'][d]['exists'])}/{len(critical_dirs)}")
        logger.info(f"  Critical scripts: {sum(1 for s in critical_scripts if health_report['components'][s]['exists'])}/{len(critical_scripts)}")

    def generate_system_status(self):
        """Generate current system status report"""
        logger.info("[STATUS] Generating system status...")

        status = {
            'timestamp': datetime.now().isoformat(),
            'uptime': 'Running since ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'components': self.component_status.copy(),
            'active_threads': len(self.threads),
            'scheduled_tasks': len(schedule.jobs),
            'next_run_times': []
        }

        # Get next run times for scheduled tasks
        for job in schedule.jobs:
            status['next_run_times'].append({
                'job': str(job),
                'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else 'N/A'
            })

        # Count files in key directories
        for folder_name in ['Needs_Action', 'Pending_Approval', 'Approved', 'Done']:
            folder = self.vault_path / folder_name
            if folder.exists():
                count = len(list(folder.glob("*.md")))
                status[f'{folder_name.lower()}_count'] = count

        # Save status report
        status_file = self.vault_path / 'Logs' / f"status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        status_file.write_text(json.dumps(status, indent=2))

        logger.info(f"[OK] Status report saved: {status_file.name}")

        return status

    def run_continuous(self):
        """Run the complete orchestration system"""
        logger.info("Starting AI Employee Automation System...")

        # Print ASCII banner (ASCII-safe for Windows console)
        print("\n" + "=" * 70)
        print("""
    RRRRR   EEEEE   AAAAA   DDDD    Y   Y
    R   R   E       A   A   D   D    Y Y
    RRRRR   EEEE    AAAAA   D   D     Y
    R  R    E       A   A   D   D     Y
    R   R   EEEEE   A   A   DDDD      Y
        AI Employee - Gold Tier Extended
        """
        )
        print("=" * 70 + "\n")

        # Start all components
        logger.info("Starting system components...")

        self.start_auto_processor()
        time.sleep(2)  # Give processor time to start

        self.start_smart_scheduler()
        time.sleep(2)  # Give scheduler time to start

        self.start_periodic_watchers()

        # Start WhatsApp and Email watchers
        self.start_whatsapp_watcher()
        time.sleep(2)  # Give WhatsApp watcher time to start

        self.start_email_watcher()
        time.sleep(2)  # Give Email watcher time to start

        # Run initial health check
        self.run_health_check()

        # Generate initial status
        status = self.generate_system_status()

        logger.info("\n" + "=" * 70)
        logger.info("[OK] ALL SYSTEMS OPERATIONAL")
        logger.info("=" * 70)
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Auto Processor: {'Running' if self.component_status['auto_processor'] else 'Failed'}")
        logger.info(f"Smart Scheduler: {'Running' if self.component_status['smart_scheduler'] else 'Failed'}")
        logger.info(f"(WhatsApp) WhatsApp Watcher: {'Running' if self.component_status['whatsapp_watcher'] else 'Failed'}")
        logger.info(f"(Email) Email Watcher: {'Running' if self.component_status['email_watcher'] else 'Failed'}")
        logger.info(f"Active Threads: {len(self.threads)}")
        logger.info(f"Scheduled Tasks: {len(schedule.jobs)}")

        # Setup graceful shutdown
        def signal_handler(sig, frame):
            logger.info("\n[STOP] Shutting down AI Employee System...")
            logger.info("This may take a few seconds...")

            # Generate final status
            final_status = self.generate_system_status()

            logger.info(f"[OK] System stopped. Final status logged.")
            logger.info("=" * 70)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("\n[INFO] Press Ctrl+C to stop the system gracefully")
        logger.info("[CLOCK]  System will run continuously, executing tasks at scheduled times")
        logger.info("=" * 70 + "\n")

        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

                # Periodic status generation (every hour)
                if datetime.now().minute == 0:
                    self.generate_system_status()

        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
        except Exception as e:
            logger.error(f"[CRITICAL] CRITICAL ERROR: {e}", exc_info=True)
            logger.info("System will attempt to continue running...")


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='AI Employee Workflow Orchestrator')
    parser.add_argument('vault_path', nargs='?', help='Path to the vault directory')
    args = parser.parse_args()

    orchestrator = WorkflowOrchestrator(args.vault_path)
    orchestrator.run_continuous()


if __name__ == "__main__":
    main()
