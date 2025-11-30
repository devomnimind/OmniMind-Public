#!/bin/bash
# OmniMind Backend Startup Script
# Starts FastAPI backend on port 8000 with real metrics

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

echo "🚀 Iniciando OmniMind Backend..."

# Kill any existing uvicorn processes
pkill -9 -f "uvicorn web.backend" 2>/dev/null || true
sleep 1

# Clear port if needed
fuser -k 8000/tcp 2>/dev/null || true
sleep 1

# Load environment variables from .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
    echo "✅ Variáveis de ambiente carregadas"
else
    echo "⚠️  .env não encontrado"
fi

# Set Python path
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT/web:$PROJECT_ROOT"

# Start backend
echo "🌐 Iniciando servidor na porta 8000..."
exec "$PROJECT_ROOT/.venv/bin/python" -m uvicorn web.backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
