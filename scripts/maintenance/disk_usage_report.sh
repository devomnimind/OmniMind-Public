#!/usr/bin/env bash
# Relatório semanal de uso de disco
# Executado via cron nos domingos às 4 AM

set -euo pipefail

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
REPORT_FILE="${PROJECT_ROOT}/reports/disk_usage_$(date '+%Y%m%d').txt"

mkdir -p "${PROJECT_ROOT}/reports"

{
    echo "=== OmniMind Disk Usage Report ==="
    echo "Data: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    echo "## Uso total do projeto:"
    du -sh "${PROJECT_ROOT}"
    echo ""

    echo "## Top 10 diretórios maiores:"
    du -sh "${PROJECT_ROOT}"/* 2>/dev/null | sort -hr | head -n 10
    echo ""

    echo "## Detalhamento de logs/:"
    du -sh "${PROJECT_ROOT}/logs"/* 2>/dev/null | sort -hr | head -n 10
    echo ""

    echo "## Detalhamento de data/:"
    du -sh "${PROJECT_ROOT}/data"/* 2>/dev/null | sort -hr | head -n 10
    echo ""

    echo "## Espaço livre na partição /home:"
    df -h /home | tail -n 1
    echo ""

    echo "## Arquivos grandes (> 50MB):"
    find "${PROJECT_ROOT}" -type f -size +50M -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $9}' | head -n 20

} > "$REPORT_FILE"

echo "📊 Relatório de disco salvo em: $REPORT_FILE"
cat "$REPORT_FILE"
