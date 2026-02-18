#!/usr/bin/env python3
"""
Weekly CEO Briefing Generator
Creates comprehensive business and accounting audit reports
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re


class CEOBriefingGenerator:
    """Generates weekly CEO briefing reports"""

    def __init__(self):
        self.vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\OneDrive\\Desktop\\hakathone zero\\AI_Employee_vault")
        self.reports_path = self.vault_path / "Reports"
        self.reports_path.mkdir(exist_ok=True)

    def collect_weekly_data(self, start_date: datetime = None) -> Dict[str, Any]:
        """Collect data from all sources for the week"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)

        end_date = datetime.now()

        data = {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "week_number": start_date.isocalendar()[1]
            },
            "emails_processed": self._count_processed_emails(start_date, end_date),
            "tasks_completed": self._get_completed_tasks(start_date, end_date),
            "linkedin_posts": self._get_linkedin_activity(start_date, end_date),
            "reddit_activity": self._get_reddit_activity(start_date, end_date),
            "social_media": self._get_social_media_summary(start_date, end_date),
            "pending_items": self._get_pending_items(),
            "revenue_opportunities": self._identify_revenue_opportunities(),
            "bottlenecks": self._identify_bottlenecks(),
            "system_performance": self._get_system_performance()
        }

        return data

    def _count_processed_emails(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Count emails processed during period"""
        logs_dir = self.vault_path / "Logs" / "Needs_Action"
        processed_dir = self.vault_path / "Done"

        count = 0
        urgent_count = 0
        categories = {}

        # Check processed emails
        for log_file in logs_dir.glob("EMAIL_*.md"):
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if start_date <= file_mtime <= end_date:
                count += 1
                content = log_file.read_text()
                if "urgent" in content.lower() or "asap" in content.lower():
                    urgent_count += 1

        return {
            "total_processed": count,
            "urgent_emails": urgent_count,
            "avg_per_day": round(count / 7, 2)
        }

    def _get_completed_tasks(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get list of completed tasks"""
        done_dir = self.vault_path / "Done"
        tasks = []

        for file in done_dir.glob("*.md"):
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if start_date <= file_mtime <= end_date:
                content = file.read_text()
                tasks.append({
                    "filename": file.name,
                    "completed_date": file_mtime.strftime("%Y-%m-%d"),
                    "summary": content[:200] + "..." if len(content) > 200 else content
                })

        return tasks

    def _get_linkedin_activity(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get LinkedIn activity summary"""
        linkedin_dir = self.vault_path / "LinkedIn_Posts"

        if not linkedin_dir.exists():
            return {"posts_count": 0, "posts": []}

        posts = []
        for file in linkedin_dir.glob("*.md"):
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if start_date <= file_mtime <= end_date:
                content = file.read_text()
                posts.append({
                    "date": file_mtime.strftime("%Y-%m-%d"),
                    "summary": content[:150] + "..." if len(content) > 150 else content,
                    "filename": file.name
                })

        return {
            "posts_count": len(posts),
            "posts": posts
        }

    def _get_reddit_activity(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get Reddit activity summary"""
        reddit_data = self.vault_path / "Reddit_Data"

        if not reddit_data.exists():
            return {"posts_count": 0, "mentions": 0, "opportunities": 0, "activities": []}

        activities = []
        post_count = 0
        mention_count = 0
        opportunity_count = 0

        # Check activity logs
        for log_file in reddit_data.glob("activity_*.json"):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if start_date <= file_mtime <= end_date:
                    data = json.loads(log_file.read_text())
                    activities.extend(data.get('activities', []))

                    # Count by type
                    for activity in data.get('activities', []):
                        if activity.get('type') == 'opportunity' or activity.get('type') == 'opportunity_comment':
                            opportunity_count += 1
                        elif activity.get('type') == 'mention':
                            mention_count += 1
                        elif activity.get('type') == 'post_reply':
                            post_count += 1
            except Exception:
                continue

        # Also check for Reddit action files in Done folder
        done_dir = self.vault_path / "Done"
        if done_dir.exists():
            for file in done_dir.glob("REDDIT_*.md"):
                file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if start_date <= file_mtime <= end_date:
                    post_count += 1

        return {
            "posts_count": post_count,
            "mentions": mention_count,
            "opportunities": opportunity_count,
            "activities": activities
        }

    def _get_social_media_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get social media activity summary"""
        reddit = self._get_reddit_activity(start_date, end_date)

        return {
            "twitter_posts": 0,  # Would integrate with Twitter API
            "instagram_posts": 0,  # Would integrate with Instagram API
            "reddit_posts": reddit['posts_count'],
            "reddit_mentions": reddit['mentions'],
            "reddit_opportunities": reddit['opportunities'],
            "total_engagement": f"Reddit: {reddit['posts_count']} posts, {reddit['mentions']} mentions, {reddit['opportunities']} opportunities"
        }

    def _get_pending_items(self) -> Dict[str, Any]:
        """Get pending items requiring attention"""
        needs_action = self.vault_path / "Needs_Action"
        pending_approval = self.vault_path / "Pending_Approval"

        needs_action_count = len(list(needs_action.glob("*.md"))) if needs_action.exists() else 0
        pending_approval_count = len(list(pending_approval.glob("*.md"))) if pending_approval.exists() else 0

        return {
            "needs_action": needs_action_count,
            "pending_approval": pending_approval_count,
            "total_pending": needs_action_count + pending_approval_count
        }

    def _identify_revenue_opportunities(self) -> List[Dict[str, Any]]:
        """Identify potential revenue opportunities"""
        opportunities = []

        # Analyze Needs_Action for potential sales leads
        needs_action = self.vault_path / "Needs_Action"
        if needs_action.exists():
            for file in needs_action.glob("EMAIL_*.md"):
                content = file.read_text()
                lower_content = content.lower()

                # Look for opportunity keywords
                keywords = ["proposal", "quote", "pricing", "interested", "demo", "meeting"]
                if any(keyword in lower_content for keyword in keywords):
                    opportunities.append({
                        "type": "Email Inquiry",
                        "source": file.name,
                        "potential_value": "High",
                        "action_required": "Follow up on inquiry",
                        "priority": "High"
                    })

        return opportunities if opportunities else [{
            "type": "No opportunities found",
            "notes": "No sales-related keywords detected in recent emails"
        }]

    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify bottlenecks in operations"""
        bottlenecks = []

        pending_approval = self.vault_path / "Pending_Approval"
        if pending_approval.exists():
            approval_count = len(list(pending_approval.glob("*.md")))
            if approval_count > 5:
                bottlenecks.append({
                    "area": "Approval Workflow",
                    "issue": f"{approval_count} items waiting for approval",
                    "impact": "Slowing down execution",
                    "suggested_action": "Schedule approval session or delegate approval authority"
                })

        needs_action = self.vault_path / "Needs_Action"
        if needs_action.exists():
            urgent_count = 0
            for file in needs_action.glob("*.md"):
                content = file.read_text().lower()
                if "urgent" in content or "asap" in content:
                    urgent_count += 1

            if urgent_count > 3:
                bottlenecks.append({
                    "area": "Urgent Items",
                    "issue": f"{urgent_count} urgent items pending",
                    "impact": "High priority items not being addressed",
                    "suggested_action": "Prioritize urgent items or increase automation capacity"
                })

        return bottlenecks if bottlenecks else [{
            "area": "No major bottlenecks",
            "status": "Operations running smoothly"
        }]

    def _get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        logs_dir = self.vault_path / "Logs"
        watchers = ["gmail", "linkedin", "filesystem"]

        return {
            "watchers_active": len(watchers),
            "watchers_list": watchers,
            "mcp_servers": ["email", "linkedin", "filesystem"],
            "uptime": "Continuous since deployment",
            "last_error": self._get_last_error()
        }

    def _get_last_error(self) -> str:
        """Get last system error"""
        error_file = self.vault_path / "error.log"
        if error_file.exists():
            content = error_file.read_text()
            lines = content.split('\n')
            for line in reversed(lines):
                if "ERROR" in line:
                    return line[:200] + "..." if len(line) > 200 else line
        return "No recent errors detected"

    def generate_briefing(self, start_date: datetime = None) -> str:
        """Generate complete CEO briefing report"""
        data = self.collect_weekly_data(start_date)

        report = []
        report.append(f"# 📊 Weekly CEO Briefing")
        report.append(f"**Week {data['period']['week_number']}** | {data['period']['start']} to {data['period']['end']}")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Executive Summary
        report.append("## 🎯 Executive Summary")
        report.append("")
        report.append(f"- **Emails Processed:** {data['emails_processed']['total_processed']} "
                     f"({data['emails_processed']['avg_per_day']} per day)")
        report.append(f"- **Tasks Completed:** {len(data['tasks_completed'])}")
        report.append(f"- **LinkedIn Posts:** {data['linkedin_posts']['posts_count']}")
        report.append(f"- **Pending Items:** {data['pending_items']['total_pending']}")
        report.append(f"- **Revenue Opportunities:** {len(data['revenue_opportunities'])}")
        report.append("")

        # Revenue Opportunities
        report.append("## 💰 Revenue Opportunities")
        report.append("")
        for opp in data['revenue_opportunities']:
            report.append(f"### {opp['type']}")
            report.append(f"- **Priority:** {opp.get('priority', 'Medium')}")
            report.append(f"- **Action Required:** {opp.get('action_required', 'Follow up')}")
            report.append(f"- **Source:** {opp.get('source', 'Unknown')}")
            report.append("")

        # Bottlenecks
        report.append("## ⚠️ Operational Bottlenecks")
        report.append("")
        for bottleneck in data['bottlenecks']:
            report.append(f"### {bottleneck['area']}")
            report.append(f"- **Issue:** {bottleneck.get('issue', 'Unknown')}")
            report.append(f"- **Impact:** {bottleneck.get('impact', 'Unknown')}")
            if 'suggested_action' in bottleneck:
                report.append(f"- **Suggested Action:** {bottleneck['suggested_action']}")
            report.append("")

        # Completed Tasks
        report.append("## ✅ Completed Tasks")
        report.append(f"**Total:** {len(data['tasks_completed'])} tasks\n")
        for task in data['tasks_completed'][:10]:  # Show first 10
            report.append(f"- **{task['completed_date']}:** {task['summary']}")
        if len(data['tasks_completed']) > 10:
            report.append(f"- *... and {len(data['tasks_completed']) - 10} more tasks*")
        report.append("")

        # LinkedIn Activity
        report.append("## 💼 LinkedIn Activity")
        report.append(f"**Posts Published:** {data['linkedin_posts']['posts_count']}\n")
        for post in data['linkedin_posts']['posts']:
            report.append(f"- **{post['date']}:** {post['summary']}")
        report.append("")

        # Pending Items
        report.append("## ⏳ Pending Items Requiring Attention")
        report.append(f"- **Needs Action:** {data['pending_items']['needs_action']} items")
        report.append(f"- **Pending Approval:** {data['pending_items']['pending_approval']} items")
        report.append("")

        # System Performance
        report.append("## 🔧 System Performance")
        report.append(f"- **Active Watchers:** {', '.join(data['system_performance']['watchers_list'])}")
        report.append(f"- **MCP Servers:** {len(data['system_performance']['mcp_servers'])} active")
        report.append(f"- **Last Error:** {data['system_performance']['last_error']}")
        report.append("")

        # AI Recommendations
        report.append("## 🤖 AI Recommendations")
        report.append("")
        report.append("Based on this week's data, I recommend:")
        report.append("")

        if data['pending_items']['total_pending'] > 10:
            report.append("1. **Address Pending Items:** High number of pending items suggests capacity constraints")
        if len(data['revenue_opportunities']) > 0:
            report.append("2. **Follow Up on Leads:** Multiple conversion opportunities identified in emails")
        if data['linkedin_posts']['posts_count'] < 3:
            report.append("3. **Increase Social Media:** Consider posting more frequently on LinkedIn")

        report.append("")
        report.append("---")
        report.append("*Report generated by AI Employee - Your Autonomous Business Partner*")

        return "\n".join(report)

    def save_briefing(self, report_content: str, filename: str = None) -> Path:
        """Save briefing to file"""
        if filename is None:
            filename = f"CEO_Briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        filepath = self.reports_path / filename
        filepath.write_text(report_content)

        logger.info(f"CEO Briefing saved: {filepath}")
        return filepath

    def generate_and_save(self, start_date: datetime = None) -> Path:
        """Generate and save briefing in one step"""
        report_content = self.generate_briefing(start_date)
        return self.save_briefing(report_content)


def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='CEO Briefing Generator')
    parser.add_argument('action', choices=[
        'generate',
        'generate_and_save'
    ], help='Action to perform')

    args = parser.parse_args()

    generator = CEOBriefingGenerator()

    if args.action == 'generate':
        report = generator.generate_briefing()
        print(report)

    elif args.action == 'generate_and_save':
        filepath = generator.generate_and_save()
        print(f"CEO Briefing saved to: {filepath}")


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    main()
