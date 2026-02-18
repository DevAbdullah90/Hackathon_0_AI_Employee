#!/usr/bin/env python3
"""
Activate Social Media MCP Servers
Connect the MCP servers to actual social media platforms using credentials
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SocialMCPActivator:
    """Activate MCP servers to connect to real social media platforms"""

    def __init__(self):
        self.vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\OneDrive\\Desktop\\hakathone zero\\AI_Employee_vault")
        self.env_path = self.vault_path / ".env"

    def check_environment_variables(self):
        """Check if environment variables exist for social media credentials"""
        logger.info("🔍 Checking environment variables for social media credentials...")

        required_vars = {
            'FACEBOOK_ACCESS_TOKEN': 'Facebook API Token',
            'INSTAGRAM_USERNAME': 'Instagram Username',
            'INSTAGRAM_PASSWORD': 'Instagram Password',
            'TWITTER_BEARER_TOKEN': 'Twitter Bearer Token',
            'TWITTER_API_KEY': 'Twitter API Key',
            'TWITTER_API_SECRET': 'Twitter API Secret',
            'TWITTER_ACCESS_TOKEN': 'Twitter Access Token',
            'TWITTER_ACCESS_TOKEN_SECRET': 'Twitter Access Token Secret',
            'LINKEDIN_ACCESS_TOKEN': 'LinkedIn Access Token',
            'LINKEDIN_PAGE_ID': 'LinkedIn Page ID'
        }

        found_vars = {}
        missing_vars = {}

        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if value and value.strip():
                found_vars[var_name] = value
                logger.info(f"✅ Found {description}: {var_name}")
            else:
                missing_vars[var_name] = description

        logger.info(f"\n📊 Environment Variables Summary:")
        logger.info(f"   Found: {len(found_vars)}")
        logger.info(f"   Missing: {len(missing_vars)}")

        if missing_vars:
            logger.warning(f"⚠️  Missing required environment variables:")
            for var_name, description in missing_vars.items():
                logger.warning(f"   - {var_name}: {description}")
            logger.warning(f"\nPlease add these to your .env file")

        return found_vars, missing_vars

    def create_mcp_configurations(self):
        """Create MCP server configurations"""
        logger.info("\n🔧 Creating MCP Server Configurations...")

        # Odoo MCP configuration
        odoo_config = {
            "servers": [
                {
                    "name": "odoo",
                    "command": "python",
                    "args": [str(self.vault_path / "odoo_mcp" / "server.py")],
                    "env": {
                        "ODOO_URL": os.getenv("ODOO_URL", "http://localhost:8069"),
                        "ODOO_DB": os.getenv("ODOO_DB", "odoo_db"),
                        "ODOO_USERNAME": os.getenv("ODOO_USERNAME", "admin"),
                        "ODOO_PASSWORD": os.getenv("ODOO_PASSWORD", "password")
                    }
                }
            ]
        }

        # Facebook/Instagram MCP configuration
        fb_ig_config = {
            "servers": [
                {
                    "name": "facebook-instagram",
                    "command": "python",
                    "args": [str(self.vault_path / "facebook_instagram_mcp" / "server.py")],
                    "env": {
                        "FACEBOOK_ACCESS_TOKEN": os.getenv("FACEBOOK_ACCESS_TOKEN", ""),
                        "INSTAGRAM_USERNAME": os.getenv("INSTAGRAM_USERNAME", ""),
                        "INSTAGRAM_PASSWORD": os.getenv("INSTAGRAM_PASSWORD", "")
                    }
                }
            ]
        }

        # Twitter MCP configuration
        twitter_config = {
            "servers": [
                {
                    "name": "twitter",
                    "command": "python",
                    "args": [str(self.vault_path / "twitter_mcp" / "server.py")],
                    "env": {
                        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN", ""),
                        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY", ""),
                        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET", ""),
                        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN", ""),
                        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
                        "TWITTER_USERNAME": os.getenv("TWITTER_USERNAME", "")
                    }
                }
            ]
        }

        # Claude Code MCP configuration file
        mcp_config_path = Path.home() / ".config" / "claude-code" / "mcp.json"
        mcp_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Aggregate all configurations
        full_config = {
            "servers": []
        }

        # Add odoo server if it exists
        if (self.vault_path / "odoo_mcp" / "server.py").exists():
            full_config["servers"].append(odoo_config["servers"][0])

        # Add facebook-instagram server if it exists
        if (self.vault_path / "facebook_instagram_mcp" / "server.py").exists():
            full_config["servers"].append(fb_ig_config["servers"][0])

        # Add twitter server if it exists
        if (self.vault_path / "twitter_mcp" / "server.py").exists():
            full_config["servers"].append(twitter_config["servers"][0])

        # Save the configuration
        with open(mcp_config_path, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2)

        logger.info(f"✅ MCP configuration saved to: {mcp_config_path}")
        logger.info(f"   Configured {len(full_config['servers'])} MCP servers")

        return mcp_config_path

    def create_sample_dotenv(self):
        """Create a sample .env file with placeholder values"""
        logger.info("\n📝 Creating sample .env file...")

        env_content = """# AI Employee Social Media Credentials
