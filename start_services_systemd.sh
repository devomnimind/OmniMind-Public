#!/bin/bash

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

# Configurar PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT/web:$PROJECT_ROOT"

# Carregar .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Ativar venv
source "$PROJECT_ROOT/.venv/bin/activate"

# Limpar porta 8000
fuser -k 8000/tcp 2>/dev/null || true
sleep 1

# Iniciar Backend
cd "$PROJECT_ROOT"
exec "$PROJECT_ROOT/.venv/bin/uvicorn" web.backend.main:app --host 0.0.0.0 --port 8000 --log-level info
