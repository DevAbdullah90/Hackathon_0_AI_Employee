#!/usr/bin/env python3
"""
AI Employee Monitor Dashboard
Displays real-time status of the AI Employee system
"""
import os
import sys
import time
import json
import psutil
from datetime import datetime
from pathlib import Path

# Try to import rich for better UI, fallback to standard print
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich library not found. Installing for better dashboard...")
    os.system("pip install rich")
    try:
        from rich.console import Console
        from rich.layout import Layout
        from rich.panel import Panel
        from rich.table import Table
        from rich.live import Live
        from rich.text import Text
        RICH_AVAILABLE = True
    except:
        print("Could not install rich. Using basic text mode.")

def get_system_stats():
    """Get system resource usage"""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, memory, disk

def get_folder_counts():
    """Get counts of files in key folders"""
    folders = {
        'Inbox': 0,
        'Needs_Action': 0,
        'Pending_Approval': 0,
        'Approved': 0,
        'Done': 0,
        'Failed': 0
    }
    
    for folder in folders:
        path = Path(folder)
        if path.exists():
            folders[folder] = len(list(path.glob('*.*')))
            
    return folders

def get_recent_logs(lines=5):
    """Get recent log entries"""
    log_dir = Path('Logs')
    if not log_dir.exists():
        return ["No logs directory found"]
        
    # Get newest log file
    log_files = sorted(log_dir.glob('*.log'), key=os.path.getmtime, reverse=True)
    if not log_files:
        return ["No log files found"]
        
    latest_log = log_files[0]
    try:
        with open(latest_log, 'r') as f:
            return f.readlines()[-lines:]
    except:
        return ["Error reading log file"]

def generate_layout():
    """Generate the dashboard layout"""
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    layout["left"].split(
        Layout(name="system", size=10),
        Layout(name="folders")
    )
    
    layout["right"].update(Panel("Logs"))
    
    return layout

def update_dashboard(console, layout):
    """Update dashboard content"""
    # Header
    layout["header"].update(
        Panel(
            Text("AI EMPLOYEE MONITORING DASHBOARD", justify="center", style="bold green"),
            style="white on black"
        )
    )
    
    # System Stats
    cpu, mem, disk = get_system_stats()
    sys_table = Table(show_header=False, expand=True)
    sys_table.add_row("CPU Usage", f"{cpu}%")
    sys_table.add_row("Memory Usage", f"{mem}%")
    sys_table.add_row("Disk Usage", f"{disk}%")
    
    layout["system"].update(
        Panel(sys_table, title="System Health", border_style="blue")
    )
    
    # Folder Counts
    counts = get_folder_counts()
    folder_table = Table(header_style="bold magenta", expand=True)
    folder_table.add_column("Folder")
    folder_table.add_column("Count")
    
    for folder, count in counts.items():
        color = "green" if count == 0 else "yellow"
        if folder == "Pending_Approval" and count > 0:
            color = "red"
        folder_table.add_row(folder, f"[{color}]{count}[/{color}]")
        
    layout["folders"].update(
        Panel(folder_table, title="Workflow Status", border_style="yellow")
    )
    
    # Logs
    logs = get_recent_logs(15)
    log_text = Text("")
    for line in logs:
        log_text.append(line)
        
    layout["right"].update(
        Panel(log_text, title="Recent Logs", border_style="white")
    )
    
    # Footer
    layout["footer"].update(
        Panel(
            Text(f"Last Updated: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to Exit", justify="center"),
            style="dim"
        )
    )

def main():
    if not RICH_AVAILABLE:
        print("Starting in basic mode (install 'rich' for dashboard view)...")
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"=== AI MONITOR ({datetime.now().strftime('%H:%M:%S')}) ===")
            print("\n[Folders]")
            for k, v in get_folder_counts().items():
                print(f"{k}: {v}")
            print("\n[System]")
            c, m, d = get_system_stats()
            print(f"CPU: {c}% | MEM: {m}%")
            print("\n[Latest Logs]")
            for line in get_recent_logs(3):
                print(line.strip())
            time.sleep(5)
            
    else:
        console = Console()
        layout = generate_layout()
        
        with Live(layout, refresh_per_second=1, screen=True):
            while True:
                update_dashboard(console, layout)
                time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
