#!/bin/bash
# Install OmniMind Systemd Services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$SCRIPT_DIR/../config/systemd"
SYSTEMD_DIR="/etc/systemd/system"

echo "🔧 Installing OmniMind Systemd Services..."

# Check sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run with sudo"
   exit 1
fi

# Copy services
echo "Copying service files..."
cp "$SERVICE_DIR/omnimind-backend.service" "$SYSTEMD_DIR/"
cp "$SERVICE_DIR/omnimind-frontend.service" "$SYSTEMD_DIR/"

# Reload daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable services
echo "Enabling services..."
systemctl enable omnimind-backend.service
systemctl enable omnimind-frontend.service

# Restart services
echo "Starting services..."
systemctl restart omnimind-backend.service
systemctl restart omnimind-frontend.service

echo "✅ OmniMind Services Installed and Started!"
echo "   Backend Status: systemctl status omnimind-backend"
echo "   Frontend Status: systemctl status omnimind-frontend"
