#!/usr/bin/env python3
"""
Error Recovery and Graceful Degradation System
Ensures AI Employee continues operating even when components fail
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from audit_logger import AuditLogger


class ErrorRecoverySystem:
    """Handles errors and implements graceful degradation"""

    def __init__(self):
        self.vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\Desktop\\hakathone zero\\AI_Employee_Vault")
        self.state_file = self.vault_path / "state" / "error_recovery_state.json"
        self.state_file.parent.mkdir(exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self.audit_logger = AuditLogger()

        # Component health tracking
        self.component_health = self._load_component_health()

        # Retry configuration
        self.retry_config = {
            "max_retries": 3,
            "base_delay": 5,  # seconds
            "max_delay": 300  # 5 minutes
        }

        # Circuit breaker configuration
        self.circuit_breaker = {
            "failure_threshold": 5,
            "recovery_timeout": 600,  # 10 minutes
            "half_open_max_calls": 3
        }

    def _load_component_health(self) -> Dict[str, Any]:
        """Load component health state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load component health: {e}")

        # Default component health
        return {
            "gmail_watcher": {"status": "healthy", "failures": 0, "last_failure": None},
            "linkedin_watcher": {"status": "healthy", "failures": 0, "last_failure": None},
            "filesystem_watcher": {"status": "healthy", "failures": 0, "last_failure": None},
            "email_mcp": {"status": "healthy", "failures": 0, "last_failure": None},
            "linkedin_mcp": {"status": "healthy", "failures": 0, "last_failure": None},
            "twitter_mcp": {"status": "healthy", "failures": 0, "last_failure": None},
            "instagram_mcp": {"status": "healthy", "failures": 0, "last_failure": None},
            "reddit_mcp": {"status": "healthy", "failures": 0, "last_failure": None},
            "whatsapp_mcp": {"status": "healthy", "failures": 0, "last_failure": None}
        }

    def _save_component_health(self):
        """Save component health state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.component_health, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save component health: {e}")

    def is_component_healthy(self, component_name: str) -> bool:
        """Check if component is healthy"""
        if component_name not in self.component_health:
            return True  # Assume healthy if not tracked

        health = self.component_health[component_name]

        if health["status"] == "healthy":
            return True

        if health["status"] == "degraded":
            return True  # Still operational but with issues

        if health["status"] == "failed":
            # Check if recovery timeout has passed
            if health["last_failure"]:
                last_failure = datetime.fromisoformat(health["last_failure"])
                if datetime.now() - last_failure > timedelta(seconds=self.circuit_breaker["recovery_timeout"]):
                    # Try to recover
                    health["status"] = "recovering"
                    self._save_component_health()
                    return True
            return False

        if health["status"] == "recovering":
            # In half-open state, allow limited calls
            return True

        return False

    def record_component_failure(self, component_name: str, error: str):
        """Record a component failure"""
        if component_name not in self.component_health:
            self.component_health[component_name] = {
                "status": "healthy",
                "failures": 0,
                "last_failure": None
            }

        health = self.component_health[component_name]
        health["failures"] += 1
        health["last_failure"] = datetime.now().isoformat()

        # Update status based on failure count
        if health["failures"] >= self.circuit_breaker["failure_threshold"]:
            health["status"] = "failed"
            self.logger.critical(f"Component {component_name} marked as FAILED")
            self.audit_logger.log_error(
                error_type="COMPONENT_FAILURE",
                error_message=f"Component {component_name} exceeded failure threshold",
                context={"component": component_name, "failure_count": health["failures"]}
            )
        elif health["failures"] >= self.circuit_breaker["failure_threshold"] // 2:
            health["status"] = "degraded"
            self.logger.warning(f"Component {component_name} marked as DEGRADED")

        self._save_component_health()

    def record_component_success(self, component_name: str):
        """Record a component success"""
        if component_name not in self.component_health:
            return

        health = self.component_health[component_name]

        # If component was recovering, check if it's fully recovered
        if health["status"] == "recovering":
            # This would track successful calls during recovery
            pass

        # Reset failure count on success
        if health["status"] in ["failed", "degraded"]:
            # Gradual recovery
            health["failures"] = max(0, health["failures"] - 1)

            if health["failures"] == 0:
                health["status"] = "healthy"
                self.logger.info(f"Component {component_name} recovered to HEALTHY")
                self.audit_logger.log_action(
                    action_type="component_recovered",
                    actor="ErrorRecoverySystem",
                    details={"component": component_name}
                )

        self._save_component_health()

    def with_retry(self, func: Callable, component_name: str, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic

        Args:
            func: Function to execute
            component_name: Name of component for health tracking
            *args, **kwargs: Arguments for the function

        Returns:
            Function result

        Raises:
            Exception if all retries fail
        """
        if not self.is_component_healthy(component_name):
            error_msg = f"Component {component_name} is not healthy"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        last_exception = None

        for attempt in range(self.retry_config["max_retries"]):
            try:
                result = func(*args, **kwargs)
                self.record_component_success(component_name)
                return result

            except Exception as e:
                last_exception = e
                self.logger.warning(f"Attempt {attempt + 1} failed for {component_name}: {e}")

                # Record failure
                self.record_component_failure(component_name, str(e))

                # Log detailed error
                self.audit_logger.log_error(
                    error_type=f"{component_name}_ERROR",
                    error_message=str(e),
                    stack_trace=traceback.format_exc(),
                    context={"attempt": attempt + 1, "component": component_name}
                )

                # Calculate delay with exponential backoff
                delay = min(
                    self.retry_config["base_delay"] * (2 ** attempt),
                    self.retry_config["max_delay"]
                )

                self.logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)

                # If component is now unhealthy, stop retrying
                if not self.is_component_healthy(component_name):
                    break

        # All retries failed
        error_msg = f"All retries failed for {component_name}: {str(last_exception)}"
        self.logger.error(error_msg)
        raise last_exception

    def graceful_degradation(self, primary_func: Callable, backup_func: Callable,
                           component_name: str, *args, **kwargs) -> Any:
        """
        Try primary function, fall back to backup on failure

        Args:
            primary_func: Primary function to try
            backup_func: Backup function if primary fails
            component_name: Component name for health tracking
            *args, **kwargs: Arguments for functions

        Returns:
            Result from primary or backup function
        """
        try:
            result = self.with_retry(primary_func, component_name, *args, **kwargs)
            self.logger.info(f"Primary function succeeded for {component_name}")
            return result

        except Exception as e:
            self.logger.warning(f"Primary failed for {component_name}, trying backup: {e}")

            try:
                result = backup_func(*args, **kwargs)
                self.logger.info(f"Backup function succeeded for {component_name}")

                # Log that we fell back to backup
                self.audit_logger.log_action(
                    action_type="graceful_degradation",
                    actor="ErrorRecoverySystem",
                    details={
                        "component": component_name,
                        "reason": str(e),
                        "fallback_used": True
                    }
                )

                return result

            except Exception as backup_e:
                self.logger.error(f"Backup also failed for {component_name}: {backup_e}")
                self.audit_logger.log_error(
                    error_type="BACKUP_FAILED",
                    error_message=str(backup_e),
                    context={"component": component_name}
                )
                raise

    def safe_execute(self, func: Callable, component_name: str, fallback_value: Any = None,
                    *args, **kwargs) -> Any:
        """
        Safely execute a function with comprehensive error handling

        Args:
            func: Function to execute
            component_name: Component name
            fallback_value: Value to return if all fails
            *args, **kwargs: Function arguments

        Returns:
            Function result or fallback value
        """
        try:
            return self.with_retry(func, component_name, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Safe execution failed for {component_name}: {e}")

            if fallback_value is not None:
                self.logger.info(f"Returning fallback value for {component_name}")
                return fallback_value

            # Re-raise if no fallback
            raise

    def get_system_health_report(self) -> Dict[str, Any]:
        """Get overall system health report"""
        healthy_count = 0
        degraded_count = 0
        failed_count = 0

        for component, health in self.component_health.items():
            status = health["status"]
            if status == "healthy":
                healthy_count += 1
            elif status == "degraded":
                degraded_count += 1
            elif status in ["failed", "recovering"]:
                failed_count += 1

        total_components = len(self.component_health)

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if failed_count == 0 else "degraded" if failed_count < total_components // 2 else "critical",
            "summary": {
                "total_components": total_components,
                "healthy": healthy_count,
                "degraded": degraded_count,
                "failed": failed_count
            },
            "components": self.component_health,
            "system_operational": failed_count < total_components
        }

    def generate_health_dashboard(self) -> str:
        """Generate health dashboard markdown"""
        report = self.get_system_health_report()

        dashboard = []
        dashboard.append("# 🏥 System Health Dashboard")
        dashboard.append(f"**Report Generated:** {report['timestamp']}")
        dashboard.append(f"**Overall Status:** {report['overall_status'].upper()}")
        dashboard.append("")

        # Summary
        dashboard.append("## 📊 Health Summary")
        dashboard.append(f"- Healthy Components: {report['summary']['healthy']}")
        dashboard.append(f"- Degraded Components: {report['summary']['degraded']}")
        dashboard.append(f"- Failed Components: {report['summary']['failed']}")
        dashboard.append(f"- System Operational: {'✅ Yes' if report['system_operational'] else '❌ No'}")
        dashboard.append("")

        # Detailed component status
        dashboard.append("## 🔍 Component Status")
        dashboard.append("")

        for component, health in report['components'].items():
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "failed": "❌",
                "recovering": "🔄"
            }.get(health['status'], "❓")

            dashboard.append(f"### {status_emoji} {component}")
            dashboard.append(f"- Status: {health['status']}")
            dashboard.append(f"- Failures: {health['failures']}")
            if health['last_failure']:
                dashboard.append(f"- Last Failure: {health['last_failure']}")
            dashboard.append("")

        return "\n".join(dashboard)

    def save_health_dashboard(self) -> Path:
        """Save health dashboard to file"""
        dashboard_content = self.generate_health_dashboard()

        dashboard_file = self.vault_path / "Reports" / f"Health_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        dashboard_file.parent.mkdir(exist_ok=True)

        dashboard_file.write_text(dashboard_content)
        self.logger.info(f"Health dashboard saved: {dashboard_file}")

        return dashboard_file


def main():
    """Main function for CLI"""
    error_system = ErrorRecoverySystem()
    report = error_system.get_system_health_report()
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
