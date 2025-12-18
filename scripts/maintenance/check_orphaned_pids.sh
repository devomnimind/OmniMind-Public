#!/usr/bin/env bash
# Script auxiliar: verificar PIDs órfãos
# Executado periodicamente via cron

set -euo pipefail

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
LOG_FILE="${PROJECT_ROOT}/logs/orphaned_pids.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log "🔍 Verificando PIDs órfãos..."

ORPHANED_COUNT=0

for pidfile in "${PROJECT_ROOT}/logs"/*.pid; do
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile" 2>/dev/null || echo "")
        if [ -n "$PID" ]; then
            if ! ps -p "$PID" > /dev/null 2>&1; then
                log "   ⚠️  PID órfão encontrado: $(basename "$pidfile") (PID $PID)"
                rm -f "$pidfile"
                ORPHANED_COUNT=$((ORPHANED_COUNT + 1))
            fi
        fi
    fi
done

if [ $ORPHANED_COUNT -eq 0 ]; then
    log "   ✅ Nenhum PID órfão encontrado"
else
    log "   🧹 Removidos $ORPHANED_COUNT PIDs órfãos"
fi
