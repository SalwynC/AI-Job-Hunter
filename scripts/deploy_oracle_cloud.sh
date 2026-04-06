#!/bin/bash
# Deploy AI Job Hunter to Oracle Cloud Free Tier VM
# Usage: scp deploy_oracle_cloud.sh ubuntu@YOUR_VM:/tmp/ && ssh ubuntu@YOUR_VM 'bash /tmp/deploy_oracle_cloud.sh'

set -e

echo "🚀 Setting up AI Job Hunter on Oracle Cloud VM..."

# Install system dependencies
echo "Installing dependencies..."
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git curl wget bc

# Install Python deps
echo "Setting up Python environment..."
pip3 install --user --upgrade pip

# Clone project (or if already copied, just install deps)
cd /opt
if [ ! -d "ai-job-automation" ]; then
    echo "❌ Project not found at /opt/ai-job-automation"
    echo "Copy it first: scp -r ai-job-automation/ ubuntu@VM:/opt/"
    exit 1
fi

cd /opt/ai-job-automation
pip3 install --user -r requirements.txt

# Create necessary directories
mkdir -p logs data/data_storage data/runtime

# Setup systemd service
cat << 'EOF' | sudo tee /etc/systemd/system/ai-job-hunter.service
[Unit]
Description=AI Job Hunter - Continuous Job Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/ai-job-hunter
ExecStart=/usr/bin/python3 /opt/ai-job-hunter/job_scraper_3hr.py
Restart=always
RestartSec=30
Environment=PATH=/home/ubuntu/.local/bin:/usr/bin:/usr/local/bin
EnvironmentFile=/opt/ai-job-automation/.env-analyst

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
echo "Setting up service..."
sudo systemctl daemon-reload
sudo systemctl enable ai-job-hunter
sudo systemctl start ai-job-hunter

echo ""
echo "✅ AI Job Hunter is running 24/7!"
echo ""
echo "Check status: sudo systemctl status ai-job-hunter"
echo "View logs:    sudo journalctl -u ai-job-hunter -f"
echo "Restart:      sudo systemctl restart ai-job-hunter"
echo "Stop:         sudo systemctl stop ai-job-hunter"
echo ""
echo "Health check: curl http://localhost:8080 (if you start the health server too)"
