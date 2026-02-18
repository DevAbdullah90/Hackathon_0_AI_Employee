# Cloud Deployment Architecture for AI Employee

## Overview
This document describes the architecture for deploying the AI Employee on cloud infrastructure with 24/7 operation.

## Cloud VM Setup (Oracle Cloud Free Tier)

### 1. VM Provisioning
```bash
# Example setup for Oracle Cloud
# 1. Create Ubuntu 22.04 VM instance
# 2. Configure security groups to allow:
#    - SSH (port 22)
#    - HTTPS (port 443) for webhooks
#    - HTTP (port 80) for monitoring

# 3. Install required packages
sudo apt update
sudo apt install -y python3.11 python3-pip nodejs npm git docker.io docker-compose

# 4. Clone the AI Employee repository
git clone https://github.com/your-org/ai-employee.git
cd ai-employee
```

### 2. Environment Configuration
```bash
# Create environment file for cloud deployment
cat > .env.cloud << EOF
# Cloud-specific configurations
CLOUD_DEPLOYMENT=true
VAULT_SYNC_ENABLED=true
VAULT_SYNC_METHOD=git
VAULT_REMOTE_REPO=your-private-git-repo-url

# MCP Server Configurations
ODOO_URL=https://your-odoo-instance.oraclecloud.com
ODOO_DB=production_db
ODOO_USERNAME=admin
ODOO_PASSWORD=your_secure_password

# Social Media API Keys
FACEBOOK_ACCESS_TOKEN=your_fb_token
INSTAGRAM_USERNAME=your_ig_username
INSTAGRAM_PASSWORD=your_ig_password
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Email Configuration
GMAIL_CREDENTIALS=/secure/path/to/gmail_credentials.json

# Monitoring
HEALTH_CHECK_PORT=8080
LOG_LEVEL=INFO
EOF
```

### 3. Service Management with systemd
```bash
# Create systemd service file for the AI Employee
sudo tee /etc/systemd/system/ai-employee.service << EOF
[Unit]
Description=AI Employee Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-employee
EnvironmentFile=/home/ubuntu/ai-employee/.env.cloud
ExecStart=/usr/bin/python3 -m ai_employee.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
```

### 4. Health Monitoring Script
```bash
# Create health monitoring script
cat > health_monitor.py << EOF
#!/usr/bin/env python3
"""
Health monitoring script for AI Employee
Runs periodic checks and reports system status
"""

import os
import time
import logging
import subprocess
import requests
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ai_employee_health.log'),
        logging.StreamHandler()
    ]
)

def check_service_status():
    """Check if AI Employee services are running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'ai-employee'],
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception as e:
        logging.error(f"Error checking service status: {e}")
        return False

def check_disk_space():
    """Check available disk space"""
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        usage_line = lines[1]  # Skip header
        usage_percent = int(usage_line.split()[4].rstrip('%'))
        return usage_percent < 80  # Return True if less than 80% used
    except Exception as e:
        logging.error(f"Error checking disk space: {e}")
        return False

def check_memory_usage():
    """Check memory usage"""
    try:
        result = subprocess.run(['free', '-m'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        mem_line = lines[1]  # Skip header
        parts = mem_line.split()
        total = int(parts[1])
        used = int(parts[2])
        usage_percent = (used / total) * 100
        return usage_percent < 80  # Return True if less than 80% used
    except Exception as e:
        logging.error(f"Error checking memory usage: {e}")
        return False

def send_health_report():
    """Send health report to monitoring endpoint if configured"""
    webhook_url = os.getenv('HEALTH_WEBHOOK_URL')
    if not webhook_url:
        return

    status = {
        'timestamp': datetime.now().isoformat(),
        'service_active': check_service_status(),
        'disk_space_ok': check_disk_space(),
        'memory_usage_ok': check_memory_usage(),
        'instance_id': os.getenv('INSTANCE_ID', 'unknown')
    }

    try:
        response = requests.post(webhook_url, json=status)
        logging.info(f"Health report sent, status: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending health report: {e}")

def main():
    """Main monitoring loop"""
    logging.info("Starting AI Employee health monitoring...")

    while True:
        try:
            # Perform checks
            service_ok = check_service_status()
            disk_ok = check_disk_space()
            memory_ok = check_memory_usage()

            # Log status
            status_msg = f"Service: {'OK' if service_ok else 'FAILED'}, "
            status_msg += f"Disk: {'OK' if disk_ok else 'HIGH'}, "
            status_msg += f"Memory: {'OK' if memory_ok else 'HIGH'}"
            logging.info(status_msg)

            # Send health report
            send_health_report()

            # Wait before next check
            time.sleep(300)  # 5 minutes

        except KeyboardInterrupt:
            logging.info("Health monitoring stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in monitoring: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()
EOF

# Make executable and set up monitoring service
chmod +x health_monitor.py

sudo tee /etc/systemd/system/ai-employee-monitor.service << EOF
[Unit]
Description=AI Employee Health Monitor
After=ai-employee.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-employee
EnvironmentFile=/home/ubuntu/ai-employee/.env.cloud
ExecStart=/usr/bin/python3 /home/ubuntu/ai-employee/health_monitor.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ai-employee-monitor
sudo systemctl start ai-employee-monitor
```

### 5. Backup Strategy
```bash
# Create backup script
cat > backup_script.sh << EOF
#!/bin/bash
# Backup script for AI Employee data

BACKUP_DIR="/home/ubuntu/backups"
VAULT_DIR="/home/ubuntu/ai-employee/vault"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup vault data
tar -czf $BACKUP_DIR/vault_backup_$DATE.tar.gz -C $(dirname $VAULT_DIR) $(basename $VAULT_DIR)

# Backup configurations
cp /home/ubuntu/ai-employee/.env.cloud $BACKUP_DIR/config_backup_$DATE.env

# Remove backups older than 7 days
find $BACKUP_DIR -name "vault_backup_*" -mtime +7 -delete
find $BACKUP_DIR -name "config_backup_*" -mtime +7 -delete

# Optional: Upload to cloud storage
# aws s3 cp $BACKUP_DIR/ s3://your-backup-bucket/ --recursive --exclude "*" --include "vault_backup_$DATE*"
EOF

chmod +x backup_script.sh

# Set up daily backup with cron
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/ai-employee/backup_script.sh") | crontab -
```

### 6. SSL Certificate Setup (for webhooks)
```bash
# Install Certbot for SSL certificates
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (update with your domain)
sudo certbot certonly --standalone -d your-domain.com

# Auto-renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -
```

This completes the cloud deployment architecture for the AI Employee with 24/7 operation, health monitoring, and backup capabilities.