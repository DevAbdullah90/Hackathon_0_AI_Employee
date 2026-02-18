import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SystemReset")

def reset_directories():
    """
    Clears all data from processing directories while checking for system files.
    """
    base_path = Path(os.getcwd())
    
    # List of directories to clean
    # These contain generated data, logs, or processed queues
    dirs_to_clean = [
        "Logs",
        "Done",
        "Failed",
        "Plans",
        "Reports",
        "Reddit_Posts",
        "Reddit_Data",
        "Reddit_Comments",
        "LinkedIn_Posts",
        "Pending_Approval",
        "Needs_Action",
        "Approved",
        "Inbox",
        "linkedin_session",
        "whatsapp_session",
        "instagram_session"
    ]

    logger.info("=" * 60)
    logger.info("⚠  STARTING SYSTEM DATA RESET  ⚠")
    logger.info("=" * 60)
    logger.info("This will delete all generated posts, logs, and queue files.")
    logger.info("System scripts and configurations will be preserved.")
    logger.info("-" * 60)

    for dir_name in dirs_to_clean:
        dir_path = base_path / dir_name
        
        if not dir_path.exists():
            logger.info(f"Skipping {dir_name} (Not found)")
            continue
            
        logger.info(f"Cleaning {dir_name}...")
        
        # Special handling for session directories - try to remove the whole tree first
        if "session" in dir_name.lower():
             try:
                 shutil.rmtree(dir_path)
                 logger.info(f"  ✔ Completely removed session directory: {dir_name}")
                 continue # Skip file iteration since dir is gone
             except Exception as e:
                 logger.warning(f"  ⚠ Could not remove session dir {dir_name} at once: {e}. Trying file-by-file...")

        # Iterate over all files in the directory
        files_deleted = 0
        for file_path in dir_path.glob("*"):
            if file_path.is_file():
                # Skip .gitkeep files if they exist
                if file_path.name == ".gitkeep":
                    continue
                
                try:
                    file_path.unlink()
                    files_deleted += 1
                except Exception as e:
                    logger.error(f"  ❌ Failed to delete {file_path.name}: {e}")
            elif file_path.is_dir():
                try:
                    shutil.rmtree(file_path)
                    files_deleted += 1
                except Exception as e:
                    logger.error(f"  ❌ Failed to delete directory {file_path.name}: {e}")
        
        if files_deleted > 0:
            logger.info(f"  ✔ Detected and removed {files_deleted} items.")
        else:
            logger.info("  (Empty)")

    # Clean up specific file types in root if necessary (e.g. .json reports)
    # Be very careful here not to delete config files
    logger.info("Cleaning root directory reports...")
    for file in base_path.glob("*.json"):
        if file.name not in ["package-lock.json", "linkedin_cookies.json", "credentials.json"]:
             # Check if it looks like a generated report
             if "report" in file.name.lower() or "result" in file.name.lower() or "summary" in file.name.lower():
                 try:
                     file.unlink()
                     logger.info(f"  ✔ Deleted {file.name}")
                 except Exception as e:
                     logger.error(f"  ❌ Failed to delete {file.name}: {e}")

    logger.info("=" * 60)
    logger.info("✔  SYSTEM RESET COMPLETE")
    logger.info("=" * 60)
    logger.info("You can now start the AI Employee with fresh data.")

if __name__ == "__main__":
    reset_directories()
