#!/usr/bin/env python3
"""
Social Media Content Generator
Creates content for Facebook, Instagram, and Twitter/X
"""

import os
import sys
import json
import logging
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re
import cp1252

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialContentGenerator:
    """Generates content for social media platforms"""

    def __init__(self, vault_path: str = None):
        if vault_path is None:
            self.vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\Desktop\\hakathone zero\\AI_Employee_Vault")
        else:
            self.vault_path = Path(vault_path)
        self.posts_folder = self.vault_path / 'Social_Media_Posts'
        self.posts_folder.mkdir(exist_ok=True)

        # Content templates
        self.templates = self._load_templates()
        self.used_content = self._load_used_content()

    def _load_templates(self) -> Dict[str, List[str]]:
        """Load content templates for different platforms"""
        return {
            'facebook': [
                "Exciting update! We've just completed {project_name} for {client_name}. Here's what we achieved:

✅ {achievement_1}
✅ {achievement_2}
✅ {achievement_3}

Ready to help your business grow? Let's talk!",
                "Business Tip: {tip}

At {company_name}, we help businesses like yours {value_proposition}. What's your biggest challenge this week?",
                "Did you know? {statistic}

This is why we focus on {specialty}. How is your business handling this?",
                "Success Story: We helped {client_name} achieve {result} in just {timeframe}!

Here's how:
{story_points}

What's your business goal?",
                "Question for business owners: {question}

We specialize in {expertise} and love helping solve these challenges. Drop a comment below!"
            ],
            'instagram': [
                "TRANSFORMATION TUESDAY

Before → After

{transformation_story}

Swipe to see the results!

What transformation does your business need?

#BusinessGrowth #Results #Transformation",
                "BUSINESS REALITY CHECK

❌ {myth}
✅ {reality}

Don't fall for common misconceptions. Get expert help!

#BusinessTips #EntrepreneurLife #MondayMotivation",
                "RESULTS DON'T LIE

{metric} in {timeframe}

This is what happens when you have the right strategy. Ready for results like this?

#Success #Growth #BusinessResults",
                "QUICK TIP

{tip}

Save this post for later!

What's your best business tip? Share below!

#BusinessTips #Entrepreneur #SmallBusiness",
                "BEHIND THE SCENES

{behind_scenes_story}

Building great results takes hard work and expertise!

#TeamWork #Process #BusinessBehindTheScenes"
            ],
            'twitter': [
                "{tip}

This is why {strategy} matters for your business.

What's your approach?",
                "{statistic}

The numbers don't lie. Is your business keeping up?

Here's what you can do: {action}

#BusinessGrowth #DataDriven",
                "Just achieved {result} for {client_name}!

{brief_description}

Your turn? DM me!",
                "Pro tip: {tip}

Small changes, big impact. Try this and let me know how it goes!",
                "{question}

As someone who helps businesses {expertise}, I'm curious about your experience.

Share below!"
            ]
        }

    def _load_used_content(self) -> List[str]:
        """Load recently used content to avoid repetition"""
        tracking_file = self.vault_path / '.social_content_tracking'
        if tracking_file.exists():
            return json.loads(tracking_file.read_text()).get('used_hashes', [])[:50]
        return []

    def _save_used_content(self):
        """Save used content hashes"""
        tracking_file = self.vault_path / '.social_content_tracking'
        tracking_file.write_text(json.dumps({
            'used_hashes': self.used_content,
            'last_updated': datetime.now().isoformat()
        }, indent=2))

    def _generate_content_hash(self, template: str, variables: Dict[str, Any]) -> str:
        """Generate hash for content to check for duplicates"""
        import hashlib
        content = template.format(**variables)
        return hashlib.md5(content.encode()).hexdigest()

    def _fill_template(self, platform: str, content_type: str = 'general') -> str:
        """Fill a template with relevant content"""
        templates = self.templates.get(platform, [])
        if not templates:
            return ""

        # Select a random template
        template = random.choice(templates)

        # Generate hash to check if we've used this recently
        variables = self._generate_variables(platform, content_type)
        content_hash = self._generate_content_hash(template, variables)

        # Try different templates if this one was recently used
        attempts = 0
        while content_hash in self.used_content and attempts < len(templates):
            template = random.choice(templates)
            content_hash = self._generate_content_hash(template, variables)
            attempts += 1

        # Mark this content as used
        self.used_content.insert(0, content_hash)
        self._save_used_content()

        return template.format(**variables)

    def _generate_variables(self, platform: str, content_type: str) -> Dict[str, Any]:
        """Generate variables to fill templates"""
        variables = {
            'company_name': 'Our Company',
            'project_name': 'Project Alpha',
            'client_name': 'Client X',
            'achievement_1': 'Increased efficiency by 45%',
            'achievement_2': 'Reduced costs by $10K',
            'achievement_3': 'Delivered 2 weeks early',
            'tip': 'Focus on one goal at a time',
            'value_proposition': 'achieve your business goals',
            'specialty': 'data-driven solutions',
            'statistic': '78% of businesses see 2x growth',
            'timeframe': '3 months',
            'result': '50% increase in revenue',
            'question': 'What\'s your biggest business challenge?',
            'expertise': 'with strategic planning',
            'strategy': 'consistent optimization',
            'action': 'Start with a data audit',
            'brief_description': 'Strategic approach + execution = results',
            'transformation_story': 'Struggling business to thriving enterprise',
            'story_points': '1. Audit\n2. Plan\n3. Execute\n4. Optimize',
            'myth': 'You need a huge budget to grow',
            'reality': 'Strategic planning beats big budgets',
            'metric': '300% ROI',
            'behind_scenes_story': 'Team collaboration and late nights'
        }

        # Business-specific variables
        business_vars = self._load_business_variables()
        variables.update(business_vars)

        return variables

    def _load_business_variables(self) -> Dict[str, Any]:
        """Load business-specific variables from vault"""
        business_vars = {}

        # Load from Company_Handbook.md if exists
        business_goals = self.vault_path / 'Business_Goals.md'
        if business_goals.exists():
            try:
                content = business_goals.read_text(encoding='utf-8')

                # Extract key metrics
                import re
                metric_match = re.search(r'goal:\s*\$(\d+)', content, re.IGNORECASE)
                if metric_match:
                    business_vars['target_revenue'] = f"${metric_match.group(1)}"
            except Exception:
                pass  # File may have encoding issues, use defaults

        # Load from Company_Handbook.md if exists
        handbook = self.vault_path / 'Company_Handbook.md'
        if handbook.exists():
            try:
                content = handbook.read_text(encoding='utf-8')

                # Extract company values
                value_match = re.search(r'values?:(.+)', content, re.IGNORECASE)
                if value_match:
                    business_vars['company_value'] = value_match.group(1).strip()
            except Exception:
                pass  # File may have encoding issues, use defaults

        return business_vars

    def generate_facebook_post(self, content_type: str = 'general') -> Dict[str, Any]:
        """Generate Facebook post content"""
        content = self._fill_template('facebook', content_type)

        return {
            'platform': 'facebook',
            'content': content,
            'content_type': content_type,
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'max_length': 5000,  # Facebook post max length
            'current_length': len(content),
            'suggested_hashtags': ['#Business', '#Growth', '#Entrepreneur']
        }

    def generate_instagram_post(self, content_type: str = 'general') -> Dict[str, Any]:
        """Generate Instagram post content"""
        content = self._fill_template('instagram', content_type)

        # Instagram has a caption limit of 2,200 characters
        if len(content) > 2200:
            content = content[:2197] + '...'

        return {
            'platform': 'instagram',
            'content': content,
            'content_type': content_type,
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'max_length': 2200,
            'current_length': len(content),
            'suggested_hashtags': ['#BusinessTips', '#GrowthHacking', '#Success']
        }

    def generate_twitter_post(self, content_type: str = 'general') -> Dict[str, Any]:
        """Generate Twitter/X post content"""
        template = self._fill_template('twitter', content_type)

        # Twitter has a 280 character limit (unless using Twitter Premium)
        if len(template) > 280:
            template = template[:277] + '...'

        return {
            'platform': 'twitter',
            'content': template,
            'content_type': content_type,
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'max_length': 280,
            'current_length': len(template)
        }

    def generate_weekly_content_plan(self) -> Dict[str, Any]:
        """Generate a full week's content plan"""
        content_plan = {
            'week_start': datetime.now().strftime('%Y-%m-%d'),
            'created': datetime.now().isoformat(),
            'posts': []
        }

        platforms = ['facebook', 'instagram', 'twitter']
        content_types = ['general', 'tip', 'success', 'question', 'news']

        # Generate 21 posts (3 per day for 7 days)
        for day in range(7):
            for post_num in range(3):
                platform = random.choice(platforms)
                content_type = random.choice(content_types)

                if platform == 'facebook':
                    post = self.generate_facebook_post(content_type)
                elif platform == 'instagram':
                    post = self.generate_instagram_post(content_type)
                else:
                    post = self.generate_twitter_post(content_type)

                # Add to schedule
                post['scheduled_date'] = (datetime.now()
                    .replace(hour=10 + post_num * 4, minute=0, second=0, microsecond=0)
                    .strftime('%Y-%m-%d %H:%M:%S'))
                post['day'] = day + 1

                content_plan['posts'].append(post)

        # Sort by date
        content_plan['posts'].sort(key=lambda x: x['scheduled_date'])

        return content_plan

    def save_post(self, post: Dict[str, Any], filename: str = None) -> Path:
        """Save generated post to file"""
        try:
            if not filename:
                platform = post['platform']
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{platform}_{timestamp}.md"

            filepath = self.posts_folder / filename
            # Save post metadata and content
            header = f"""---
type: social_media_post
platform: {post['platform']}
content_type: {post['content_type']}
created: {post['created']}
status: {post['status']}
max_length: {post['max_length']}
current_length: {post['current_length']}
---

"""
            content = header + post['content']
            filepath.write_text(content)

            logger.info(f"Saved post to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving post: {e}")
            return None

    def save_content_plan(self, content_plan: Dict[str, Any]) -> Path:
        """Save content plan to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Content_Plan_{timestamp}.md"
            filepath = self.vault_path / filename

            content = f"""---
