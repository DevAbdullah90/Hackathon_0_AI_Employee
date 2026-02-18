#!/usr/bin/env python3
"""
Reddit Content Generator
Creates Reddit posts and comments for business engagement
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
from gemini_client import GeminiClient

try:
    import praw
except ImportError:
    print("Installing praw...")
    os.system("pip install praw")
    import praw

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedditContentGenerator:
    """Generates Reddit content for business engagement"""

    def __init__(self, vault_path: str = None):
        if vault_path is None:
            self.vault_path = Path("C:\\Users\\hp\\OneDrive\\Desktop\\Hackathon_AI_Employee")
        else:
            self.vault_path = Path(vault_path)
        self.reddit_posts = self.vault_path / 'Reddit_Posts'
        self.reddit_comments = self.vault_path / 'Reddit_Comments'
        self.reddit_posts.mkdir(exist_ok=True)
        self.reddit_comments.mkdir(exist_ok=True)

        # Initialize Reddit API
        self.reddit = None
        self._initialize_api()

        # Content templates
        self.post_templates = self._load_post_templates()
        self.comment_templates = self._load_comment_templates()
        self.ai_client = GeminiClient()

    def _initialize_api(self):
        """Initialize Reddit API client"""
        try:
            client_id = os.environ.get('REDDIT_CLIENT_ID')
            client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
            user_agent = os.environ.get('REDDIT_USER_AGENT', 'AI Employee Bot v1.0')
            username = os.environ.get('REDDIT_USERNAME')
            password = os.environ.get('REDDIT_PASSWORD')

            if not all([client_id, client_secret, username, password]):
                logger.warning("Reddit credentials not fully configured")
                return

            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                username=username,
                password=password
            )

            user = self.reddit.user.me()
            logger.info(f"Reddit API authenticated as: {user.name}")

        except Exception as e:
            logger.error(f"Error initializing Reddit API: {e}")

    def _load_post_templates(self) -> Dict[str, List[str]]:
        """Load Reddit post templates"""
        return {
            'case_study': [
                "[Case Study] How we helped {client_type} increase {metric} by {percentage}\n\n"
                "{story_intro}\n\n"
                "The Challenge:\n"
                "{challenge_description}\n\n"
                "Our Approach:\n"
                "{approach_description}\n\n"
                "Results:\n"
                "{results_description}\n\n"
                "Key Takeaways:\n"
                "{takeaway_1}\n"
                "{takeaway_2}\n\n"
                "AMA about our approach!\n\n"
                "---\n\n"
                "*We're {business_name}, and we help {target_audience}.*",

                "I just finished a project that {result} - here's what I learned\n\n"
                "Hi r/{subreddit}, I'm {name} from {business_name}.\n\n"
                "We recently worked with {client_name} who {problem_description}.\n\n"
                "Here's what worked:\n"
                "{what_worked}\n\n"
                "Here's what didn't:\n"
                "{what_didnt_work}\n\n"
                "My biggest lesson:\n"
                "{big_lesson}\n\n"
                "Happy to answer questions about {topic}!"
            ],
            'tips': [
                "{number} tips for {audience} that {desire} (from {experience})\n\n"
                "Hey r/{subreddit},\n\n"
                "I've been {experience_description} for {timeframe}.\n\n"
                "Here are my top {number} tips:\n\n"
                "{tip_list}\n\n"
                "What would you add to this list?\n\n"
                "---\n\n"
                "*Context: {additional_context}*",

                "The {number} biggest mistakes I see {target_audience} make (and how to avoid them)\n\n"
                "As someone who {credentials}, I see the same mistakes over and over.\n\n"
                "Here they are:\n\n"
                "{mistake_list}\n\n"
                "Avoid these and you'll {benefit}.\n\n"
                "What's a mistake you made that others could learn from?"
            ],
            'question': [
                "How do you handle {challenge} in {context}?\n\n"
                "I'm curious how other {professionals} approach this.\n\n"
                "At {business_name}, we've tried {approach} with {results}.\n\n"
                "But I'm always looking to improve.\n\n"
                "What's working for you?\n\n"
                "---\n\n"
                "*Context: We're {background}*",

                "{question}? (Research for {purpose})\n\n"
                "I'm working on {project} and could use your input.\n\n"
                "Specifically, I'm trying to understand:\n"
                "{specific_question_1}\n"
                "{specific_question_2}\n\n"
                "Any insights would be appreciated!\n\n"
                "---\n\n"
                "*Why I'm asking: {reason}*"
            ],
            'discussion': [
                "Does anyone else {experience} or is it just me?\n\n"
                "I've noticed that {observation} and I'm wondering if others see this too.\n\n"
                "For example: {example}\n\n"
                "Am I alone in this experience?\n\n"
                "How do you handle it?\n\n"
                "---\n\n"
                "*Background: {business_context}*",

                "Unpopular opinion: {opinion}\n\n"
                "I know this goes against conventional wisdom, but here's why I think this:\n\n"
                "{reasoning}\n\n"
                "In my experience working with {audience}, {observation}.\n\n"
                "I'd love to hear your thoughts. Change my mind!\n\n"
                "---\n\n"
                "*Disclaimer: {disclaimer}*"
            ]
        }

    def _load_comment_templates(self) -> Dict[str, List[str]]:
        """Load Reddit comment templates"""
        return {
            'helpful': [
                "This is a great point. In my experience, {experience}.\n\n"
                "One thing that worked for me was {solution}.\n\n"
                "Have you considered trying {suggestion}?\n\n"
                "Happy to share more details if you're interested.",

                "I had a similar challenge with {situation}.\n\n"
                "What worked for me: {approach}.\n\n"
                "The key insight was {insight}.\n\n"
                "Hope this helps!"
            ],
            'question': [
                "Interesting perspective. Can you elaborate on {topic}?\n\n"
                "Specifically, I'm curious about:\n"
                "- {question_1}\n"
                "- {question_2}\n\n"
                "This is relevant to me because {reason}.",

                "Thanks for sharing this. Have you tried {alternative_approach}?\n\n"
                "I'm asking because {context}.\n\n"
                "What were your results with {previous_approach}?"
            ],
            'appreciation': [
                "Thanks for sharing this! I found {aspect} particularly valuable.\n\n"
                "I'm going to implement {takeaway} in my own work.\n\n"
                "Looking forward to more insights from you.",

                "This is really well explained. The part about {detail} really resonated with me.\n\n"
                "Saved this comment for future reference!"
            ],
            'collaborative': [
                "This is fascinating. Have you looked into {resource} by {author}?\n\n"
                "It covers similar ground from {perspective} angle.\n\n"
                "Would be interesting to compare notes.",

                "I'm working on something similar at {business_name}.\n\n"
                "Would you be open to a brief conversation about {topic}?\n\n"
                "I think there's potential for {collaboration_opportunity}."
            ]
        }

    def _get_business_context(self) -> Dict[str, Any]:
        """Get business context from vault files"""
        context = {
            'business_name': 'AI Employee Solutions',
            'target_audience': 'business owners',
            'industry': 'AI automation',
            'name': 'Your Name',
            'subreddit': 'smallbusiness',
            'credentials': 'work with businesses daily'
        }

        # Try to load from Company_Handbook.md
        handbook = self.vault_path / 'Company_Handbook.md'
        if handbook.exists():
            try:
                content = handbook.read_text(encoding='utf-8')

                # Extract business name
                match = re.search(r'Company Name:\s*(.+)', content)
                if match:
                    context['business_name'] = match.group(1).strip()
            except Exception:
                pass

        return context

    def generate_reddit_post(self, post_type: str = 'tips', subreddit: str = 'smallbusiness') -> Dict[str, Any]:
        """Generate a Reddit post using Gemini if available"""
        try:
            context = self._get_business_context()
            
            # Use Gemini if API key is available
            if self.ai_client.api_key:
                prompt = f"""Generate a Reddit post for r/{subreddit}.
                Post Type: {post_type}
                Business Context: {json.dumps(context)}
                Return Valid JSON with 'title' and 'content' fields.
                Make it look authentic and not promotional.
                """
                result = self.ai_client.generate_structured_json(prompt)
                if 'title' in result and 'content' in result:
                    return {
                        'platform': 'reddit',
                        'post_type': post_type,
                        'subreddit': subreddit,
                        'title': result['title'],
                        'content': result['content'],
                        'created': datetime.now().isoformat(),
                        'status': 'draft',
                        'character_count': len(result['content'])
                    }

            # Fallback to templates
            templates = self.post_templates.get(post_type, self.post_templates['tips'])
            template = random.choice(templates)

            # Fill context specific to post type
            if post_type == 'case_study':
                context.update({
                    'client_type': 'small business',
                    'metric': 'productivity',
                    'percentage': '40%',
                    'story_intro': 'I wanted to share a recent success story...',
                    'challenge_description': 'They were spending too much time on manual tasks.',
                    'approach_description': 'We implemented AI-powered automation.',
                    'results_description': 'Reduced manual work by 60% in 3 months.',
                    'takeaway_1': 'Start small - automate one task at a time.',
                    'takeaway_2': 'Measure everything to track ROI.',
                    'subreddit': subreddit
                })

            elif post_type == 'tips':
                context.update({
                    'number': '5',
                    'audience': 'small business owners',
                    'desire': 'want to automate repetitive tasks',
                    'experience': '5 years of automation consulting',
                    'experience_description': 'building automation systems for small businesses',
                    'timeframe': '5 years',
                    'tip_list': '1. Start with repetitive tasks\n2. Document processes first\n3. Test thoroughly\n4. Train your team\n5. Monitor and optimize',
                    'additional_context': 'I run an AI automation consultancy helping businesses save 10+ hours/week.',
                    'subreddit': subreddit,
                    'mistake_list': '1. Automating broken processes\n2. Not documenting workflows\n3. Skipping user training\n4. Trying to automate everything at once',
                    'benefit': 'see immediate time savings',
                    'credentials': 'automates business processes',
                    'target_audience': 'small business owners'
                })

            elif post_type == 'question':
                context.update({
                    'challenge': 'client onboarding',
                    'context': 'client onboarding',
                    'professionals': 'consultants',
                    'business_name': context['business_name'],
                    'approach': 'automated welcome sequences with personal check-ins',
                    'results': 'mixed results - some clients love it, others want more personal touch',
                    'question': 'How do you balance automation with personal touch',
                    'purpose': 'improving our client experience',
                    'project': 'our client onboarding process',
                    'specific_question_1': 'What automation tools do you use?',
                    'specific_question_2': 'How do you maintain personal connection?',
                    'reason': 'we want to improve our client experience',
                    'subreddit': subreddit
                })

            elif post_type == 'discussion':
                context.update({
                    'experience': 'feel like LinkedIn is getting less valuable for B2B',
                    'observation': 'engagement is dropping while spam is increasing',
                    'example': 'My posts used to get 1000+ views, now lucky to get 200',
                    'business_context': 'I use LinkedIn for B2B lead generation',
                    'opinion': 'LinkedIn is dying for B2B lead generation',
                    'reasoning': 'The algorithm changes and increased spam have killed organic reach.',
                    'audience': 'B2B professionals',
                    'disclaimer': 'This is based on my recent experience. Your mileage may vary.'
                })

            content = template.format(**context)

            return {
                'platform': 'reddit',
                'post_type': post_type,
                'subreddit': subreddit,
                'title': self._extract_title(content),
                'content': content,
                'created': datetime.now().isoformat(),
                'status': 'draft',
                'character_count': len(content)
            }

        except Exception as e:
            logger.error(f"Error generating Reddit post: {e}")
            return self._get_default_post()

    def generate_reddit_comment(self, comment_type: str = 'helpful') -> Dict[str, Any]:
        """Generate a Reddit comment"""
        try:
            templates = self.comment_templates.get(comment_type, self.comment_templates['helpful'])
            template = random.choice(templates)
            context = self._get_business_context()

            # Fill context specific to comment type
            if comment_type == 'helpful':
                context.update({
                    'experience': 'automating 50+ business processes',
                    'solution': 'starting with task documentation',
                    'suggestion': 'creating process maps before automating',
                    'situation': 'automating our invoicing process',
                    'approach': 'breaking it down into 5 small steps',
                    'insight': 'automating the wrong process just makes you fail faster'
                })

            elif comment_type == 'question':
                context.update({
                    'topic': 'your implementation timeline',
                    'question_1': 'How long did implementation take?',
                    'question_2': 'What was the biggest obstacle?',
                    'reason': 'we are planning a similar project',
                    'alternative_approach': 'hiring a consultant to guide you',
                    'context': 'my team is considering similar automation',
                    'previous_approach': 'the DIY approach'
                })

            elif comment_type == 'appreciation':
                context.update({
                    'aspect': 'your point about starting small',
                    'takeaway': 'your "start with one process" advice',
                    'detail': 'how you emphasized measuring before optimizing'
                })

            elif comment_type == 'collaborative':
                context.update({
                    'resource': 'The E-Myth Revisited',
                    'author': 'Michael Gerber',
                    'perspective': 'the systems-thinking',
                    'business_name': context['business_name'],
                    'topic': 'our automation challenges',
                    'collaboration_opportunity': 'knowledge sharing'
                })

            content = template.format(**context)

            return {
                'platform': 'reddit',
                'comment_type': comment_type,
                'content': content,
                'created': datetime.now().isoformat(),
                'status': 'draft',
                'character_count': len(content)
            }

        except Exception as e:
            logger.error(f"Error generating Reddit comment: {e}")
            return self._get_default_comment()

    def _extract_title(self, content: str) -> str:
        """Extract title from post content (first line)"""
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('---'):
                # Reddit titles max at 300 characters
                return line.strip()[:300]
        return "Business Automation Insights"

    def _get_default_post(self) -> Dict[str, Any]:
        """Default post if generation fails"""
        return {
            'platform': 'reddit',
            'post_type': 'tips',
            'subreddit': 'smallbusiness',
            'title': '5 automation tips for busy business owners',
            'content': 'I help businesses automate repetitive tasks. Here are my top 5 tips...',
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'character_count': 100
        }

    def _get_default_comment(self) -> Dict[str, Any]:
        """Default comment if generation fails"""
        return {
            'platform': 'reddit',
            'comment_type': 'helpful',
            'content': 'Thanks for sharing this. In my experience with automation, starting small is key.',
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'character_count': 120
        }

    def generate_weekly_posts(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate a week's worth of Reddit posts"""
        posts = []
        post_types = ['case_study', 'tips', 'question', 'discussion']
        subreddits = ['smallbusiness', 'Entrepreneur', 'business', 'automation']

        for _ in range(count):
            post_type = random.choice(post_types)
            subreddit = random.choice(subreddits)
            post = self.generate_reddit_post(post_type, subreddit)
            posts.append(post)

        return posts

    def save_post(self, post: Dict[str, Any], filename: str = None) -> Path:
        """Save post to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                post_type = post['post_type']
                filename = f"reddit_{post_type}_{timestamp}.md"

            filepath = self.reddit_posts / filename

            # Save post with metadata
            header = f"""---
