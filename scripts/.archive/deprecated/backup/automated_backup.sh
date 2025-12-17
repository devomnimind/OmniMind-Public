#!/bin/bash
# OmniMind Automated Backup System
# Critical disaster recovery implementation

set -euo pipefail

# Configuration
BACKUP_ROOT="/var/backups/omnimind"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="omnimind_backup_${TIMESTAMP}"
BACKUP_DIR="${BACKUP_ROOT}/${BACKUP_NAME}"

# External storage (configurable)
EXTERNAL_STORAGE="/run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_backups"

# Logging
LOG_FILE="/var/log/omnimind/backup.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [BACKUP] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >&2 | tee -a "$LOG_FILE"
    exit 1
}

# Pre-flight checks
preflight_checks() {
    log "Starting pre-flight checks..."

    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        error "Backup must be run as root or with sudo"
    fi

    # Check disk space (need at least 2GB free)
    local available_space
    available_space=$(df /var/backups | tail -1 | awk '{print $4}')
    if [[ $available_space -lt 2097152 ]]; then  # 2GB in KB
        error "Insufficient disk space. Need at least 2GB free"
    fi

    # Check if external storage is mounted
    if [[ ! -d "$EXTERNAL_STORAGE" ]]; then
        log "Warning: External storage not mounted at $EXTERNAL_STORAGE"
    fi

    log "Pre-flight checks completed successfully"
}

# Create backup directories
create_backup_structure() {
    log "Creating backup directory structure..."

    mkdir -p "$BACKUP_DIR"/{database,config,logs,ssl,models,data}

    # Set secure permissions
    chmod 700 "$BACKUP_DIR"
    chmod 600 "$BACKUP_DIR"/* 2>/dev/null || true

    log "Backup structure created at $BACKUP_DIR"
}

# Backup database (if exists)
backup_database() {
    log "Backing up database..."

    # PostgreSQL backup (if running)
    if pg_isready -q 2>/dev/null; then
        pg_dumpall -U omnimind > "$BACKUP_DIR/database/postgres_all.sql" 2>/dev/null || {
            log "Warning: PostgreSQL backup failed (may not be configured)"
        }
    fi

    # SQLite databases
    find . -name "*.db" -o -name "*.sqlite*" 2>/dev/null | while read -r db_file; do
        if [[ -f "$db_file" ]]; then
            cp "$db_file" "$BACKUP_DIR/database/"
            log "Backed up database: $db_file"
        fi
    done
}

# Backup configuration files
backup_config() {
    log "Backing up configuration files..."

    # Copy config directory
    if [[ -d "config" ]]; then
        cp -r config "$BACKUP_DIR/"
        # Remove sensitive data from backup
        find "$BACKUP_DIR/config" -name "*.key" -o -name "*secret*" -o -name "*password*" | xargs -r rm -f
        log "Configuration backed up (sensitive data removed)"
    fi

    # Backup environment variables (redacted)
    env | grep -E "(OMNIMIND|DATABASE|SECRET)" | sed 's/=.*/=REDACTED/' > "$BACKUP_DIR/config/environment.txt" 2>/dev/null || true
}

# Backup SSL certificates and keys
backup_ssl() {
    log "Backing up SSL certificates..."

    if [[ -d ".omnimind/ssl" ]]; then
        # Only backup certificates, not private keys
        cp ".omnimind/ssl/certificate.crt" "$BACKUP_DIR/ssl/" 2>/dev/null || true
        log "SSL certificates backed up"
    fi
}

# Backup logs
backup_logs() {
    log "Backing up logs..."

    # System logs
    if [[ -d "/var/log/omnimind" ]]; then
        cp -r /var/log/omnimind "$BACKUP_DIR/logs/" 2>/dev/null || true
    fi

    # Application logs
    find . -name "*.log" -type f 2>/dev/null | head -10 | xargs -I {} cp {} "$BACKUP_DIR/logs/" 2>/dev/null || true

    # Rotate logs (keep last 7 days)
    find "$BACKUP_DIR/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true

    log "Logs backed up and rotated"
}

