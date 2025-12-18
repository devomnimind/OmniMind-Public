#!/bin/bash
# Setup OmniMind Security Privileges
# This script installs the sudoers configuration for OmniMind SecurityAgent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUDOERS_FILE="$SCRIPT_DIR/../config/sudoers.d/omnimind"
SUDOERS_DEST="/etc/sudoers.d/omnimind"

echo "🔐 OmniMind Security Setup"
echo "=========================="
echo ""
echo "This script will:"
echo "  1. Validate the sudoers configuration"
echo "  2. Install it to /etc/sudoers.d/omnimind"
echo "  3. Set correct permissions (0440)"
echo ""
echo "The configuration grants NOPASSWD sudo for:"
echo "  - Network monitoring (tc, iptables -L, ss, netstat)"
echo "  - Process monitoring (pgrep, ps, pkill -f nmap)"
echo "  - System audit (auditctl, ausearch)"
echo "  - Log monitoring (tail, journalctl)"
echo "  - Service management (systemctl for omnimind-* services only)"
echo ""
echo "CRITICAL commands (reboot, shutdown) will STILL require your password."
echo ""

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run with sudo:"
   echo "   sudo $0"
   exit 1
fi

# Validate sudoers file
echo "Validating sudoers configuration..."
if ! visudo -cf "$SUDOERS_FILE"; then
    echo "❌ Sudoers configuration is invalid!"
    echo "Please check $SUDOERS_FILE for syntax errors."
    exit 1
fi

echo "✅ Sudoers configuration is valid"

# Get the actual username (not root if using sudo)
ACTUAL_USER="${SUDO_USER:-$USER}"
echo "Configuring for user: $ACTUAL_USER"

# Replace placeholder username in sudoers file if needed
sed "s/fahbrain/$ACTUAL_USER/g" "$SUDOERS_FILE" > /tmp/omnimind_sudoers_tmp

# Validate modified file
if ! visudo -cf /tmp/omnimind_sudoers_tmp; then
    echo "❌ Modified sudoers configuration is invalid!"
    rm /tmp/omnimind_sudoers_tmp
    exit 1
fi

# Install
echo "Installing to $SUDOERS_DEST..."
cp /tmp/omnimind_sudoers_tmp "$SUDOERS_DEST"
chmod 0440 "$SUDOERS_DEST"
chown root:root "$SUDOERS_DEST"
rm /tmp/omnimind_sudoers_tmp

echo ""
echo "✅ OmniMind security privileges installed successfully!"
echo ""
echo "📝 Audit logs:"
echo "   - System sudo logs: /var/log/auth.log"
echo "   - OmniMind security log: $(pwd)/logs/security_validation.jsonl"
echo ""
echo "🔍 To verify:"
echo "   sudo -l -U $ACTUAL_USER | grep -A 20 NOPASSWD"
echo ""
echo "⚠️  To remove:"
echo "   sudo rm $SUDOERS_DEST"
echo ""