type: reddit_post
post_type: {post['post_type']}
subreddit: {post['subreddit']}
title: {post['title']}
created: {post['created']}
status: {post['status']}
character_count: {post['character_count']}
---

# {post['title']}

**Subreddit**: r/{post['subreddit']}
**Type**: {post['post_type']}
**Character Count**: {post['character_count']}

---

"""

            full_content = header + post['content']
            filepath.write_text(full_content)

            logger.info(f"Saved Reddit post to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving post: {e}")
            return None

    def save_comment(self, comment: Dict[str, Any], context_post: str = None, filename: str = None) -> Path:
        """Save comment to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                comment_type = comment['comment_type']
                filename = f"reddit_comment_{comment_type}_{timestamp}.md"

            filepath = self.reddit_comments / filename

            # Save comment with metadata
            header = f"""---
type: reddit_comment
comment_type: {comment['comment_type']}
created: {comment['created']}
status: {comment['status']}
character_count: {comment['character_count']}
{('context_post: ' + context_post) if context_post else ''}
---

# Reddit Comment ({comment['comment_type']})

**Type**: {comment['comment_type']}
**Character Count**: {comment['character_count']}

---

"""

            full_content = header + comment['content']
            filepath.write_text(full_content)

            logger.info(f"Saved Reddit comment to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving comment: {e}")
            return None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Reddit Content Generator')
    parser.add_argument('--vault', type=str, help='Path to vault', default=None)
    parser.add_argument('--type', type=str,
                       choices=['post', 'comment', 'batch'],
                       default='post', help='Content type to generate')
    parser.add_argument('--post-type', type=str,
                       choices=['case_study', 'tips', 'question', 'discussion'],
                       default='tips', help='Reddit post type')
    parser.add_argument('--comment-type', type=str,
                       choices=['helpful', 'question', 'appreciation', 'collaborative'],
                       default='helpful', help='Comment type')
    parser.add_argument('--subreddit', type=str, default='smallbusiness',
                       help='Target subreddit')
    parser.add_argument('--count', type=int, default=3,
                       help='Number of posts/comments to generate')

    args = parser.parse_args()

    vault_path = args.vault or r"C:\Users\LENOVO X1 YOGA\Desktop\hakathone zero\AI_Employee_Vault"
    generator = RedditContentGenerator(vault_path)

    if args.type == 'post':
        post = generator.generate_reddit_post(args.post_type, args.subreddit)
        filepath = generator.save_post(post)
        print(f"Generated Reddit post: {filepath}")

    elif args.type == 'comment':
        comment = generator.generate_reddit_comment(args.comment_type)
        filepath = generator.save_comment(comment)
        print(f"Generated Reddit comment: {filepath}")

    elif args.type == 'batch':
        posts = generator.generate_weekly_posts(args.count)
        for post in posts:
            filepath = generator.save_post(post)
            print(f"Generated: {filepath}")


if __name__ == "__main__":
    main()