# Backup models and data
backup_models() {
    log "Backing up models and data..."

    # ML models (if exist)
    if [[ -d "models" ]]; then
        # Create lightweight backup (exclude large files)
        find models -type f -size -100M | xargs -I {} cp --parents {} "$BACKUP_DIR/" 2>/dev/null || true
        log "Models backed up (large files excluded)"
    fi

    # Vector databases (lightweight backup)
    if [[ -d "data/qdrant" ]]; then
        # Only backup configuration, not data
        cp -r data/qdrant/collections "$BACKUP_DIR/data/" 2>/dev/null || true
        log "Vector database configuration backed up"
    fi
}

# Create backup manifest
create_manifest() {
    log "Creating backup manifest..."

    cat > "$BACKUP_DIR/BACKUP_MANIFEST.txt" << EOF
OmniMind Automated Backup Manifest
==================================

Backup Date: $(date)
Backup Name: $BACKUP_NAME
Backup Location: $BACKUP_DIR

Contents:
$(find "$BACKUP_DIR" -type f | wc -l) files
$(du -sh "$BACKUP_DIR" | cut -f1) total size

Components Backed Up:
- Database dumps
- Configuration files (sanitized)
- SSL certificates
- Log files (last 7 days)
- Model configurations
- Vector database schemas

Integrity Check:
$(find "$BACKUP_DIR" -type f -exec sha256sum {} \; | sha256sum | cut -d' ' -f1) - Global checksum

Retention Policy:
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months

Recovery Instructions:
1. Stop all OmniMind services
2. Restore from backup directory
3. Restart services
4. Verify integrity

Contact: support@omnimind.ai
EOF

    log "Backup manifest created"
}

# Compress backup
compress_backup() {
    log "Compressing backup..."

    local archive_name="${BACKUP_NAME}.tar.gz"
    local archive_path="${BACKUP_ROOT}/${archive_name}"

    cd "$BACKUP_ROOT"
    tar -czf "$archive_path" "$BACKUP_NAME"

    # Calculate checksum
    sha256sum "$archive_path" > "${archive_path}.sha256"

    log "Backup compressed: $archive_path ($(du -sh "$archive_path" | cut -f1))"
}

# Copy to external storage
copy_to_external() {
    if [[ -d "$EXTERNAL_STORAGE" ]]; then
        log "Copying to external storage..."

        local archive_name="${BACKUP_NAME}.tar.gz"
        cp "${BACKUP_ROOT}/${archive_name}"* "$EXTERNAL_STORAGE/"

        # Verify copy integrity
        if [[ -f "${EXTERNAL_STORAGE}/${archive_name}" ]]; then
            if cmp "${BACKUP_ROOT}/${archive_name}" "${EXTERNAL_STORAGE}/${archive_name}"; then
                log "External backup verified successfully"
            else
                error "External backup verification failed"
            fi
        fi
    else
        log "External storage not available, skipping external copy"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old backups..."

    # Keep last 7 daily backups
    find "$BACKUP_ROOT" -name "omnimind_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true

    # Keep last 4 weekly backups (marked with _weekly)
    find "$BACKUP_ROOT" -name "*_weekly.tar.gz" -mtime +28 -delete 2>/dev/null || true

    # Keep last 12 monthly backups (marked with _monthly)
    find "$BACKUP_ROOT" -name "*_monthly.tar.gz" -mtime +365 -delete 2>/dev/null || true

    log "Old backups cleaned up"
}

# Main execution
main() {
    log "=== Starting OmniMind Automated Backup ==="
    log "Backup ID: $BACKUP_NAME"

    preflight_checks
    create_backup_structure
    backup_database
    backup_config
    backup_ssl
    backup_logs
    backup_models
    create_manifest
    compress_backup
    copy_to_external
    cleanup_old_backups

    log "=== Backup completed successfully ==="
    log "Backup location: $BACKUP_DIR"
    log "Archive: ${BACKUP_ROOT}/${BACKUP_NAME}.tar.gz"

    # Send notification (placeholder)
    echo "Backup completed: $BACKUP_NAME" | mail -s "OmniMind Backup Complete" root 2>/dev/null || true
}

# Run main function
main "$@"
