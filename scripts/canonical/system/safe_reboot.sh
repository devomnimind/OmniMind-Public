#!/bin/bash
# Safe Reboot Script for OmniMind
# Stops all services gracefully before reboot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
LOG_FILE="/tmp/reboot_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_step() {
    log "${BLUE}[STEP]${NC} $1"
}

log_success() {
    log "${GREEN}[✓]${NC} $1"
}

log_warning() {
    log "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    log "${RED}[✗]${NC} $1"
}

# ============================================================================
# Main Reboot Procedure
# ============================================================================

main() {
    log ""
    log "${BLUE}════════════════════════════════════════════════════════════${NC}"
    log "${BLUE}  OmniMind Safe Reboot Procedure${NC}"
    log "${BLUE}════════════════════════════════════════════════════════════${NC}"
    log ""

    # Phase 1: Collect System State
    log_step "PHASE 1: Collecting system state..."

    log_step "System info:"
    uname -a | tee -a "$LOG_FILE"

    log_step "Uptime:"
    uptime | tee -a "$LOG_FILE"

    log_step "Active services:"
    systemctl list-units --type=service --state=active --no-pager | \
        grep -E 'omnimind|docker' | tee -a "$LOG_FILE" || log_warning "No OmniMind services found"

    log_success "System state collected in $LOG_FILE"
    echo ""

    # Phase 2: Stop Services
    log_step "PHASE 2: Stopping services..."

    # Stop docker-compose
    if [[ -f "$PWD/deploy/docker-compose.yml" ]]; then
        log_step "Stopping docker-compose..."
        docker-compose -f deploy/docker-compose.yml down 2>&1 | tee -a "$LOG_FILE" || true
        log_success "docker-compose stopped"
    fi

    # Stop systemd services
    log_step "Stopping systemd services..."
    systemctl list-units --type=service --state=active --no-pager | \
        grep omnimind | awk '{print $1}' | while read service; do
            log_step "Stopping: $service"
            sudo systemctl stop "$service" 2>&1 | tee -a "$LOG_FILE" || true
        done
    log_success "systemd services stopped"

    # Kill remaining Python processes
    log_step "Checking for remaining Python processes..."
    python_count=$(ps aux | grep -E 'python|uvicorn' | grep -v grep | wc -l)
    if [[ $python_count -gt 0 ]]; then
        log_warning "Found $python_count Python processes, attempting graceful stop..."
        pkill -TERM -f "python|uvicorn" || true
        sleep 3

        # Force kill if still running
        remaining=$(ps aux | grep -E 'python|uvicorn' | grep -v grep | wc -l)
        if [[ $remaining -gt 0 ]]; then
            log_warning "Force killing $remaining remaining processes..."
            pkill -KILL -f "python|uvicorn" || true
        fi
    fi
    log_success "Python processes cleaned"

    echo ""

    # Phase 3: Sync and Cleanup
    log_step "PHASE 3: Syncing and cleanup..."

    log_step "Syncing buffers..."
    sync
    sudo sync
    log_success "Buffers synced"

    log_step "Clearing caches..."
    sudo sysctl -w vm.drop_caches=3 2>&1 | tee -a "$LOG_FILE" || true
    log_success "Caches cleared"

    sleep 2

    echo ""

    # Phase 4: Final Verification
    log_step "PHASE 4: Final verification..."

    active_services=$(systemctl list-units --type=service --state=active | grep -c omnimind || echo 0)
    docker_containers=$(docker ps -q | wc -l)
    python_procs=$(ps aux | grep -E 'python|uvicorn' | grep -v grep | wc -l)

    log "Active OmniMind services: $active_services"
    log "Docker containers running: $docker_containers"
    log "Python processes: $python_procs"

    if [[ $active_services -eq 0 ]] && [[ $docker_containers -eq 0 ]] && [[ $python_procs -eq 0 ]]; then
        log_success "All OmniMind services stopped"
    else
        log_warning "Some services still running (may be system services)"
    fi

    echo ""

    # Phase 5: Reboot
    log_step "PHASE 5: Reboot preparation..."

    log_success "System ready for reboot"
    log ""
    log "Log file: $LOG_FILE"
    log ""

    echo -e "${YELLOW}Reboot in 10 seconds... Press Ctrl+C to cancel${NC}"
    sleep 10

    log_step "Initiating reboot..."
    sudo reboot
}

# Error handling
trap 'log_error "Reboot cancelled"; exit 1' INT

# Run main
main "$@"
