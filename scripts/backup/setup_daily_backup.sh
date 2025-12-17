#!/bin/bash
#
# Setup Daily Backup Cron Job
# Configures automatic daily backup at end of day
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/daily_backup.sh"
CRON_TIME="23:59"  # End of day

echo "Setting up daily backup cron job..."
echo "Project: $PROJECT_DIR"
echo "Backup Script: $BACKUP_SCRIPT"
echo "Time: $CRON_TIME (daily)"

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "ERROR: Backup script not found: $BACKUP_SCRIPT"
    exit 1
fi

# Create systemd timer (preferred method)
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_USER_DIR"

# Create service file
cat > "$SYSTEMD_USER_DIR/omnimind-backup.service" <<EOF
[Unit]
Description=OmniMind Daily Backup
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/sudo $BACKUP_SCRIPT
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# Create timer file
cat > "$SYSTEMD_USER_DIR/omnimind-backup.timer" <<EOF
[Unit]
Description=OmniMind Daily Backup Timer
Requires=omnimind-backup.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 23:59:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo ""
echo "✅ Systemd timer created:"
echo "   Service: $SYSTEMD_USER_DIR/omnimind-backup.service"
echo "   Timer: $SYSTEMD_USER_DIR/omnimind-backup.timer"
echo ""
echo "To enable and start:"
echo "  systemctl --user enable omnimind-backup.timer"
echo "  systemctl --user start omnimind-backup.timer"
echo "  systemctl --user status omnimind-backup.timer"
echo ""
echo "To check next run:"
echo "  systemctl --user list-timers omnimind-backup.timer"
echo ""

# Also create cron job as fallback
CRON_ENTRY="59 23 * * * /usr/bin/sudo $BACKUP_SCRIPT >> $PROJECT_DIR/logs/backup_cron.log 2>&1"

# Check if cron entry already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠️  Cron entry already exists, skipping..."
else
    echo "Creating cron entry as fallback..."
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "✅ Cron entry added"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Choose one method:"
echo ""
echo "1. Systemd Timer (Recommended):"
echo "   systemctl --user enable --now omnimind-backup.timer"
echo ""
echo "2. Cron (Fallback - already configured):"
echo "   Check with: crontab -l"
echo ""
echo "To test backup manually:"
echo "   sudo $BACKUP_SCRIPT"
echo ""

