#!/bin/bash
# Script de inicialização ESSENCIAL do OmniMind
# Fase 1: Apenas serviços críticos (Backend + Orchestrator)
# Autor: Fabrício da Silva + assistência de IA

# Não usar set -e para não sair no loop de monitoramento
set -u  # Apenas falhar em variáveis não definidas

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Serviços Essenciais OmniMind (Fase 1)...${NC}"

# 🔧 CRÍTICO: Ativar venv ANTES de qualquer import Python
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✅ Venv ativado: $VIRTUAL_ENV"
else
    echo -e "${RED}❌ Venv não encontrado em $PROJECT_ROOT/.venv${NC}"
    exit 1
fi

# 🔧 GPU Configuration - Kali Linux Native Paths
export CUDA_HOME="/usr"
export CUDA_PATH="/usr"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
export CUDA_VISIBLE_DEVICES="0"
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"

# Lógica de Autenticação Dinâmica (Soberania Local)
DASH_USER=""
DASH_PASS=""
AUTH_FILE="$PROJECT_ROOT/config/dashboard_auth.json"

# 1. Tentar ler do arquivo gerado anteriormente
if [ -f "$AUTH_FILE" ]; then
    DASH_USER=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('user', ''))" 2>/dev/null || echo "")
    DASH_PASS=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('pass', ''))" 2>/dev/null || echo "")
fi

# 2. Fallback para .env
if [ -z "$DASH_USER" ] && [ -f "$PROJECT_ROOT/.env" ]; then
    DASH_USER=$(grep "^OMNIMIND_DASHBOARD_USER=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "")
    DASH_PASS=$(grep "^OMNIMIND_DASHBOARD_PASS=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "")
fi

# 3. Gerar novas se não existirem
if [ -z "$DASH_USER" ]; then
    DASH_USER="admin"
    DASH_PASS=$(openssl rand -base64 12)
    echo "{\"user\": \"$DASH_USER\", \"pass\": \"$DASH_PASS\"}" > "$AUTH_FILE"
    echo "🔑 Novas credenciais SOBERANAS geradas em $AUTH_FILE"
fi

# EXPORTAR PARA O AMBIENTE
export OMNIMIND_DASHBOARD_USER="$DASH_USER"
export OMNIMIND_DASHBOARD_PASS="$DASH_PASS"
export OMNIMIND_DASHBOARD_AUTH_FILE="$AUTH_FILE"

echo -e "${GREEN}🔐 Credenciais Essenciais:${NC}"
echo "   User: $DASH_USER"

# 1. Verificar se serviços já estão rodando
echo "🔍 Verificando serviços existentes..."
if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend já está rodando na porta 8000${NC}"
    echo "   Pulando inicialização do backend..."
else
    # 2. Limpeza apenas de processos relacionados
    echo "🧹 Limpando processos antigos do backend..."
    pkill -f "uvicorn web.backend.main:app" || true
    pkill -f "python web/backend/main.py" || true
    sleep 2

    # 3. Iniciar Backend Cluster (ESSENCIAL)
    echo -e "${GREEN}🔌 Iniciando Backend Cluster (Essencial)...${NC}"
    cd "$PROJECT_ROOT"
    chmod +x scripts/canonical/system/run_cluster.sh
    ./scripts/canonical/system/run_cluster.sh

    # 4. Aguardar Backend subir (ESSENCIAL)
    echo "⏳ Aguardando Backend inicializar (40s - Orchestrator + SecurityAgent)..."
    sleep 40

    # 5. Verificar Health Check
    if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend (Primary) Online!${NC}"
    elif curl -s http://localhost:8000/api/v1/status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend (Primary) Online (via Status API)!${NC}"
    else
        echo -e "${RED}❌ Falha ao conectar no Backend (Port 8000). Verifique logs/backend_8000.log${NC}"
        tail -n 10 "$PROJECT_ROOT/logs/backend_8000.log" || true
        exit 1
    fi
fi

echo -e "${GREEN}✅ Serviços Essenciais Iniciados!${NC}"
echo "   Backend: http://localhost:8000"
echo "   Logs: logs/backend_*.log"
echo "   Monitorando backend a cada 30s..."

# Criar diretório de logs se não existir
mkdir -p "$PROJECT_ROOT/logs"

# Manter processo vivo (systemd Type=simple)
# Logs serão escritos no journalctl via systemd
while true; do
    # Verificar se backend ainda está rodando
    if ! curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${RED}❌ Backend parou! Reiniciando...${NC}" >&2
        cd "$PROJECT_ROOT"
        chmod +x scripts/canonical/system/run_cluster.sh
        ./scripts/canonical/system/run_cluster.sh || {
            echo -e "${RED}❌ Falha ao reiniciar backend${NC}" >&2
            sleep 10
            continue
        }
        echo "⏳ Aguardando Backend reinicializar (40s)..."
        sleep 40
        
        # Verificar novamente
        if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend reiniciado com sucesso!${NC}"
        else
            echo -e "${RED}❌ Backend não respondeu após reinicialização${NC}" >&2
        fi
    else
        # Backend está rodando - log silencioso a cada 5 minutos
        if [ $(( $(date +%s) % 300 )) -eq 0 ]; then
            echo "✅ Backend está rodando (health check OK)"
        fi
    fi
    sleep 30
done

