#!/usr/bin/env bash
# Installation script for OmniMind Daemon
# This sets up the daemon to run 24/7 as a systemd service

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   OmniMind Daemon Installation Script     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should NOT be run as root${NC}" 
   echo -e "${YELLOW}Run it as your regular user. It will ask for sudo when needed.${NC}"
   exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${YELLOW}📁 Project root: $PROJECT_ROOT${NC}"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}❌ Virtual environment not found at $PROJECT_ROOT/.venv${NC}"
    echo -e "${YELLOW}Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment found${NC}"

# Check if daemon module exists
if [ ! -f "$PROJECT_ROOT/src/daemon/omnimind_daemon.py" ]; then
    echo -e "${RED}❌ Daemon module not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Daemon module found${NC}"

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/omnimind-daemon.service"
TEMP_SERVICE="/tmp/omnimind-daemon.service"

# Replace paths in service file
cat "$SCRIPT_DIR/systemd/omnimind-daemon.service" | \
    sed "s|/home/fabricio/projects/omnimind|$PROJECT_ROOT|g" | \
    sed "s|User=fabricio|User=$USER|g" > "$TEMP_SERVICE"

echo ""
echo -e "${YELLOW}Installing systemd service...${NC}"

# Install service file (requires sudo)
sudo cp "$TEMP_SERVICE" "$SERVICE_FILE"
sudo chmod 644 "$SERVICE_FILE"

echo -e "${GREEN}✓ Service file installed to $SERVICE_FILE${NC}"

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"
echo -e "${GREEN}✓ Logs directory created${NC}"

# Reload systemd
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload

# Enable the service
echo -e "${YELLOW}Enabling omnimind-daemon service...${NC}"
sudo systemctl enable omnimind-daemon.service

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation Complete! ✓           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}The daemon is now installed but not started.${NC}"
echo ""
echo -e "Commands to manage the daemon:"
echo -e "  ${GREEN}sudo systemctl start omnimind-daemon${NC}    - Start the daemon"
echo -e "  ${GREEN}sudo systemctl stop omnimind-daemon${NC}     - Stop the daemon"
echo -e "  ${GREEN}sudo systemctl status omnimind-daemon${NC}   - Check daemon status"
echo -e "  ${GREEN}sudo systemctl restart omnimind-daemon${NC}  - Restart the daemon"
echo -e "  ${GREEN}sudo journalctl -u omnimind-daemon -f${NC}   - View live logs"
echo ""
echo -e "${YELLOW}To start the daemon now, run:${NC}"
echo -e "  ${GREEN}sudo systemctl start omnimind-daemon${NC}"
echo ""
