#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite
Verifies all connections (Odoo, Social Media, AI) and System Status
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("TestIntegrations")

# File logger
file_handler = logging.FileHandler('final_test_results.txt', mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)

def print_result(name, success, message=""):
    status = "PASS" if success else "FAIL"
    icon = "✅" if success else "❌"
    msg = f"{icon} {status} - {name}: {message}"
    print(msg)
    logger.info(msg)
    if not success:
        logger.error(f"FAILURE DETAILS for {name}: {message}")

async def test_odoo():
    print("\n--- Testing Odoo Integration ---")
    try:
        # from src.core.verify_odoo import get_odoo_client
        from xmlrpc import client
        
        url = os.getenv('ODOO_URL')
        db = os.getenv('ODOO_DB')
        username = os.getenv('ODOO_USERNAME')
        password = os.getenv('ODOO_PASSWORD')
        
        if not all([url, db, username, password]):
            print_result("Odoo Config", False, "Missing .env variables")
            return
            
        common = client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if uid:
            print_result("Odoo Authentication", True, f"Connected as UID {uid}")
            
            models = client.ServerProxy(f'{url}/xmlrpc/2/object')
            # Use simple search_count to verify read access
            count = models.execute_kw(db, uid, password, 'res.partner', 'search_count', [[]])
            print_result("Odoo Permissions", True, f"Found {count} partners")
        else:
            print_result("Odoo Authentication", False, "Login failed")
            
    except Exception as e:
        print_result("Odoo Connection", False, str(e))

async def test_openai():
    print("\n--- Testing AI Core (OpenAI) ---")
    try:
        from openai import OpenAI
        client = OpenAI()
        # Simple cheap call
        response = client.models.list()
        print_result("OpenAI Connection", True, f"Retrieved {len(response.data)} models")
    except Exception as e:
        print_result("OpenAI Connection", False, str(e))

async def test_folders():
    print("\n--- Testing Folder Structure ---")
    required_folders = [
        "src/core", "src/platforms", "src/generators", 
        "Approved", "Inbox", "Logs", "Needs_Action"
    ]
    
    root = Path(os.getcwd())
    for folder in required_folders:
        path = root / folder
        exists = path.exists()
        print_result(f"Folder: {folder}", exists, "Exists" if exists else "Missing")

def check_script_imports():
    print("\n--- Testing Script Imports ---")
    try:
        from src.core.workflow_orchestrator import WorkflowOrchestrator
        print_result("Import WorkflowOrchestrator", True)
    except Exception as e:
        print_result("Import WorkflowOrchestrator", False, str(e))
        
    try:
        from src.platforms.linkedin.linkedin_poster import LinkedInPoster
        print_result("Import LinkedInPoster", True)
    except Exception as e:
        print_result("Import LinkedInPoster", False, str(e))

    try:
        from src.platforms.facebook.facebook_poster import FacebookPoster
        print_result("Import FacebookPoster", True)
    except Exception as e:
        print_result("Import FacebookPoster", False, str(e))

def check_env_vars():
    print("\n--- Testing Environment Variables ---")
    vars = [
        "ODOO_URL", "ODOO_DB", "ODOO_USERNAME", "ODOO_PASSWORD",
        "FACEBOOK_EMAIL", "FACEBOOK_PASSWORD",
        "LINKEDIN_EMAIL", "LINKEDIN_PASSWORD" # Optional but good to check
    ]
    for var in vars:
        val = os.getenv(var)
        status = "✅ Set" if val else "⚠️ Missing"
        print(f"{var}: {status}")

async def main():
    print("🚀 STARTING FINAL SYSTEM INTEGRATION TEST")
    load_dotenv()
    
    # 1. Check Folders
    await test_folders()
    
    # 2. Check Scripts
    check_script_imports()

    # 2.5 Check Env Vars
    check_env_vars()
    
    # 3. Check Odoo
    await test_odoo()
    
    # 4. Check AI
    await test_openai()
    
    print("\n-------------------------------------------")
    print("Tests Completed. Review any failures above.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest cancelled.")
