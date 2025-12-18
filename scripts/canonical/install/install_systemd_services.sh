#!/bin/bash
#
# OmniMind Systemd Installer
# ==========================
# Installs backend service with Autopoietic Recovery ("Fight for Life")
#

set -e

PROJECT_ROOT=$(pwd)
USER_NAME=$(whoami)
SERVICE_NAME="omnimind-backend"
RECOVERY_SCRIPT="$PROJECT_ROOT/scripts/omnimind_intelligent_recovery.sh"
START_SCRIPT="$PROJECT_ROOT/scripts/start_omnimind_system.sh"

echo "🔧 OmniMind Service Installer"
echo "============================="
echo "Project Root: $PROJECT_ROOT"
echo "User: $USER_NAME"
echo ""

# Ensure scripts are executable
chmod +x "$RECOVERY_SCRIPT"
chmod +x "$START_SCRIPT"

# Generate Service File
cat > /tmp/$SERVICE_NAME.service << EOF
[Unit]
Description=OmniMind Backend (Autopoietic System)
After=network.target postgresql.service redis.service
Documentation=file://$PROJECT_ROOT/docs/SYSTEM_ARCHITECTURE.md

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_ROOT
Environment=OMNIMIND_PROJECT_ROOT=$PROJECT_ROOT
Environment=PYTHONUNBUFFERED=1

# Startup
ExecStart=$START_SCRIPT

# Autopoietic Recovery Hook
# Runs after stop/crash to analyze and "fight for life" (backup/compress) if needed
ExecStopPost=$RECOVERY_SCRIPT

# Restart Policy
Restart=always
RestartSec=5s
StartLimitIntervalSec=0

[Install]
WantedBy=multi-user.target
EOF

echo "📝 Service file generated at /tmp/$SERVICE_NAME.service"

if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Installing requires sudo. Asking for permission..."
    if ! sudo -n true 2>/dev/null; then
        echo "   (You may be asked for your password)"
    fi
fi

# Install
echo "Installing to /etc/systemd/system/..."
sudo cp /tmp/$SERVICE_NAME.service /etc/systemd/system/$SERVICE_NAME.service
rm /tmp/$SERVICE_NAME.service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo "✅ Installed $SERVICE_NAME.service"
echo ""
echo "🚀 To start: sudo systemctl start $SERVICE_NAME"
echo "📜 Status: sudo systemctl status $SERVICE_NAME"
