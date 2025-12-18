#!/usr/bin/env bash
# Limpeza automática de dados antigos do OmniMind
# Para executar via cron: 0 3 * * * /home/fahbrain/projects/omnimind/scripts/maintenance/cleanup_old_data.sh

set -euo pipefail

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
LOG_FILE="${PROJECT_ROOT}/logs/maintenance_cleanup.log"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "🧹 Iniciando limpeza automática de dados antigos..."

# 1. Remover alertas antigos (> 30 dias)
if [ -d "${PROJECT_ROOT}/data/alerts" ]; then
    ALERTS_REMOVED=$(find "${PROJECT_ROOT}/data/alerts" -name "*.json" -type f -mtime +30 -delete -print | wc -l)
    log "   ✓ Removidos ${ALERTS_REMOVED} alertas antigos (> 30 dias)"
fi

# 2. Remover dados de stimulation antigos (> 30 dias)
if [ -d "${PROJECT_ROOT}/data/stimulation" ]; then
    STIM_REMOVED=$(find "${PROJECT_ROOT}/data/stimulation" -name "*.json" -type f -mtime +30 -delete -print | wc -l)
    log "   ✓ Removidos ${STIM_REMOVED} arquivos de stimulation antigos (> 30 dias)"
fi

# 3. Remover incidentes forenses antigos (> 60 dias)
if [ -d "${PROJECT_ROOT}/data/forensics/incidents" ]; then
    INCIDENTS_REMOVED=$(find "${PROJECT_ROOT}/data/forensics/incidents" -name "*.json" -type f -mtime +60 -delete -print | wc -l)
    log "   ✓ Removidos ${INCIDENTS_REMOVED} incidentes forenses antigos (> 60 dias)"
fi

# 4. Comprimir logs de módulos antigos (> 7 dias)
if [ -d "${PROJECT_ROOT}/logs/modules" ]; then
    find "${PROJECT_ROOT}/logs/modules" -name "*.jsonl" -type f -mtime +7 ! -name "*.gz" -exec gzip {} \;
    log "   ✓ Comprimidos logs de módulos antigos (> 7 dias)"
fi

# 5. Remover arquivos PID órfãos (processos que não existem mais)
for pidfile in "${PROJECT_ROOT}/logs"/*.pid; do
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile" 2>/dev/null || echo "")
        if [ -n "$PID" ]; then
            if ! ps -p "$PID" > /dev/null 2>&1; then
                rm -f "$pidfile"
                log "   ✓ Removido PID órfão: $(basename "$pidfile")"
            fi
        fi
    fi
done

# 6. Verificar uso de disco
DISK_USAGE=$(du -sh "${PROJECT_ROOT}" | cut -f1)
log "📊 Uso total de disco do projeto: ${DISK_USAGE}"

# 7. Remover logs de rotação antigos comprimidos (> 90 dias)
find "${PROJECT_ROOT}/logs" -name "*.log.*.gz" -type f -mtime +90 -delete
log "   ✓ Removidos logs comprimidos antigos (> 90 dias)"

log "✅ Limpeza concluída com sucesso"
