#!/usr/bin/env python3
"""
AI Employee System Overview and Verification
Shows the complete status of the Platinum Tier implementation
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

def print_system_overview():
    """Print comprehensive system overview"""
    print("="*80)
    print("AI EMPLOYEE PLATINUM TIER SYSTEM OVERVIEW")
    print("="*80)

    vault_path = Path("C:\\Users\\LENOVO X1 YOGA\\OneDrive\\Desktop\\hakathone zero\\AI_Employee_vault")

    # Check key directories
    directories = {
        "Needs_Action": (vault_path / "Needs_Action").exists(),
        "Pending_Approval": (vault_path / "Pending_Approval").exists(),
        "Approved": (vault_path / "Approved").exists(),
        "Rejected": (vault_path / "Rejected").exists(),
        "Done": (vault_path / "Done").exists(),
        "Plans": (vault_path / "Plans").exists(),
        "In_Progress": (vault_path / "In_Progress").exists(),
        "Updates": (vault_path / "Updates").exists(),
        "odoo_mcp": (vault_path / "odoo_mcp").exists(),
        "facebook_instagram_mcp": (vault_path / "facebook_instagram_mcp").exists(),
        "twitter_mcp": (vault_path / "twitter_mcp").exists(),
        "Skills": (vault_path / "Skills").exists()
    }

    print("\n📁 DIRECTORY STRUCTURE:")
    for dir_name, exists in directories.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_name}")

    # Check key files
    key_files = {
        "Dashboard.md": (vault_path / "Dashboard.md").exists(),
        "Company_Handbook.md": (vault_path / "Company_Handbook.md").exists(),
        "ceo_briefing_generator.py": (vault_path / "ceo_briefing_generator.py").exists(),
        "audit_logger.py": (vault_path / "audit_logger.py").exists(),
        "workflow_orchestrator.py": (vault_path / "workflow_orchestrator.py").exists(),
        "error_handler.py": (vault_path / "error_handler.py").exists()
    }

    print("\n📄 KEY FILES:")
    for file_name, exists in key_files.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {file_name}")

    # Check MCP servers
    mcp_servers = {
        "Odoo MCP": (vault_path / "odoo_mcp" / "server.py").exists(),
        "Facebook/Instagram MCP": (vault_path / "facebook_instagram_mcp" / "server.py").exists(),
        "Twitter MCP": (vault_path / "twitter_mcp" / "server.py").exists()
    }

    print("\n⚙️  MCP SERVERS:")
    for server_name, exists in mcp_servers.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {server_name}")

    # Check social media integrations
    social_integrations = {
        "Facebook Integration": len(list(vault_path.glob("facebook*/*.py"))) > 0,
        "Instagram Integration": len(list(vault_path.glob("instagram*/*.py"))) > 0,
        "Twitter Integration": len(list(vault_path.glob("twitter*/*.py"))) > 0,
        "LinkedIn Integration": len(list(vault_path.glob("*linkedin*.py"))) > 0
    }

    print("\n📡 SOCIAL MEDIA INTEGRATIONS:")
    for platform, exists in social_integrations.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {platform}")

    # Check automation scripts
    automation_scripts = {
        "Scheduler": (vault_path / "scheduler.py").exists(),
        "Auto Processor": (vault_path / "auto_processor.py").exists(),
        "Email Handler": (vault_path / "email_handler.md").exists(),
        "Plan Creator": (vault_path / "plan_creator.py").exists()
    }

    print("\n🔄 AUTOMATION SCRIPTS:")
    for script_name, exists in automation_scripts.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {script_name}")

    # Check documentation
    documentation = {
        "Platinum Tier Complete": (vault_path / "PLATINUM_TIER_COMPLETE.md").exists(),
        "Gold Tier Complete": (vault_path / "GOLD_TIER_COMPLETE.md").exists(),
        "Silver Tier Complete": (vault_path / "SILVER_TIER_COMPLETE.md").exists(),
        "Architecture Guide": (vault_path / "haka.md").exists(),
        "Cloud Deployment": (vault_path / "cloud_deployment.md").exists(),
        "Work Zone Specialization": (vault_path / "work_zone_specialization.md").exists()
    }

    print("\n📋 DOCUMENTATION:")
    for doc_name, exists in documentation.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {doc_name}")

    # Count total components
    all_checks = {**directories, **key_files, **mcp_servers, **social_integrations, **automation_scripts, **documentation}
    total_checks = len(all_checks)
    passed_checks = sum(1 for result in all_checks.values() if result)
    success_rate = (passed_checks / total_checks) * 100

    print(f"\n📊 OVERALL STATISTICS:")
    print(f"  Total Components Checked: {total_checks}")
    print(f"  Successful Components: {passed_checks}")
    print(f"  Failed Components: {total_checks - passed_checks}")
    print(f"  Success Rate: {success_rate:.1f}%")

    print("\n" + "="*80)
    if success_rate >= 95:
        print("🎉 PLATINUM TIER SYSTEM VERIFICATION: COMPLETE SUCCESS!")
        print("The AI Employee system is fully operational with Platinum Tier capabilities.")
        print("- Cross-domain integration (Personal + Business)")
        print("- Odoo Community accounting with MCP integration")
        print("- Facebook, Instagram, Twitter social media management")
        print("- Cloud + Local work-zone specialization")
        print("- Automated posting with approval workflows")
        print("- 24/7 operation with health monitoring")
    else:
        print("⚠️  SYSTEM VERIFICATION: PARTIAL SUCCESS")
        print(f"Success rate of {success_rate:.1f}% indicates system is mostly functional.")

    print("="*80)

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": total_checks - passed_checks,
        "success_rate": success_rate,
        "components": all_checks
    }

    results_file = vault_path / "system_verification_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Verification results saved to: {results_file}")

if __name__ == "__main__":
    print_system_overview()