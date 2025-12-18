#!/bin/bash
# Install OmniMind Monitor as systemd service
# This ensures the continuous monitor starts automatically on boot

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SERVICE_FILE="$PROJECT_ROOT/config/systemd/omnimind-monitor.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "================================================"
echo "📡 OmniMind Monitor - Systemd Service Installation"
echo "================================================"
echo ""

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

echo "📋 Service configuration:"
echo "   Source: $SERVICE_FILE"
echo "   Target: $SYSTEMD_DIR/omnimind-monitor.service"
echo ""

# Copy service file
echo "📝 Copying service file..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/omnimind-monitor.service"
chmod 644 "$SYSTEMD_DIR/omnimind-monitor.service"

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable service (auto-start on boot)
echo "✅ Enabling service for auto-start..."
systemctl enable omnimind-monitor.service

# Start service immediately
echo "🚀 Starting monitor service..."
systemctl start omnimind-monitor.service

echo ""
echo "================================================"
echo "✅ Installation Complete!"
echo "================================================"
echo ""
echo "Monitor Status:"
systemctl status omnimind-monitor.service --no-pager | head -20
echo ""
echo "📡 Monitor Service Commands:"
echo "   Check status:  sudo systemctl status omnimind-monitor"
echo "   View logs:     sudo journalctl -u omnimind-monitor -f"
echo "   Stop monitor:  sudo systemctl stop omnimind-monitor"
echo "   Restart:       sudo systemctl restart omnimind-monitor"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - O monitor inicia automaticamente no boot"
echo "   - Ele reinicia automaticamente se falhar"
echo "   - Só pode ser parado manualmente (segurança)"
echo "   - Verifique logs: sudo journalctl -u omnimind-monitor -f"
echo ""