type: content_plan
week_start: {content_plan['week_start']}
created: {content_plan['created']}
post_count: {len(content_plan['posts'])}
---

# Weekly Social Media Content Plan

**Week Starting**: {content_plan['week_start']}
**Total Posts**: {len(content_plan['posts'])}
**Date Created**: {content_plan['created']}

## Schedule

| Day | Platform | Type | Time | Status | Word Count |
|-----|----------|------|------|--------|------------|
"""
            for i, post in enumerate(content_plan['posts'], 1):
                content += (f"| Day {post['day']} | {post['platform'].capitalize()} "
                           f"{post['content_type'].capitalize()} | {post['scheduled_date'].split(' ')[1]} | "
                           f"{post['status']} | {post['current_length']}/{post['max_length']} |\n")
            # Add full posts
            content += "\n\n## Full Posts\n\n"
            for i, post in enumerate(content_plan['posts'], 1):
                content += f"### Post {i}: {post['platform'].capitalize()} ({post['scheduled_date']})\n\n"
                content += f"{post['content']}\n\n"
                content += "---\n\n"

            filepath.write_text(content)
            logger.info(f"Saved content plan to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving content plan: {e}")
            return None

    def generate_posts_batch(self, count: int = 5, platform: str = None) -> List[Path]:
        """Generate multiple posts at once"""
        paths = []

        platforms = [platform] if platform else ['facebook', 'instagram', 'twitter']

        for _ in range(count):
            selected_platform = random.choice(platforms)

            if selected_platform == 'facebook':
                post = self.generate_facebook_post()
            elif selected_platform == 'instagram':
                post = self.generate_instagram_post()
            else:
                post = self.generate_twitter_post()

            filepath = self.save_post(post)
            if filepath:
                paths.append(filepath)

            return paths


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Social Media Content Generator')
    parser.add_argument('--vault', type=str, help='Path to vault', default=None)
    parser.add_argument('--platform', type=str,
                       choices=['facebook', 'instagram', 'twitter', 'all'],
                       default='all', help='Platform to generate for')
    parser.add_argument('--count', type=int, default=5, help='Number of posts to generate')
    parser.add_argument('--plan', action='store_true', help='Generate weekly content plan')

    args = parser.parse_args()

    vault_path = args.vault if args.vault else r"C:\Users\LENOVO X1 YOGA\Desktop\hakathone zero\AI_Employee_Vault"

    generator = SocialContentGenerator(vault_path)

    if args.plan:
        plan = generator.generate_weekly_content_plan()
        path = generator.save_content_plan(plan)
        print(f"Content plan saved to: {path}")
    else:
        if args.platform == 'all':
            paths = generator.generate_posts_batch(args.count)
        else:
            paths = generator.generate_posts_batch(args.count, args.platform)

        print(f"Generated {len(paths)} posts:")
        for path in paths:
            print(f"  - {path}")

if __name__ == "__main__":
    main()
