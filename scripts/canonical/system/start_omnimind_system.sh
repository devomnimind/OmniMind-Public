#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Sistema OmniMind Completo...${NC}"

# 🔧 CRÍTICO: Ativar venv ANTES de qualquer import Python
# PROJECT_ROOT deve apontar para a raiz do projeto (1 nível acima de scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✅ Venv ativado: $VIRTUAL_ENV"
else
    echo "⚠️  Venv não encontrado em $PROJECT_ROOT/.venv"
fi

# 🔒 SEGURANÇA: Bloquear porta 4444 (comumente usada por malware)
# Documentado em: docs/SECURITY_PORT_4444_BLOCK.md
echo "🔒 Aplicando bloqueio de segurança (porta 4444)..."
if command -v iptables &> /dev/null; then
    # Verificar se regras já existem
    if ! sudo iptables -C INPUT -p tcp --dport 4444 -j DROP 2>/dev/null; then
        sudo iptables -A INPUT -p tcp --dport 4444 -j DROP 2>/dev/null || true
        sudo iptables -A OUTPUT -p tcp --dport 4444 -j DROP 2>/dev/null || true
        sudo iptables -A INPUT -p udp --dport 4444 -j DROP 2>/dev/null || true
        sudo iptables -A OUTPUT -p udp --dport 4444 -j DROP 2>/dev/null || true
        echo "✅ Porta 4444 bloqueada (segurança)"
    else
        echo "✅ Porta 4444 já está bloqueada"
    fi
else
    echo "⚠️  iptables não disponível - porta 4444 não bloqueada"
fi

# 🔧 GPU Configuration - Kali Linux Native Paths
echo "🔧 Configurando ambiente GPU (Kali Native)..."
# No Kali/Debian, CUDA é integrado em /usr
export CUDA_HOME="/usr"
export CUDA_path="/usr"
# A libcuda.so.1 está em /usr/lib/x86_64-linux-gnu/
# Adicionar ao LD_LIBRARY_PATH explicitamente para garantir que PyTorch a encontre
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
export CUDA_VISIBLE_DEVICES="0"
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"
# export CUDA_LAUNCH_BLOCKING="1" # Descomente se precisar debugar inicialização síncrona

# Garantir permissão de execução no run_cluster
chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh" 2>/dev/null || true

# Lógica de Autenticação Dinâmica (Soberania Local) - UNIFICADA PARA CLUSTER
# Gera credenciais UMA VEZ e exporta para todos os subprocessos
DASH_USER=""
DASH_PASS=""
AUTH_FILE="$PROJECT_ROOT/config/dashboard_auth.json"

# 1. Tentar ler do arquivo gerado anteriormente ou preservar sessão
if [ -f "$AUTH_FILE" ]; then
    # Extração segura
    DASH_USER=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('user', ''))" 2>/dev/null)
    DASH_PASS=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('pass', ''))" 2>/dev/null)
fi

