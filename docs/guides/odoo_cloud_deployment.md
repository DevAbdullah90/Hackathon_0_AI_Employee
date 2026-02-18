# Odoo Community Deployment on Cloud VM with Health Monitoring

## Overview
This document outlines the deployment of Odoo Community Edition on a cloud VM with health monitoring and integration with the AI Employee system.

## Cloud VM Setup for Odoo

### 1. VM Provisioning (Oracle Cloud Free Tier)
```bash
# Connect to your cloud VM
ssh ubuntu@your-vm-ip

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required dependencies
sudo apt install -y python3-pip python3-dev python3-wheel libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev libjpeg-dev libpq-dev postgresql-client
```

### 2. PostgreSQL Database Setup
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create Odoo database user
sudo -u postgres createuser -s odoo
sudo -u postgres createdb -O odoo odoo_db

# Set password for odoo user
sudo -u postgres psql -c "ALTER USER odoo PASSWORD 'your_secure_password';"
```

### 3. Odoo Installation
```bash
# Create odoo user
sudo adduser --system --group --home=/opt/odoo odoo

# Switch to odoo user
sudo su - odoo -s /bin/bash

# Download Odoo 19+ (latest community edition)
wget https://nightly.odoo.com/19.0/nightly/src/odoo_19.0.latest.zip
unzip odoo_19.0.latest.zip
mv odoo-19.0* odoo-server
cd odoo-server

# Install Python dependencies
pip3 install -r requirements.txt

# Exit odoo user
exit
```

### 4. Odoo Configuration
```bash
# Create Odoo configuration file
sudo mkdir -p /etc/odoo
sudo tee /etc/odoo/odoo.conf << EOF
[options]
; This is the password that allows database operations:
admin_passwd = your_master_password
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_secure_password
addons_path = /opt/odoo/odoo-server/addons
data_dir = /var/lib/odoo

; Security
proxy_mode = True

; Performance
workers = 4
max_cron_threads = 1

; Ports
xmlrpc_port = 8069
longpolling_port = 8072
EOF

# Set proper permissions
sudo chown -R odoo:odoo /etc/odoo/odoo.conf
sudo chmod 640 /etc/odoo/odoo.conf
```

### 5. Systemd Service for Odoo
```bash
# Create systemd service file
sudo tee /etc/systemd/system/odoo.service << EOF
[Unit]
Description=Odoo Open Source ERP and CRM
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=forking
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo-server/odoo-bin -c /etc/odoo/odoo.conf
KillMode=mixed
TimeoutStopSec=360
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
```

### 6. SSL Certificate Setup (HTTPS)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Install Nginx as reverse proxy
sudo apt install nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/odoo << EOF
upstream odoo {
    server 127.0.0.1:8069;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Add HSTS header
    add_header Strict-Transport-Security "max-age=31536000" always;

    location / {
        proxy_pass http://odoo;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Timeout settings
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }

    # Static files
    location /web/static/ {
        proxy_pass http://odoo;
        expires 1y;
        add_header Cache-Control "public";
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 7. Health Monitoring
```bash
# Create health check script
sudo tee /opt/odoo/check_odoo_health.py << EOF
#!/usr/bin/env python3
"""
Odoo Health Check Script
Monitors Odoo service and database connectivity
"""

import requests
import psycopg2
import subprocess
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/odoo_health.log'),
        logging.StreamHandler()
    ]
)

def check_odoo_service():
    """Check if Odoo service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'odoo'],
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception as e:
        logging.error(f"Error checking Odoo service: {e}")
        return False

def check_odoo_web_interface():
    """Check if Odoo web interface is accessible"""
    try:
        response = requests.get('https://your-domain.com/web/database/selector', timeout=10)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error checking Odoo web interface: {e}")
        return False

def check_database_connection():
    """Check database connectivity"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="odoo_db",
            user="odoo",
            password="your_secure_password"
        )
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
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

def send_alert(subject, message):
    """Send alert notification"""
    # In production, implement proper notification (email, Slack, etc.)
    logging.error(f"ALERT: {subject} - {message}")

def main():
    """Main health check function"""
    logging.info("Starting Odoo health check...")

    checks = {
        'service_running': check_odoo_service(),
        'web_accessible': check_odoo_web_interface(),
        'database_connected': check_database_connection(),
        'disk_space_ok': check_disk_space()
    }

    status = 'healthy' if all(checks.values()) else 'unhealthy'

    logging.info(f"Health check result: {status}")
    logging.info(f"Checks: {checks}")

    # Send alert if any check failed
    if not all(checks.values()):
        failed_checks = [k for k, v in checks.items() if not v]
        send_alert("Odoo Service Alert", f"Failed checks: {failed_checks}")

    # Log status for monitoring tools
    health_data = {
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'checks': checks
    }

    with open('/tmp/odoo_health_status.json', 'w') as f:
        json.dump(health_data, f)

    return status == 'healthy'

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
EOF

