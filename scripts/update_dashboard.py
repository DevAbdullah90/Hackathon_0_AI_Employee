import json
import psutil
import os
from datetime import datetime
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / "Logs"
DASHBOARD_FILE = ROOT_DIR / "Dashboard.md"

def get_system_stats():
    """Get CPU, Memory, and Disk usage."""
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, memory, disk

def get_workflow_counts():
    """Count files in workflow directories."""
    folders = ['Inbox', 'Needs_Action', 'Pending_Approval', 'Approved', 'Done', 'Failed']
    counts = {}
    for folder in folders:
        path = ROOT_DIR / folder
        if path.exists():
            counts[folder] = len(list(path.glob('*.*')))
        else:
            counts[folder] = 0
    return counts

def get_schedule_status():
    """Get the latest schedule status from Logs."""
    if not LOGS_DIR.exists():
        return None
    
    # Find latest status file
    status_files = sorted(LOGS_DIR.glob('status_*.json'), key=os.path.getmtime, reverse=True)
    if not status_files:
        return None
        
    try:
        with open(status_files[0], 'r') as f:
            return json.load(f)
    except:
        return None

def get_recent_activity(limit=10):
    """Get recent success/failure logs."""
    if not LOGS_DIR.exists():
        return []
        
    # Find all success/failed json files
    files = list(LOGS_DIR.glob('success_*.json')) + list(LOGS_DIR.glob('failed_*.json'))
    files.sort(key=os.path.getmtime, reverse=True)
    
    activities = []
    for file_path in files[:limit]:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Determine status icon
            is_success = 'success' in file_path.name
            icon = "✅" if is_success else "❌"
            
            # Extract details
            platform = data.get('result', {}).get('platform', 'unknown')
            timestamp = data.get('timestamp', '')
            if timestamp:
                timestamp = timestamp.split('T')[1][:8] # HH:MM:SS
                
            # Try to get metadata type if platform is generic
            if platform == 'unknown':
                platform = data.get('metadata', {}).get('type', 'unknown')
                
            activities.append(f"| {timestamp} | {icon} | {platform} | {file_path.name} |")
        except:
            continue
            
    return activities

def generate_dashboard():
    """Generate the Markdown dashboard."""
    cpu, mem, disk = get_system_stats()
    workflow = get_workflow_counts()
    schedule = get_schedule_status()
    activities = get_recent_activity()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"""# 🤖 AI Employee Dashboard
**Last Updated:** {now}

## 🖥️ System Health
| Metric | Usage | Status |
| :--- | :--- | :--- |
| **CPU** | {cpu}% | {"🟢 Good" if cpu < 80 else "🔴 High"} |
| **RAM** | {mem}% | {"🟢 Good" if mem < 80 else "🔴 High"} |
| **Disk** | {disk}% | {"🟢 Good" if disk < 90 else "🔴 Full"} |

## 📂 Workflow Queue
| Folder | Files | Status |
| :--- | :--- | :--- |
| 📥 **Inbox** | {workflow['Inbox']} | {"Wait" if workflow['Inbox'] > 0 else "Empty"} |
| ⚠️ **Needs Action** | {workflow['Needs_Action']} | {"**ACTION REQUIRED**" if workflow['Needs_Action'] > 0 else "Clear"} |
| ⏳ **Pending Approval** | {workflow['Pending_Approval']} | {"**REVIEW**" if workflow['Pending_Approval'] > 0 else "Clear"} |
| ✅ **Approved** | {workflow['Approved']} | - |
| 🏁 **Done** | {workflow['Done']} | - |
| ❌ **Failed** | {workflow['Failed']} | {"**CHECK LOGS**" if workflow['Failed'] > 0 else "Clear"} |

## 📅 Upcoming Schedule
"""

    if schedule and 'next_run_times' in schedule:
        md += "| Task | Next Run | Interval |\n| :--- | :--- | :--- |\n"
        for item in schedule['next_run_times']:
            # Parse Job string roughly "Job(interval=3, unit=hours...)"
            job_str = item.get('job', '')
            func = "Unknown"
            if 'do=' in job_str:
                func = job_str.split('do=')[1].split(',')[0]
            
            next_run = item.get('next_run', '').split(' ')[1] # Time only
            
            md += f"| `{func}` | **{next_run}** | {job_str} |\n"
    else:
        md += "> *No schedule data available.*\n"

    md += """
## 📜 Recent Activity
| Time | Status | Platform | Log File |
| :--- | :---: | :--- | :--- |
"""
    
    if activities:
        md += "\n".join(activities)
    else:
        md += "| - | - | - | - |"
        
    md += """

---
> *This dashboard updates automatically when `scripts/update_dashboard.py` runs.*
"""

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(md)
        
    print(f"Dashboard updated at {DASHBOARD_FILE}")

if __name__ == "__main__":
    generate_dashboard()
