import os
from pathlib import Path
from datetime import datetime

def create_validation_posts():
    """
    Creates validation posts in the 'Approved' folder to trigger immediate posting.
    """
    vault_path = Path(os.getcwd())
    approved_folder = vault_path / 'Approved'
    approved_folder.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Create Twitter Validation Post
    twitter_file = approved_folder / f"VALIDATION_TWITTER_{timestamp}.md"
    twitter_content = f"""---
type: twitter_post
status: approved
created: {datetime.now().isoformat()}
---
## Post Content
🤖 AI Employee System Verification
Timestamp: {timestamp}
Status: Online & Operational 🚀
#AI #Automation #SystemCheck
"""
    twitter_file.write_text(twitter_content, encoding='utf-8')
    print(f"Created Twitter validation post: {twitter_file.name}")
    
    # 2. Create LinkedIn Validation Post
    linkedin_file = approved_folder / f"VALIDATION_LINKEDIN_{timestamp}.md"
    linkedin_content = f"""---
type: linkedin_post
status: approved
created: {datetime.now().isoformat()}
---
## Post Content
🤖 **System Verification Protocol**

The AI Employee system is currently performing a self-test of its social media integration capabilities.

✅ Status: Operational
🕒 Timestamp: {timestamp}
🚀 Mode: Gold Tier Automation

This post confirms that the LinkedIn integration is correctly configured and active.

#AI #Automation #FutureIsNow #SystemCheck #TechInnovation
"""
    linkedin_file.write_text(linkedin_content, encoding='utf-8')
    print(f"Created LinkedIn validation post: {linkedin_file.name}")
    
    print("\n✅ Verification posts created in 'Approved' folder.")
    print("👉 If the system is running, it should process and post these immediately.")
    print("   Check your LinkedIn and Twitter profiles in a moment!")

if __name__ == "__main__":
    create_validation_posts()
