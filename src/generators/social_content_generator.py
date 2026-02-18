#!/usr/bin/env python3
"""
Social Media Content Generator Agent Skill
Automatically generates engaging content for Twitter, Instagram, LinkedIn, and Reddit
"""

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re
from gemini_client import GeminiClient

class SocialContentGenerator:
    """Generates social media content based on business context and trends"""

    def __init__(self):
        self.vault_path = Path("C:\\Users\\hp\\OneDrive\\Desktop\\Hackathon_AI_Employee")
        self.content_templates = self._load_templates()
        self.generated_content = []
        self.ai_client = GeminiClient()

    def _load_templates(self) -> Dict[str, List[str]]:
        """Load content templates for different platforms"""
        return {
            "twitter": [
                "🚀 {business_name} is revolutionizing {industry} with AI-powered solutions! ",
                "Just deployed {achievement} for a client! Results: {metric}. ",
                "Quick tip: {tip} #AI #Automation #Business",
                "Excited to share: {announcement} 🎉",
                "Behind the scenes at {business_name}: {insight}"
            ],
            "linkedin": [
                "I'm excited to announce that {business_name} has achieved {milestone}! "
                "This represents {impact} for our clients in the {industry} space. "
                "Thank you to our amazing team and partners who made this possible.\n\n"
                "What's your biggest milestone this quarter?",

                "5 lessons learned from {experience}:\n\n"
                "1. {lesson1}\n"
                "2. {lesson2}\n"
                "3. {lesson3}\n"
                "4. {lesson4}\n"
                "5. {lesson5}\n\n"
                "What would you add to this list?",

                "The future of {industry} is here, and it's powered by AI. "
                "At {business_name}, we're seeing {trend} transform how businesses operate. "
                "The key insight? {insight}\n\n"
                "How is AI impacting your industry?"
            ],
            "instagram": [
                "{visual_description} ✨\n\n"
                "{caption}\n\n"
                "#{hashtag1} #{hashtag2} #{hashtag3}",

                "{story_hook}\n\n"
                "{body}\n\n"
                "{call_to_action}",

                "💡 Did you know? {fact}\n\n"
                "{explanation}\n\n"
                "Save this post for later!"
            ],
            "reddit": [
                "[{industry}] Just achieved {achievement} - here's what I learned\n\n"
                "{story}\n\n"
                "Happy to answer any questions about the process!",

                "How do you handle {challenge} in {industry}?\n\n"
                "At {business_name}, we've tried {approach} with {results}.\n\n"
                "What's working for you?",

                "[Case Study] How we helped {client_type} increase {metric} by {percentage}\n\n"
                "{details}\n\n"
                "AMA about our approach!"
            ]
        }

    def _get_business_context(self) -> Dict[str, Any]:
        """Extract business context from vault files"""
        context = {
            "business_name": "Your Business",
            "industry": "AI Automation",
            "milestone": "new automation deployment",
            "achievement": "automated workflow",
            "metric": "50% time savings",
            "experience": "deploying 10 AI agents"
        }

        # Try to load from Company Handbook
        handbook_path = self.vault_path / "Company_Handbook.md"
        if handbook_path.exists():
            content = handbook_path.read_text(encoding='utf-8')  # Specify UTF-8 encoding to handle special characters/emojis properly
        else:
            content = ""
            # Fall back to default context if file doesn't exist
            return context

        # Try to load from Company Handbook
        handbook_path = self.vault_path / "Company_Handbook.md"
        if handbook_path.exists():
            content = handbook_path.read_text(encoding='utf-8')  # Explicitly specify UTF-8 encoding for reading text files with potential Unicode characters to prevent UnicodeDecodeError

            # Extract business name
            if "#### Company Name:" in content:
                match = re.search(r"#### Company Name:\s*(.+)", content)
                if match:
                    context["business_name"] = match.group(1).strip()

            # Extract business goals
            goal_match = re.search(r"#### Primary Business Goal:\s*(.+)", content)
            if goal_match:
                context["primary_goal"] = goal_match.group(1).strip()

        return context

    def generate_twitter_post(self, content_type="general"):
        '''Generate Twitter post content using predefined templates'''
        template = random.choice(self.content_templates["twitter"])
        context = self._get_business_context()

        # Fill template with context
        content = template.format(**context)

        # Ensure Twitter's character limit
        if len(content) > 280:
            content = content[:277] + "..."

        return {
            "platform": "twitter",
            "content": content,
            "character_count": len(content),
            "status": "draft"
        }

        return context

    def generate_twitter_post(self, topic: str = None, context: Dict = None) -> Dict[str, Any]:
        """Generate a Twitter post using Gemini if available"""
        if context is None:
            context = self._get_business_context()

        # Use Gemini if API key is available
        if self.ai_client.api_key:
            prompt = f"""Generate a Twitter post about {topic or 'our latest updates'}.
            Business Context: {json.dumps(context)}
            Maintain a professional but engaging tone.
            Ensure it is under 280 characters.
            Include relevant hashtags.
            """
            content = self.ai_client.generate_content(prompt)
            # Ensure character limit
            if len(content) > 280:
                content = content[:277] + "..."
                
            return {
                "platform": "twitter",
                "content": content,
                "character_count": len(content),
                "hashtags": re.findall(r'#\w+', content),
                "created_at": datetime.now().isoformat()
            }

        # Fallback to templates
        template = random.choice(self.content_templates["twitter"])

        # Fill in placeholders
        placeholders = {
            "{business_name}": context.get("business_name", "Your Business"),
            "{industry}": context.get("industry", "tech"),
            "{achievement}": "workflow automation",
            "{metric}": "40% efficiency gain",
            "{tip}": "Automate repetitive tasks first",
            "{announcement}": "New feature launch",
            "{insight}": "AI reduces manual work by 60%"
        }

        content = template
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, value)

        # Ensure it's under 280 characters
        if len(content) > 280:
            content = content[:277] + "..."

        return {
            "platform": "twitter",
            "content": content,
            "character_count": len(content),
            "hashtags": re.findall(r'#\w+', content),
            "created_at": datetime.now().isoformat()
        }

    def generate_linkedin_post(self, topic: str = None, context: Dict = None) -> Dict[str, Any]:
        """Generate a LinkedIn post using Gemini if available"""
        if context is None:
            context = self._get_business_context()

        # Use Gemini if API key is available
        if self.ai_client.api_key:
            prompt = f"""Generate a LinkedIn post about {topic or 'industry insights'}.
            Business Context: {json.dumps(context)}
            Structure with a hook, body, and call to action.
            Professional tone.
            """
            content = self.ai_client.generate_content(prompt)
            return {
                "platform": "linkedin",
                "content": content,
                "word_count": len(content.split()),
                "created_at": datetime.now().isoformat()
            }

        template = random.choice(self.content_templates["linkedin"])

        placeholders = {
            "{business_name}": context.get("business_name", "Your Business"),
            "{milestone}": "10x productivity improvement",
            "{impact}": "significant cost reduction",
            "{industry}": context.get("industry", "AI Automation"),
            "{experience}": "building autonomous agents",
            "{lesson1}": "Start with clear processes",
            "{lesson2}": "Measure everything",
            "{lesson3}": "Iterate constantly",
            "{lesson4}": "Keep humans in the loop",
            "{lesson5}": "Document everything",
            "{trend}": "agentic AI",
            "{insight}": "The future is autonomous collaboration"
        }

        content = template
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, value)

        return {
            "platform": "linkedin",
            "content": content,
            "word_count": len(content.split()),
            "created_at": datetime.now().isoformat()
        }

    def generate_instagram_post(self, context: Dict = None) -> Dict[str, Any]:
        """Generate Instagram content"""
        if context is None:
            context = self._get_business_context()

        template = random.choice(self.content_templates["instagram"])

        placeholders = {
            "{visual_description}": "Team celebrating a milestone",
            "{caption}": "Another successful deployment! 🎉",
            "{hashtag1}": "business",
            "{hashtag2}": "automation",
            "{hashtag3}": "success",
            "{story_hook}": "We almost gave up...",
            "{body}": "But then we discovered the power of systematic automation.",
            "{call_to_action}": "What's your automation story?",
            "{fact}": "AI can handle 80% of repetitive tasks",
            "{explanation}": "Freeing you to focus on what matters most."
        }

        content = template
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, value)

        return {
            "platform": "instagram",
            "content": content,
            "hashtags": re.findall(r'#\w+', content),
            "created_at": datetime.now().isoformat()
        }

    def generate_reddit_post(self, subreddit: str = None, context: Dict = None) -> Dict[str, Any]:
        """Generate a Reddit post"""
        if context is None:
            context = self._get_business_context()

        template = random.choice(self.content_templates["reddit"])

        placeholders = {
            "{industry}": context.get("industry", "automation"),
            "{achievement}": "automated 100+ workflows",
            "{story}": "After months of development, we've successfully deployed AI agents that handle everything from email processing to social media management.",
            "{challenge}": "scaling operations",
            "{business_name}": context.get("business_name", "Your Business"),
            "{approach}": "gradual automation",
            "{results}": "amazing outcomes",
            "{client_type}": "a startup",
            "{metric}": "productivity",
            "{percentage}": "300%",
            "{details}": "By implementing Claude Code agents, we reduced manual work from 40 hours/week to just 5 hours, allowing the team to focus on strategic initiatives."
        }

        content = template
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, value)

        return {
            "platform": "reddit",
            "content": content,
            "word_count": len(content.split()),
            "subreddit_suggestions": ["automation", "artificial", "Entrepreneur", "smallbusiness"],
            "created_at": datetime.now().isoformat()
        }

    def generate_weekly_content_batch(self, platforms: List[str] = None) -> Dict[str, List[Dict]]:
        """Generate content for all platforms for the week"""
        if platforms is None:
            platforms = ["twitter", "linkedin", "instagram", "reddit"]

        context = self._get_business_context()
        batch = {}

        for platform in platforms:
            batch[platform] = []

            # Generate 5 posts per platform for the week
            for i in range(5):
                if platform == "twitter":
                    post = self.generate_twitter_post(context=context)
                elif platform == "linkedin":
                    post = self.generate_linkedin_post(context=context)
                elif platform == "instagram":
                    post = self.generate_instagram_post(context=context)
                elif platform == "reddit":
                    post = self.generate_reddit_post(context=context)

                batch[platform].append(post)

        return batch

    def generate_whatsapp_message(self, topic: str = None, context: Dict = None) -> Dict[str, Any]:
        """Generate a WhatsApp update"""
        if context is None:
            context = self._get_business_context()

        # Use Gemini if available
        if self.ai_client.api_key:
            prompt = f"""Generate a short, professional WhatsApp update about {topic or 'business progress'}.
            Business Context: {json.dumps(context)}
            Keep it conversational and brief (under 50 words).
            Include 1-2 emojis.
            """
            content = self.ai_client.generate_content(prompt)
            return {
                "platform": "whatsapp",
                "content": content,
                "status": "ready"
            }

        # Fallback template
        return {
            "platform": "whatsapp",
            "content": f"🚀 Quick Update: {context.get('business_name')} just hit a new milestone! We're now automating workflows with AI. 🤖✨",
            "status": "ready"
        }

    def save_content_plan(self, batch: Dict[str, List[Dict]], filename: str = None):
        """Save content plan to file"""
        if filename is None:
            filename = f"Content_Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        filepath = self.vault_path / "Plans" / filename
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, 'w') as f:
            f.write(f"# Social Media Content Plan\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for platform, posts in batch.items():
                f.write(f"## {platform.capitalize()} Posts\n\n")

                for i, post in enumerate(posts, 1):
                    f.write(f"### Post {i}\n")
                    f.write(f"- **Schedule:** Day {i} of week\n")
                    f.write(f"- **Content:** {post['content']}\n")
                    f.write(f"- **Status:** ⏳ Pending\n\n")

                f.write("\n")

        return filepath


def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Social Media Content Generator')
    parser.add_argument('action', choices=[
        'generate_twitter_post',
        'generate_linkedin_post',
        'generate_instagram_post',
        'generate_reddit_post',
        'generate_weekly_batch',
        'generate_all_platforms',
        'generate_whatsapp_message'
    ], help='Action to perform')

    parser.add_argument('--platform', help='Specific platform')
    parser.add_argument('--topic', help='Content topic')
    parser.add_argument('--save', action='store_true', help='Save to file')

    args = parser.parse_args()

    generator = SocialContentGenerator()

    if args.action == 'generate_twitter_post':
        result = generator.generate_twitter_post(args.topic)

    elif args.action == 'generate_linkedin_post':
        result = generator.generate_linkedin_post(args.topic)

    elif args.action == 'generate_instagram_post':
        result = generator.generate_instagram_post()

    elif args.action == 'generate_reddit_post':
        result = generator.generate_reddit_post()

    elif args.action == 'generate_weekly_batch':
        result = generator.generate_weekly_content_batch()

        if args.save:
            filepath = generator.save_content_plan(result)
            print(f"\nContent plan saved to: {filepath}")

    elif args.action == 'generate_whatsapp_message':
        result = generator.generate_whatsapp_message(args.topic)

    print(json.dumps(result, indent=2, default=str))


if __name__ == '__main__':
    main()
