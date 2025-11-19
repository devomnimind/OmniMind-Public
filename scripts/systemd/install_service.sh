#!/bin/bash
# OmniMind Systemd Service Installation Script
# Installs and configures systemd services for OmniMind

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run this script as root"
    print_info "Run as: ./install_service.sh [--user USERNAME]"
    exit 1
fi

# Parse arguments
USER_NAME="${USER}"
INSTALL_USER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --user)
            INSTALL_USER="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --user USERNAME    Install for specific user (default: current user)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Use specified user or current user
if [ -n "$INSTALL_USER" ]; then
    USER_NAME="$INSTALL_USER"
fi

print_info "Installing OmniMind services for user: $USER_NAME"

# Detect project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

print_info "Project directory: $PROJECT_DIR"

# Verify required files exist
if [ ! -f "$PROJECT_DIR/.venv/bin/python" ]; then
    print_error "Virtual environment not found at $PROJECT_DIR/.venv"
    print_info "Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/omnimind.service" ]; then
    print_error "Service file not found: $SCRIPT_DIR/omnimind.service"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/omnimind-daemon.service" ]; then
    print_error "Daemon service file not found: $SCRIPT_DIR/omnimind-daemon.service"
    exit 1
fi

# Create systemd user directory if it doesn't exist
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_USER_DIR"

print_info "Installing systemd service files..."

# Copy and customize service files
sed "s|%i|$USER_NAME|g" "$SCRIPT_DIR/omnimind.service" > "$SYSTEMD_USER_DIR/omnimind.service"
sed "s|%i|$USER_NAME|g" "$SCRIPT_DIR/omnimind-daemon.service" > "$SYSTEMD_USER_DIR/omnimind-daemon.service"

print_info "Service files installed to: $SYSTEMD_USER_DIR"

# Create required directories
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/data"

print_info "Created log and data directories"

# Reload systemd daemon
print_info "Reloading systemd daemon..."
systemctl --user daemon-reload

# Enable services
print_info "Enabling services..."
systemctl --user enable omnimind.service
systemctl --user enable omnimind-daemon.service

print_info "Services enabled"

# Optional: Enable linger for user (allows services to run when user is not logged in)
print_info "Enabling linger for user $USER_NAME (allows services to run without login)..."
if loginctl show-user "$USER_NAME" | grep -q "Linger=yes"; then
    print_info "Linger already enabled for user $USER_NAME"
else
    sudo loginctl enable-linger "$USER_NAME" 2>/dev/null || print_warn "Could not enable linger (requires sudo)"
fi

# Setup log rotation
print_info "Setting up log rotation..."
LOGROTATE_CONFIG="/etc/logrotate.d/omnimind-$USER_NAME"

cat > /tmp/omnimind-logrotate <<EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 $USER_NAME $USER_NAME
    sharedscripts
    postrotate
        systemctl --user restart omnimind.service > /dev/null 2>&1 || true
    endscript
}
EOF

sudo mv /tmp/omnimind-logrotate "$LOGROTATE_CONFIG" 2>/dev/null || \
    print_warn "Could not install logrotate config (requires sudo)"

print_info "=================================="
print_info "Installation complete!"
print_info "=================================="
echo ""
print_info "Service management commands:"
echo "  Start:    systemctl --user start omnimind.service"
echo "  Stop:     systemctl --user stop omnimind.service"
echo "  Status:   systemctl --user status omnimind.service"
echo "  Logs:     journalctl --user -u omnimind.service -f"
echo ""
print_info "Daemon management commands:"
echo "  Start:    systemctl --user start omnimind-daemon.service"
echo "  Stop:     systemctl --user stop omnimind-daemon.service"
echo "  Status:   systemctl --user status omnimind-daemon.service"
echo "  Logs:     journalctl --user -u omnimind-daemon.service -f"
echo ""
print_info "Start both services:"
echo "  systemctl --user start omnimind.service omnimind-daemon.service"
echo ""
print_warn "Note: Services are enabled but not started automatically."
print_info "Start them manually with the commands above."
