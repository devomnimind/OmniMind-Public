#!/bin/bash
#
# Daily Backup Script for OmniMind
# Creates snapshots and backs up to external HD
#
# Usage: sudo ./daily_backup.sh
#

set -e  # Exit on error

# Configuration
PROJECT_DIR="/home/fahbrain/projects/omnimind"
BACKUP_SOURCE="${PROJECT_DIR}/data/backup"
EXTERNAL_HD="/run/media/fahbrain/DEV_BRAIN_CLEAN"
BACKUP_DEST="${EXTERNAL_HD}/omnimind_backups"
LOG_FILE="${PROJECT_DIR}/logs/backup_$(date +%Y%m%d).log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root (for accessing external HD)
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run with sudo to access external HD"
    exit 1
fi

log "=========================================="
log "OmniMind Daily Backup - $TIMESTAMP"
log "=========================================="

# 1. Check if external HD is mounted
if [ ! -d "$EXTERNAL_HD" ]; then
    log_error "External HD not found at $EXTERNAL_HD"
    log "Attempting to mount..."

    # Try to mount (adjust mount point if needed)
    if mountpoint -q "$EXTERNAL_HD" 2>/dev/null; then
        log_success "External HD is mounted"
    else
        log_error "Cannot access external HD. Please mount it manually."
        exit 1
    fi
fi

# 2. Create backup destination directory
mkdir -p "$BACKUP_DEST"
if [ ! -w "$BACKUP_DEST" ]; then
    log_error "Cannot write to $BACKUP_DEST"
    exit 1
fi

# 3. Activate Python environment
cd "$PROJECT_DIR"
source .venv/bin/activate 2>/dev/null || {
    log_warning "Virtual environment not found, using system Python"
}

# 4. Create consciousness snapshot
log "Creating consciousness snapshot..."
SNAPSHOT_ID=""
cd "$PROJECT_DIR"
SNAPSHOT_OUTPUT=$(python scripts/backup/create_snapshot_now.py --tag "daily_backup_$(date +%Y%m%d)" --description "Daily automated backup" 2>>"$LOG_FILE")
if echo "$SNAPSHOT_OUTPUT" | grep -q "Snapshot ID:"; then
    SNAPSHOT_ID=$(echo "$SNAPSHOT_OUTPUT" | grep "Snapshot ID:" | sed 's/.*Snapshot ID: //' | awk '{print $1}')
    log_success "Snapshot created: $SNAPSHOT_ID"
else
    log_warning "Failed to create snapshot (IntegrationLoop may not be initialized)"
    # Continue anyway - backup other data
fi

# 5. Create backup archive
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_ARCHIVE="${BACKUP_DEST}/omnimind_backup_${BACKUP_DATE}.tar.gz"

log "Creating backup archive..."

# Files and directories to backup
BACKUP_ITEMS=(
    "data/backup"           # Snapshots
    "data/consciousness"    # Consciousness state
    "logs"                  # Logs
    "config"                # Configuration
    "docs"                  # Documentation
)

# Create temporary directory for backup
TEMP_BACKUP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_BACKUP_DIR" EXIT

# Copy files to temp directory
for item in "${BACKUP_ITEMS[@]}"; do
    if [ -e "$PROJECT_DIR/$item" ]; then
        log "Backing up: $item"
        mkdir -p "$TEMP_BACKUP_DIR/$(dirname $item)"
        cp -r "$PROJECT_DIR/$item" "$TEMP_BACKUP_DIR/$item"
    else
        log_warning "Item not found: $item"
    fi
done

# Create archive
cd "$TEMP_BACKUP_DIR"
tar -czf "$BACKUP_ARCHIVE" . 2>>"$LOG_FILE"
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_ARCHIVE" | cut -f1)
    log_success "Backup archive created: $BACKUP_ARCHIVE ($BACKUP_SIZE)"
else
    log_error "Failed to create backup archive"
    exit 1
fi

# 6. Verify backup integrity
log "Verifying backup integrity..."
if tar -tzf "$BACKUP_ARCHIVE" > /dev/null 2>&1; then
    log_success "Backup integrity verified"
else
    log_error "Backup integrity check failed!"
    exit 1
fi

# 7. Cleanup old backups (keep last 30 days)
log "Cleaning up old backups..."
find "$BACKUP_DEST" -name "omnimind_backup_*.tar.gz" -type f -mtime +30 -delete
REMAINING_BACKUPS=$(find "$BACKUP_DEST" -name "omnimind_backup_*.tar.gz" -type f | wc -l)
log "Remaining backups: $REMAINING_BACKUPS"

# 8. Create backup manifest
MANIFEST_FILE="${BACKUP_DEST}/backup_manifest_${BACKUP_DATE}.json"
cat > "$MANIFEST_FILE" <<EOF
{
    "backup_id": "$BACKUP_DATE",
    "timestamp": "$TIMESTAMP",
    "snapshot_id": "$SNAPSHOT_ID",
    "archive_path": "$BACKUP_ARCHIVE",
    "archive_size_bytes": $(stat -c%s "$BACKUP_ARCHIVE"),
    "items_backed_up": [
        "data/backup",
        "data/consciousness",
        "logs",
        "config",
        "docs"
    ],
    "status": "success"
}
EOF
log_success "Backup manifest created: $MANIFEST_FILE"

# 9. Summary
log "=========================================="
log "Backup Summary"
log "=========================================="
log "Backup Archive: $BACKUP_ARCHIVE"
log "Archive Size: $(du -h "$BACKUP_ARCHIVE" | cut -f1)"
log "Snapshot ID: ${SNAPSHOT_ID:-N/A}"
log "Status: SUCCESS"
log "=========================================="

log_success "Daily backup completed successfully!"