# Fill in your actual credentials here

# Facebook API Credentials
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here

# Instagram API Credentials (using same as Facebook for basic access)
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# Twitter/X API Credentials
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_USERNAME=your_twitter_username

# LinkedIn API Credentials
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PAGE_ID=your_linkedin_page_id

# Odoo Community Credentials
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Health Monitoring
HEALTH_CHECK_PORT=8080
LOG_LEVEL=INFO
"""

        env_file = self.vault_path / ".env"
        if not env_file.exists():
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            logger.info(f"✅ Sample .env file created: {env_file}")
        else:
            logger.info(f"ℹ️  .env file already exists: {env_file}")

        return env_file

    def activate_mcp_servers(self):
        """Provide instructions to activate MCP servers"""
        logger.info("\n🚀 ACTIVATION INSTRUCTIONS:")
        logger.info("="*60)
        logger.info("To activate real posting to social platforms:")
        logger.info("="*60)
        logger.info("\n1. 📝 UPDATE YOUR CREDENTIALS:")
        logger.info("   - Edit the .env file with your actual API credentials")
        logger.info("   - Get API tokens from respective platforms:")
        logger.info("     • Facebook: https://developers.facebook.com/")
        logger.info("     • Instagram: https://developers.facebook.com/")
        logger.info("     • Twitter: https://developer.twitter.com/")
        logger.info("     • LinkedIn: https://docs.microsoft.com/en-us/linkedin/")

        logger.info("\n2. ⚙️  START MCP SERVERS:")
        logger.info("   Run these commands in separate terminals:")
        logger.info("   python odoo_mcp/server.py")
        logger.info("   python facebook_instagram_mcp/server.py")
        logger.info("   python twitter_mcp/server.py")

        logger.info("\n3. 🤖 START CLAUDE CODE:")
        logger.info("   Launch Claude Code pointing to your vault")
        logger.info("   Claude will automatically connect to MCP servers")

        logger.info("\n4. 🔄 PROCESS EXISTING POSTS:")
        logger.info("   The posts created earlier will now be processed")
        logger.info("   with real API calls to publish to social platforms")

        logger.info("\n5. 📊 MONITOR POSTING:")
        logger.info("   Check the Done folder for successfully posted content")
        logger.info("   Monitor logs for any errors or issues")

        logger.info("\n💡 TIPS:")
        logger.info("   - Start with test posts to verify connections")
        logger.info("   - Monitor API rate limits")
        logger.info("   - Check platform-specific posting requirements")
        logger.info("   - Have backup credentials ready")

        logger.info("="*60)

    def run_activation(self):
        """Run the full activation process"""
        logger.info("🚀 INITIATING SOCIAL MCP SERVER ACTIVATION")
        logger.info("="*60)

        # Step 1: Check environment variables
        found_vars, missing_vars = self.check_environment_variables()

        # Step 2: Create sample .env if needed
        self.create_sample_dotenv()

        # Step 3: Create MCP configurations
        mcp_config_path = self.create_mcp_configurations()

        # Step 4: Provide activation instructions
        self.activate_mcp_servers()

        logger.info("\n✅ ACTIVATION SETUP COMPLETED!")
        logger.info("The MCP servers are configured and ready for activation.")
        logger.info("Please follow the instructions above to complete the setup.")

        return len(missing_vars) == 0  # Return True if no critical vars missing


def main():
    """Main function to activate social MCP servers"""
    logger.info("Initializing Social MCP Server Activator...")

    activator = SocialMCPActivator()
    success = activator.run_activation()

    if success:
        logger.info("\n🎉 MCP SERVERS READY FOR ACTIVATION!")
        logger.info("All configurations are in place. Follow the instructions to activate real posting.")
    else:
        logger.info("\n⚠️  MCP SERVERS NEED CONFIGURATION")
        logger.info("Please add your credentials to the .env file and restart the servers.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)