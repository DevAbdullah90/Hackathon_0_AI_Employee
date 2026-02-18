#!/usr/bin/env python3
"""
Dashboard Logger - Updates Dashboard.md with all platform activities
Call this after any post/send action to keep dashboard current
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class DashboardLogger:
    """Logs all activities to Dashboard.md"""

    def __init__(self, vault_path: Path = None):
        self.vault_path = vault_path or Path(__file__).parent
        self.dashboard_file = self.vault_path / 'Activity_Log.md'
        self.log_file = self.vault_path / 'Logs' / 'activity.json'
        self.log_file.parent.mkdir(exist_ok=True)

    def log_activity(
        self,
        platform: str,
        action: str,
        status: str,
        details: Dict[str, Any] = None,
        url: str = None
    ):
        """
        Log an activity to dashboard and JSON log

        Args:
            platform: twitter, linkedin, whatsapp, email, instagram
            action: posted, sent, replied, failed
            status: success, failed
            details: Additional details dict
            url: Optional URL to the post
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        icon = self._get_icon(platform, status)

        # Build dashboard entry
        entry = f"""

## {timestamp} - {icon} {platform.title()} {action.title()}

**Platform**: {platform}
**Status**: {'Successfully ' + action if status == 'success' else 'Failed to ' + action}
"""

        if details:
            for key, value in details.items():
                if value:
                    entry += f"**{key.title()}**: {value}\n"

        if url:
            entry += f"**URL**: {url}\n"

        entry += "\n---\n"

        # Append to dashboard
        try:
            with open(self.dashboard_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception as e:
            print(f"Failed to update dashboard: {e}")

        # Also log to JSON
        self._log_json(platform, action, status, details, url)

    def _get_icon(self, platform: str, status: str) -> str:
        """Get status icon"""
        if status != 'success':
            return '❌'

        icons = {
            'twitter': '🐦',
            'linkedin': '💼',
            'whatsapp': '💬',
            'email': '📧',
            'instagram': '📸'
        }
        return icons.get(platform, '✅')

    def _log_json(
        self,
        platform: str,
        action: str,
        status: str,
        details: Dict,
        url: str
    ):
        """Log to JSON file"""
        try:
            # Load existing logs
            logs = []
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)

            # Add new entry
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'platform': platform,
                'action': action,
                'status': status,
                'details': details,
                'url': url
            })

            # Keep last 1000 entries
            logs = logs[-1000:]

            # Save
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print(f"Failed to log JSON: {e}")

    def log_twitter(self, tweet_text: str, success: bool, url: str = None, error: str = None):
        """Log Twitter activity"""
        self.log_activity(
            platform='twitter',
            action='posted' if success else 'failed',
            status='success' if success else 'failed',
            details={
                'content': tweet_text[:100] + '...' if len(tweet_text) > 100 else tweet_text,
                'error': error
            },
            url=url
        )

    def log_linkedin(self, content: str, success: bool, url: str = None, error: str = None):
        """Log LinkedIn activity"""
        self.log_activity(
            platform='linkedin',
            action='posted' if success else 'failed',
            status='success' if success else 'failed',
            details={
                'content': content[:100] + '...' if len(content) > 100 else content,
                'error': error
            },
            url=url
        )

    def log_email(self, to: str, subject: str, success: bool, error: str = None):
        """Log Email activity"""
        self.log_activity(
            platform='email',
            action='sent' if success else 'failed',
            status='success' if success else 'failed',
            details={
                'to': to,
                'subject': subject,
                'error': error
            }
        )

    def log_whatsapp(self, phone: str, success: bool, error: str = None):
        """Log WhatsApp activity"""
        self.log_activity(
            platform='whatsapp',
            action='sent' if success else 'failed',
            status='success' if success else 'failed',
            details={
                'phone': phone,
                'error': error
            }
        )

    def log_instagram(self, post_type: str, success: bool, error: str = None):
        """Log Instagram activity"""
        self.log_activity(
            platform='instagram',
            action='posted' if success else 'failed',
            status='success' if success else 'failed',
            details={
                'type': post_type,
                'error': error
            }
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get activity statistics"""
        try:
            if not self.log_file.exists():
                return {'total': 0}

            with open(self.log_file, 'r') as f:
                logs = json.load(f)

            stats = {
                'total': len(logs),
                'success': len([l for l in logs if l.get('status') == 'success']),
                'failed': len([l for l in logs if l.get('status') == 'failed']),
                'by_platform': {}
            }

            for log in logs:
                platform = log.get('platform', 'unknown')
                if platform not in stats['by_platform']:
                    stats['by_platform'][platform] = 0
                stats['by_platform'][platform] += 1

            return stats

        except Exception as e:
            return {'error': str(e)}


# Global instance
logger = DashboardLogger()


def log_twitter(tweet: str, success: bool, url: str = None, error: str = None):
    logger.log_twitter(tweet, success, url, error)

def log_linkedin(content: str, success: bool, url: str = None, error: str = None):
    logger.log_linkedin(content, success, url, error)

def log_email(to: str, subject: str, success: bool, error: str = None):
    logger.log_email(to, subject, success, error)

def log_whatsapp(phone: str, success: bool, error: str = None):
    logger.log_whatsapp(phone, success, error)

def log_instagram(post_type: str, success: bool, error: str = None):
    logger.log_instagram(post_type, success, error)


if __name__ == '__main__':
    # Test
    logger = DashboardLogger()
    logger.log_twitter("Test tweet", True, "https://twitter.com/test/123")
    print("Dashboard logger ready!")
    print("Stats:", logger.get_stats())