# Make executable
sudo chmod +x /opt/odoo/check_odoo_health.py
sudo chown odoo:odoo /opt/odoo/check_odoo_health.py
```

### 8. Health Monitoring Service
```bash
# Create systemd service for health monitoring
sudo tee /etc/systemd/system/odoo-health-monitor.service << EOF
[Unit]
Description=Odoo Health Monitoring Service
After=odoo.service

[Service]
Type=simple
User=odoo
ExecStart=/usr/bin/python3 /opt/odoo/check_odoo_health.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

# Enable and start health monitoring
sudo systemctl daemon-reload
sudo systemctl enable odoo-health-monitor
sudo systemctl start odoo-health-monitor
```

### 9. Backup Strategy
```bash
# Create backup script
sudo tee /opt/odoo/backup_odoo.sh << EOF
#!/bin/bash
# Odoo Backup Script

BACKUP_DIR="/opt/odoo/backups"
DB_NAME="odoo_db"
DATE=\$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p \$BACKUP_DIR

# Stop Odoo temporarily for consistent backup
sudo systemctl stop odoo

# Backup database
sudo -u postgres pg_dump \$DB_NAME > \$BACKUP_DIR/db_backup_\$DATE.sql

# Backup filestore
sudo -u odoo cp -r /var/lib/odoo/filestore \$BACKUP_DIR/filestore_\$DATE/

# Restart Odoo
sudo systemctl start odoo

# Compress backups
cd \$BACKUP_DIR
tar -czf odoo_complete_backup_\$DATE.tar.gz db_backup_\$DATE.sql filestore_\$DATE/

# Clean up uncompressed files
rm db_backup_\$DATE.sql
rm -rf filestore_\$DATE/

# Remove backups older than 30 days
find \$BACKUP_DIR -name "odoo_complete_backup_*" -mtime +30 -delete

echo "Backup completed at \$(date)"
EOF

# Make executable
sudo chmod +x /opt/odoo/backup_odoo.sh
sudo chown odoo:odoo /opt/odoo/backup_odoo.sh

# Set up daily backup with cron
echo "0 2 * * * /opt/odoo/backup_odoo.sh" | sudo crontab -
```

### 10. Integration with AI Employee MCP
```bash
# Update the Odoo MCP server configuration to point to cloud instance
cat > /home/ubuntu/ai-employee/odoo_mcp/cloud_config.json << EOF
{
  "servers": [
    {
      "name": "odoo",
      "command": "python",
      "args": ["/home/ubuntu/ai-employee/odoo_mcp/server.py"],
      "env": {
        "ODOO_URL": "https://your-domain.com",
        "ODOO_DB": "odoo_db",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "your_secure_password"
      }
    }
  ]
}
EOF
```

### 11. Auto-restart on Failure
```bash
# Update Odoo service with auto-restart configuration
sudo sed -i '/\[Service\]/a Restart=always\nRestartSec=10' /etc/systemd/system/odoo.service
sudo systemctl daemon-reload
```

### 12. Testing the Setup
```bash
# Check service status
sudo systemctl status odoo
sudo systemctl status odoo-health-monitor

# Check if Odoo is accessible
curl -I https://your-domain.com

# Run manual health check
sudo -u odoo python3 /opt/odoo/check_odoo_health.py

# Check logs
sudo journalctl -u odoo -f
sudo tail -f /var/log/odoo_health.log
```

## Security Considerations

1. **Master Password**: Store the admin password securely, not in plain text
2. **Database Security**: Use strong passwords and restrict database access
3. **SSL/TLS**: Always use HTTPS for production deployments
4. **Firewall**: Restrict access to necessary ports only
5. **Backups**: Regular encrypted backups stored securely
6. **Monitoring**: Real-time monitoring and alerting for critical issues

## Maintenance Tasks

1. **Regular Updates**: Keep Odoo and system packages updated
2. **Log Rotation**: Configure log rotation to prevent disk space issues
3. **Performance Monitoring**: Monitor system resources and database performance
4. **Security Audits**: Regular security reviews and vulnerability assessments

This completes the deployment of Odoo Community on a cloud VM with health monitoring and proper integration with the AI Employee system.