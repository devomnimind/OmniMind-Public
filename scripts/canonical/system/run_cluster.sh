#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Calcular PROJECT_ROOT de forma robusta (pode ser chamado de qualquer lugar)
# Se PROJECT_ROOT foi passado como argumento, usar
if [ -n "${PROJECT_ROOT:-}" ]; then
    CLUSTER_PROJECT_ROOT="$PROJECT_ROOT"
else
    # Procurar pela raiz do projeto
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    while [ "$SCRIPT_DIR" != "/" ]; do
        if [ -f "$SCRIPT_DIR/.env" ] || [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
            CLUSTER_PROJECT_ROOT="$SCRIPT_DIR"
            break
        fi
        SCRIPT_DIR="$(dirname "$SCRIPT_DIR")"
    done

    if [ -z "$CLUSTER_PROJECT_ROOT" ]; then
        # Fallback: subir 3 níveis de scripts/canonical/system/
        CLUSTER_PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
    fi
fi

# Mover para project root ANTES de qualquer comando
cd "$CLUSTER_PROJECT_ROOT" || {
    echo -e "${RED}❌ Falha ao entrar em $CLUSTER_PROJECT_ROOT${NC}"
    exit 1
}

echo -e "${GREEN}🚀 Iniciando OmniMind Backend Cluster...${NC}"
echo "   Projeto: $CLUSTER_PROJECT_ROOT"
echo "   Diretório: $(pwd)"

# Kill existing python processes related to main.py
pkill -f "python web/backend/main.py" 2>/dev/null || true
pkill -f "uvicorn src.api.main:app" 2>/dev/null || true
pkill -f "uvicorn web.backend.main:app" 2>/dev/null || true

# Export PYTHONPATH
export PYTHONPATH="$CLUSTER_PROJECT_ROOT:${PYTHONPATH}"

# Configuração de Workers e Backends (com valores padrão otimizados)
# OMNIMIND_WORKERS: número de workers por backend (padrão 2 = estável + rápido)
# OMNIMIND_BACKENDS: quantos backends rodar (padrão 3 = HA cluster)
# OMNIMIND_WORKERS_VALIDATION: workers durante validação científica (padrão 2 = consistente com produção)
export OMNIMIND_WORKERS="${OMNIMIND_WORKERS:-2}"
export OMNIMIND_BACKENDS="${OMNIMIND_BACKENDS:-3}"
export OMNIMIND_WORKERS_VALIDATION="${OMNIMIND_WORKERS_VALIDATION:-2}"

# Create logs directory if it doesn't exist
mkdir -p logs
chmod 755 logs 2>/dev/null || true

echo "Starting OmniMind Backend Cluster..."
echo -e "${GREEN}⚙️  Configuração:${NC}"
echo "   Workers por backend: $OMNIMIND_WORKERS (OMNIMIND_WORKERS)"
echo "   Backends ativos: $OMNIMIND_BACKENDS (OMNIMIND_BACKENDS)"
echo "   Workers em validação: $OMNIMIND_WORKERS_VALIDATION (OMNIMIND_WORKERS_VALIDATION)"
echo ""

# Start Primary Instance (Port 8000)
if [ "$OMNIMIND_BACKENDS" -ge 1 ]; then
    echo -e "${GREEN}▶ Iniciando Primary (Port 8000)...${NC}"
    nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --workers "$OMNIMIND_WORKERS" > logs/backend_8000.log 2>&1 &
    PID_8000=$!
    echo $PID_8000 > logs/backend_8000.pid
    echo "✓ Primary iniciado com PID $PID_8000 (workers: $OMNIMIND_WORKERS)"
    echo "   Log: tail -f logs/backend_8000.log"
    sleep 1
fi

# Start Secondary Instance (Port 8080)
if [ "$OMNIMIND_BACKENDS" -ge 2 ]; then
    echo -e "${GREEN}▶ Iniciando Secondary (Port 8080)...${NC}"
    nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8080 --workers "$OMNIMIND_WORKERS" > logs/backend_8080.log 2>&1 &
    PID_8080=$!
    echo $PID_8080 > logs/backend_8080.pid
    echo "✓ Secondary iniciado com PID $PID_8080 (workers: $OMNIMIND_WORKERS)"
    echo "   Log: tail -f logs/backend_8080.log"
    sleep 1
fi

# Start Fallback Instance (Port 3001)
if [ "$OMNIMIND_BACKENDS" -ge 3 ]; then
    echo -e "${GREEN}▶ Iniciando Fallback (Port 3001)...${NC}"
    nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 3001 --workers "$OMNIMIND_WORKERS" > logs/backend_3001.log 2>&1 &
    PID_3001=$!
    echo $PID_3001 > logs/backend_3001.pid
    echo "✓ Fallback iniciado com PID $PID_3001 (workers: $OMNIMIND_WORKERS)"
    echo "   Log: tail -f logs/backend_3001.log"
    sleep 1
fi

echo -e "${GREEN}✅ Cluster rodando${NC}"
echo "   Logs disponíveis em: logs/backend_*.log"
echo "   Monitor com: tail -f logs/backend_*.log"
echo ""
echo "   PIDs:"
echo "     Primary (8000):  $PID_8000"
echo "     Secondary (8080): $PID_8080"
echo "     Fallback (3001):  $PID_3001"
