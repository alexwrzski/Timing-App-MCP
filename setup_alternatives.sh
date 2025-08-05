#!/bin/bash

# Setup Alternatives for Timing App Workflow
# This script provides multiple ways to run the workflow without n8n

echo "🚀 Setting up Timing App Workflow Alternatives"
echo "=============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$TIMING_API_TOKEN" ]; then
    echo "❌ TIMING_API_TOKEN environment variable not set"
    echo "Please set it: export TIMING_API_TOKEN='your_token_here'"
    exit 1
fi

echo "✅ Environment check passed"

# Option 1: Run standalone script
echo ""
echo "📋 Option 1: Run Standalone Script"
echo "----------------------------------"
echo "Run the workflow manually:"
echo "  python3 standalone_workflow.py --once    # Single check"
echo "  python3 standalone_workflow.py           # Continuous (every 30 min)"
echo ""

# Option 2: Setup cron job
echo "📋 Option 2: Setup Cron Job"
echo "---------------------------"
echo "Add this to your crontab (crontab -e):"
echo "*/30 * * * * cd $(pwd) && python3 standalone_workflow.py --once >> workflow.log 2>&1"
echo ""

# Option 3: Setup systemd service
echo "📋 Option 3: Setup Systemd Service"
echo "----------------------------------"

# Create systemd service file
cat > timing-workflow.service << EOF
[Unit]
Description=Timing App Workflow
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=TIMING_API_TOKEN=$TIMING_API_TOKEN
Environment=JIRA_BASE_URL=${JIRA_BASE_URL:-}
Environment=JIRA_USERNAME=${JIRA_USERNAME:-}
Environment=JIRA_API_TOKEN=${JIRA_API_TOKEN:-}
ExecStart=/usr/bin/python3 $(pwd)/standalone_workflow.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

echo "Created systemd service file: timing-workflow.service"
echo ""
echo "To install the service:"
echo "  sudo cp timing-workflow.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable timing-workflow"
echo "  sudo systemctl start timing-workflow"
echo ""
echo "To check status:"
echo "  sudo systemctl status timing-workflow"
echo "  sudo journalctl -u timing-workflow -f"
echo ""

# Option 4: Docker setup
echo "📋 Option 4: Docker Setup"
echo "-------------------------"

# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV TIMING_API_TOKEN=\${TIMING_API_TOKEN}
ENV JIRA_BASE_URL=\${JIRA_BASE_URL}
ENV JIRA_USERNAME=\${JIRA_USERNAME}
ENV JIRA_API_TOKEN=\${JIRA_API_TOKEN}

# Run the workflow
CMD ["python3", "standalone_workflow.py"]
EOF

echo "Created Dockerfile"
echo ""
echo "To build and run with Docker:"
echo "  docker build -t timing-workflow ."
echo "  docker run -d --name timing-workflow \\"
echo "    -e TIMING_API_TOKEN=\$TIMING_API_TOKEN \\"
echo "    -e JIRA_BASE_URL=\$JIRA_BASE_URL \\"
echo "    -e JIRA_USERNAME=\$JIRA_USERNAME \\"
echo "    -e JIRA_API_TOKEN=\$JIRA_API_TOKEN \\"
echo "    timing-workflow"
echo ""

# Option 5: Test the workflow
echo "📋 Option 5: Test the Workflow"
echo "------------------------------"
echo "Test the workflow now:"
echo "  python3 standalone_workflow.py --once"
echo ""

echo "✅ Setup complete!"
echo ""
echo "🎯 Recommended approach:"
echo "1. Test with: python3 standalone_workflow.py --once"
echo "2. If it works, set up cron job or systemd service"
echo "3. Monitor logs to ensure it's working correctly"
echo ""
echo "📁 Files created:"
echo "- standalone_workflow.py (main script)"
echo "- timing-workflow.service (systemd service)"
echo "- Dockerfile (Docker container)"
echo ""
echo "📖 For more information, see the documentation files." 