# 2. Fallback para .env
if [ -z "$DASH_USER" ] && [ -f "$PROJECT_ROOT/.env" ]; then
    DASH_USER=$(grep "^OMNIMIND_DASHBOARD_USER=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    DASH_PASS=$(grep "^OMNIMIND_DASHBOARD_PASS=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'")
fi

# 3. Gerar novas se não existirem (e salvar no arquivo para o backend usar a mesma)
if [ -z "$DASH_USER" ]; then
    # SOBERANIA LOCAL REAL: Gerar credenciais aleatórias fortes a cada sessão
    # Isso garante segurança e obriga o uso correto do fluxo de autenticação
    DASH_USER="admin"
    DASH_PASS=$(openssl rand -base64 12)

    # Salvar no JSON para persistência e leitura pelo backend
    echo "{\"user\": \"$DASH_USER\", \"pass\": \"$DASH_PASS\"}" > "$AUTH_FILE"
    echo "🔑 Novas credenciais SOBERANAS geradas em $AUTH_FILE"
fi

# EXPORTAR PARA O AMBIENTE - ISSO GARANTE QUE TODOS OS BACKENDS USEM A MESMA SENHA
export OMNIMIND_DASHBOARD_USER="$DASH_USER"
export OMNIMIND_DASHBOARD_PASS="$DASH_PASS"
export OMNIMIND_DASHBOARD_AUTH_FILE="$AUTH_FILE"

echo -e "${GREEN}🔐 Credenciais Unificadas do Cluster:${NC}"
echo "   User: $DASH_USER"
echo "   Pass: $DASH_PASS"

# 1. Limpeza
echo "🧹 Limpando processos antigos..."
pkill -f "python web/backend/main.py"
pkill -f "uvicorn web.backend.main:app"
pkill -f "python -m src.main"
pkill -f "vite"
pkill -f "bpftrace.*monitor_mcp_bpf" || true
sleep 2

# 2. Iniciar Backend Cluster (FASE 1: ESSENCIAIS)
echo -e "${GREEN}🔌 Iniciando Backend Cluster (Fase 1: Essenciais)...${NC}"

# SEMPRE reiniciar o backend para garantir serviços novos
# Mesmo que já esteja rodando, fazer restart para confirmar serviços atualizados
if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend já está rodando na porta 8000${NC}"
    echo "   Reiniciando para garantir serviços novos..."
    pkill -f "uvicorn web.backend.main:app" || true
    pkill -f "python web/backend/main.py" || true
    sleep 3
fi

"$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh"

# Aguardar Backend subir
# ⚠️ CRÍTICO: Uvicorn + Orchestrator + SecurityAgent podem levar 30-60s
# Aumentado de 10s para 40s para garantir inicialização completa
echo "⏳ Aguardando Backend inicializar (40s - Orchestrator + SecurityAgent)..."
sleep 40

# Verificar Health Check (usando o endpoint /health/ que agora é servido pelo router)
# Nota: O endpoint raiz /health foi removido do main.py, agora é /health/ (com barra) ou /health (se o router permitir sem barra)
# O router tem prefix="/health" e @router.get("/"). Então é /health/
if curl -s http://localhost:8000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Backend (Primary) Online!${NC}"
elif curl -s http://localhost:8000/api/v1/status > /dev/null; then
    echo -e "${GREEN}✅ Backend (Primary) Online (via Status API)!${NC}"
else
    echo -e "${RED}❌ Falha ao conectar no Backend (Port 8000). Verifique logs/backend_8000.log${NC}"
    tail -n 10 "$PROJECT_ROOT/logs/backend_8000.log" 2>/dev/null || echo "   Log não encontrado"
    exit 1
fi

# FASE 2: SECUNDÁRIOS (após 30s dos essenciais)
echo -e "${GREEN}⏰ Aguardando 30s antes de iniciar serviços secundários...${NC}"
echo "   (Garantindo que serviços essenciais estejam totalmente inicializados)"
sleep 30

# 2.1. Iniciar MCP Servers (FASE 2: SECUNDÁRIOS)
echo -e "${GREEN}🌐 Iniciando MCP Servers...${NC}"
cd "$PROJECT_ROOT"

# Verificar se MCP Orchestrator já está rodando
if pgrep -f "run_mcp_orchestrator.py" > /dev/null || pgrep -f "mcp_orchestrator" > /dev/null; then
    echo -e "${YELLOW}⚠️  MCP Orchestrator já está rodando${NC}"
    MCP_ORCHESTRATOR_PID=$(pgrep -f "run_mcp_orchestrator.py" | head -1)
    echo "   Usando PID existente: $MCP_ORCHESTRATOR_PID"
else
    # Garantir permissão de execução
    chmod +x "$PROJECT_ROOT/scripts/canonical/system/start_mcp_servers.sh" 2>/dev/null || true
    chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" 2>/dev/null || true

    # Iniciar MCP Orchestrator
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" > "$PROJECT_ROOT/logs/mcp_orchestrator.log" 2>&1 &
    MCP_ORCHESTRATOR_PID=$!
    echo $MCP_ORCHESTRATOR_PID > "$PROJECT_ROOT/logs/mcp_orchestrator.pid"
    echo "✓ MCP Orchestrator iniciado (PID $MCP_ORCHESTRATOR_PID)"
    echo "   Log: tail -f logs/mcp_orchestrator.log"
    sleep 5
fi

# 3. Iniciar Ciclo Principal com Autopoiese (Phase 23)
echo -e "${GREEN}🔄 Iniciando Ciclo Principal OmniMind (Fase 23: Autopoiese + Integração Real-time)...${NC}"
cd "$PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT/logs" "$PROJECT_ROOT/data/autopoietic/synthesized_code" "$PROJECT_ROOT/data/monitor"

# Verificar se já está rodando
if [ -f "$PROJECT_ROOT/logs/main_cycle.pid" ]; then
    OLD_PID=$(cat "$PROJECT_ROOT/logs/main_cycle.pid" 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ciclo Principal já está rodando (PID $OLD_PID)${NC}"
        MAIN_CYCLE_PID=$OLD_PID
    else
        # Iniciar ciclo principal em background (Rhizome + Consciência + Autopoiese)
        nohup python -m src.main > "$PROJECT_ROOT/logs/main_cycle.log" 2>&1 &
        MAIN_CYCLE_PID=$!
        echo $MAIN_CYCLE_PID > "$PROJECT_ROOT/logs/main_cycle.pid"
        echo "✓ Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
    fi
else
    # Iniciar ciclo principal em background (Rhizome + Consciência + Autopoiese)
    nohup python -m src.main > "$PROJECT_ROOT/logs/main_cycle.log" 2>&1 &
    MAIN_CYCLE_PID=$!
    echo $MAIN_CYCLE_PID > "$PROJECT_ROOT/logs/main_cycle.pid"
    echo "✓ Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
fi
echo "   Log: tail -f logs/main_cycle.log"
sleep 3

# 4. Iniciar Daemon
echo -e "${GREEN}🤖 Inicializando OmniMind Daemon...${NC}"
cd "$PROJECT_ROOT"

# Fazer requisição com as credenciais descobertas
if [ -n "$OMNIMIND_DASHBOARD_PASS" ]; then
    curl -X POST http://localhost:8000/daemon/start \
      -u "${OMNIMIND_DASHBOARD_USER}:${OMNIMIND_DASHBOARD_PASS}" \
      > "$PROJECT_ROOT/logs/daemon_start.log" 2>&1 &
    DAEMON_START_PID=$!
    echo "✓ Daemon start request enviado (PID $DAEMON_START_PID)"
else
    echo -e "${YELLOW}⚠️  Senha não encontrada, pulando inicialização do daemon via API${NC}"
fi
sleep 2

# 5. Iniciar Frontend
echo -e "${GREEN}🎨 Iniciando Frontend...${NC}"
cd "$PROJECT_ROOT"

# Verificar se diretório frontend existe
if [ ! -d "web/frontend" ]; then
    echo -e "${RED}❌ Diretório web/frontend não encontrado!${NC}"
    echo "   Verificando estrutura do projeto..."
    ls -la web/ 2>&1 | head -10
    FRONTEND_PID=""
else
    cd web/frontend

    # Verificar se node_modules existe, se não, instalar
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependências do Frontend..."
        npm install
    fi

    # Verificar se já está rodando
    if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
        OLD_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid" 2>/dev/null || echo "")
        if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Frontend já está rodando (PID $OLD_PID)${NC}"
            FRONTEND_PID=$OLD_PID
        else
            nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
            FRONTEND_PID=$!
            echo $FRONTEND_PID > "$PROJECT_ROOT/logs/frontend.pid"
            echo "✓ Frontend iniciado (PID $FRONTEND_PID)"
        fi
    else
        nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "$PROJECT_ROOT/logs/frontend.pid"
        echo "✓ Frontend iniciado (PID $FRONTEND_PID)"
    fi
fi

# Voltar para raiz do projeto
cd "$PROJECT_ROOT"

# 6. Verificação Final
echo -e "${GREEN}🔍 Verificando status do sistema...${NC}"
sleep 5

if [ -n "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend rodando (PID $FRONTEND_PID)${NC}"
    echo "   Acesse: http://localhost:3000"
else
    echo -e "${RED}❌ Frontend falhou ao iniciar. Verifique logs/frontend.log${NC}"
    if [ -f "$PROJECT_ROOT/logs/frontend.log" ]; then
        tail -n 20 "$PROJECT_ROOT/logs/frontend.log"
    else
        echo "   Arquivo de log não encontrado"
    fi
fi

# FASE 3: MONITORAMENTO (após 15s dos serviços principais)
# Aguardar estabilização completa antes de iniciar serviços de monitoramento
echo -e "${GREEN}⏰ Aguardando 15s antes de iniciar serviços de monitoramento...${NC}"
echo "   (Garantindo que todos os serviços principais estejam totalmente estáveis)"
sleep 15

# 7. Iniciar Observer Service (FASE 3: MONITORAMENTO - após serviços principais)
echo -e "${GREEN}📊 Iniciando Observer Service (Métricas de Longo Prazo)...${NC}"
cd "$PROJECT_ROOT"

# Verificar se já está rodando
if [ -f "$PROJECT_ROOT/logs/observer_service.pid" ]; then
    OLD_PID=$(cat "$PROJECT_ROOT/logs/observer_service.pid" 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Observer Service já está rodando (PID $OLD_PID)${NC}"
        OBSERVER_PID=$OLD_PID
    else
        # Criar diretório de logs se não existir
        mkdir -p "$PROJECT_ROOT/data/long_term_logs" "$PROJECT_ROOT/logs"

        # Garantir permissão de execução no script
        chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" 2>/dev/null || true

        # Iniciar Observer Service em background usando script wrapper
        nohup python "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" > "$PROJECT_ROOT/logs/observer_service.log" 2>&1 &
        OBSERVER_PID=$!
        echo $OBSERVER_PID > "$PROJECT_ROOT/logs/observer_service.pid"
        echo "✓ Observer Service iniciado (PID $OBSERVER_PID)"
        echo "   Log: tail -f logs/observer_service.log"
        echo "   Métricas: data/long_term_logs/omnimind_metrics.jsonl"
        sleep 3  # Aguardar inicialização
    fi
else
    # Criar diretório de logs se não existir
    mkdir -p "$PROJECT_ROOT/data/long_term_logs" "$PROJECT_ROOT/logs"

    # Garantir permissão de execução no script
    chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" 2>/dev/null || true

    # Iniciar Observer Service em background usando script wrapper
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" > "$PROJECT_ROOT/logs/observer_service.log" 2>&1 &
    OBSERVER_PID=$!
    echo $OBSERVER_PID > "$PROJECT_ROOT/logs/observer_service.pid"
    echo "✓ Observer Service iniciado (PID $OBSERVER_PID)"
    echo "   Log: tail -f logs/observer_service.log"
    echo "   Métricas: data/long_term_logs/omnimind_metrics.jsonl"
    sleep 3  # Aguardar inicialização
fi

# 8. Iniciar eBPF Monitor Contínuo (FASE 3: MONITORAMENTO AVANÇADO)
echo -e "${GREEN}📊 Iniciando eBPF Monitor Contínuo...${NC}"

# Voltar para a raiz do projeto para encontrar scripts/canonical/system/secure_run.py
cd "$PROJECT_ROOT"

if command -v bpftrace &> /dev/null; then
    EBPF_LOG="$PROJECT_ROOT/logs/ebpf_monitor.log"
    mkdir -p "$PROJECT_ROOT/logs"

    # Garantir permissões no arquivo de log se ele existir
    if [ -f "$EBPF_LOG" ]; then
        # Tentar mudar dono para usuário atual se possível, ou remover se falhar
        if ! touch "$EBPF_LOG" 2>/dev/null; then
            echo "⚠️  Sem permissão de escrita em $EBPF_LOG. Tentando remover com sudo..."
            sudo rm -f "$EBPF_LOG"
        fi
    fi

    # Parar eBPF anterior
    python3 "$PROJECT_ROOT/scripts/canonical/system/secure_run.py" pkill -f "bpftrace.*monitor_mcp_bpf" || true
    sleep 1
    # Iniciar em background
    # Nota: secure_run.py já lida com sudo -n
    python3 "$PROJECT_ROOT/scripts/canonical/system/secure_run.py" bpftrace "$PROJECT_ROOT/scripts/canonical/system/monitor_mcp_bpf.bt" > "${EBPF_LOG}" 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ eBPF Monitor ativo${NC}"
    echo "   Log: tail -f ${EBPF_LOG}"
else
    echo -e "${RED}⚠️  bpftrace não encontrado. Instale com: sudo apt install bpftrace${NC}"
fi

echo -e "${GREEN}✨ Sistema OmniMind Reiniciado!${NC}"
echo ""
echo -e "${GREEN}📋 SERVIÇOS ATIVOS:${NC}"
echo "   Backend Cluster: Ports 8000, 8080, 3001"
if [ -n "${MCP_ORCHESTRATOR_PID:-}" ]; then
    echo "   MCP Orchestrator: PID ${MCP_ORCHESTRATOR_PID}"
fi
echo "   Ciclo Principal (Autopoiese Phase 23): PID $MAIN_CYCLE_PID"
if [ -n "${OBSERVER_PID:-}" ]; then
    echo "   Observer Service: PID ${OBSERVER_PID}"
fi
echo "   Frontend: http://localhost:3000"
echo ""
echo -e "${GREEN}🔐 CREDENCIAIS DA SESSÃO ATUAL (CLUSTER UNIFICADO):${NC}"
echo -e "   User: ${GREEN}${OMNIMIND_DASHBOARD_USER}${NC}"
echo -e "   Pass: ${GREEN}${OMNIMIND_DASHBOARD_PASS}${NC}"
echo "   (Use estas credenciais para logar no Dashboard)"
echo ""
echo -e "${GREEN}📊 MONITORAMENTO:${NC}"
echo "   eBPF Monitor: logs/ebpf_monitor.log"
if [ -n "${OBSERVER_PID:-}" ]; then
    echo "   Observer Service: logs/observer_service.log"
    echo "   Métricas Longo Prazo: data/long_term_logs/omnimind_metrics.jsonl"
    echo "   Heartbeat: data/long_term_logs/heartbeat.status"
fi
echo "   Logs Directory: logs/"
echo ""
echo "📊 Autopoiese Phase 23 (Active):"
echo "   - Componentes sintetizados: data/autopoietic/synthesized_code/"
echo "   - Histórico de ciclos: data/autopoietic/cycle_history.jsonl"
echo "   - Log do ciclo: logs/main_cycle.log"
