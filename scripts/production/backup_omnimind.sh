#!/bin/bash
# Script de Backup Automático para OmniMind
# Executa backup diário com compressão e rotação

set -euo pipefail

BACKUP_DIR="/opt/omnimind/backups"
DATA_DIR="/opt/omnimind/data"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/omnimind_backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "🔄 Iniciando backup OmniMind..."
echo "   Timestamp: $TIMESTAMP"
echo "   Destino: $BACKUP_FILE"

# Criar backup
tar -czf "$BACKUP_FILE" \
    --exclude="$DATA_DIR/test_reports/*" \
    --exclude="$DATA_DIR/metrics/*" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude=".git" \
    --exclude=".pytest_cache" \
    "$DATA_DIR" \
    "/opt/omnimind/config" \
    "/opt/omnimind/src" \
    "/opt/omnimind/scripts" \
    2>/dev/null

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "✅ Backup criado: $BACKUP_SIZE"

# Rotação - remover backups antigos
echo "🧹 Limpando backups antigos (>${RETENTION_DAYS}dias)..."
find "$BACKUP_DIR" -name "omnimind_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Listar backups mantidos
echo "📋 Backups disponíveis:"
ls -lh "$BACKUP_DIR"/omnimind_backup_*.tar.gz 2>/dev/null | tail -5

echo "✅ Backup rotina concluída!"
