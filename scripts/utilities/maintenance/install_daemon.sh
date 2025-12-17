#!/usr/bin/env bash
# Installation script for OmniMind Daemon
# This sets up the daemon to run 24/7 as a systemd service

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   OmniMind Daemon Installation Script     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

OMNIMIND_USER="${OMNIMIND_USER:-$USER}"

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

print_success "Daemon module found"

SERVICE_TEMPLATE="$SCRIPT_DIR/systemd/omnimind-daemon.service"
SERVICE_FILE="/etc/systemd/system/omnimind-daemon.service"
TEMP_SERVICE="$(mktemp /tmp/omnimind-daemon.XXXXXX)"
trap 'rm -f "$TEMP_SERVICE"' EXIT

check_systemd_available() {
    if ! command -v systemctl &> /dev/null; then
        echo -e "${RED}❌ systemctl not found${NC}"
        exit 1
    fi
}

check_sudo_privileges() {
    print_status "Verifying sudo privileges for $OMNIMIND_USER..."
    if ! id "$OMNIMIND_USER" &> /dev/null; then
        echo -e "${RED}❌ User $OMNIMIND_USER does not exist${NC}"
        exit 1
    fi

    local user_groups
    user_groups=$(id -nG "$OMNIMIND_USER")
    if [[ ! " $user_groups " =~ (sudo|wheel|admin|root) ]]; then
        echo -e "${RED}❌ $OMNIMIND_USER lacks sudo privileges${NC}"
        echo -e "${YELLOW}Add $OMNIMIND_USER to a sudo group before continuing${NC}"
        exit 1
    fi

    print_success "User $OMNIMIND_USER has sudo privileges"
}

check_system_health() {
    print_status "Evaluating host resource headroom (brakes)..."
    python3 <<'PY'
import os
from pathlib import Path

meminfo = {}
with open('/proc/meminfo') as fh:
    for line in fh:
        key, value = line.split(':')
        meminfo[key.strip()] = int(value.split()[0])

available_mb = meminfo.get('MemAvailable', meminfo.get('MemFree', meminfo.get('MemTotal', 0))) // 1024
cpus = os.cpu_count() or 1
load5 = float(Path('/proc/loadavg').read_text().split()[1])

print(f"  CPUs: {cpus}")
print(f"  Memory available: {available_mb} MB")
print(f"  5m load average: {load5:.2f}")

warnings = []
if available_mb < 2048:
    warnings.append('low memory headroom (<=2GB)')
if load5 > cpus * 0.9:
    warnings.append('load approaching CPU capacity')

if warnings:
    print('  ⚠ ' + ' and '.join(warnings))
else:
    print('  ✅ Headroom looks healthy for installation')
PY
}

render_service_template() {
    python3 - "$SERVICE_TEMPLATE" "$PROJECT_ROOT" "$OMNIMIND_USER" <<'PY'
from pathlib import Path
import sys

template = Path(sys.argv[1]).read_text()
project_root = sys.argv[2]
user = sys.argv[3]
template = template.replace('__PROJECT_ROOT__', project_root)
template = template.replace('__OMNIMIND_USER__', user)
print(template, end='')
PY
}

check_systemd_available
check_sudo_privileges
check_system_health

print_status "Rendering systemd unit for $SERVICE_FILE"
render_service_template > "$TEMP_SERVICE"

print_status "Installing systemd service..."
sudo cp "$TEMP_SERVICE" "$SERVICE_FILE"
sudo chmod 644 "$SERVICE_FILE"

print_success "Service file installed to $SERVICE_FILE"

mkdir -p "$PROJECT_ROOT/logs"
print_success "Logs directory created"

print_status "Reloading systemd daemon" 
sudo systemctl daemon-reload

print_status "Enabling omnimind-daemon service"
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
