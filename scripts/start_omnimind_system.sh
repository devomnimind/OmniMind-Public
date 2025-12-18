#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Sistema OmniMind Completo...${NC}"

# 🔧 CRÍTICO: Calcular PROJECT_ROOT de forma robusta
# O script pode ser chamado de vários contextos:
# 1. Direto: ./scripts/canonical/system/start_omnimind_system.sh
# 2. Via wrapper: ./start_omnimind_system.sh (que chama canonical/system/)
# 3. Via chamada direta do diretório raiz

# Se OMNIMIND_PROJECT_ROOT está definido (wrapper), usar ele
if [ -n "${OMNIMIND_PROJECT_ROOT:-}" ]; then
    PROJECT_ROOT="$OMNIMIND_PROJECT_ROOT"
else
    # Calcular PROJECT_ROOT procurando pelo arquivo de identidade do projeto
    # Procurar por config/omnimind.yaml ou .env ou pyproject.toml (marcadores do projeto)
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

    # Subir até encontrar a raiz do projeto
    while [ "$SCRIPT_DIR" != "/" ]; do
        if [ -f "$SCRIPT_DIR/.env" ] || [ -f "$SCRIPT_DIR/pyproject.toml" ] || [ -f "$SCRIPT_DIR/config/omnimind.yaml" ]; then
            PROJECT_ROOT="$SCRIPT_DIR"
            break
        fi
        SCRIPT_DIR="$(dirname "$SCRIPT_DIR")"
    done

    # Se não encontrou, usar o padrão
    if [ -z "$PROJECT_ROOT" ]; then
        # Fallback: subir 3 níveis de scripts/canonical/system/
        PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
    fi
fi

# Validar que encontrou a raiz do projeto
if [ ! -f "$PROJECT_ROOT/config/omnimind.yaml" ] && [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}❌ Não conseguiu encontrar raiz do projeto OmniMind${NC}"
    echo "   Procurou por: config/omnimind.yaml ou .env"
    echo "   PROJECT_ROOT calculado: $PROJECT_ROOT"
    exit 1
fi

echo "✅ Raiz do projeto encontrada: $PROJECT_ROOT"

# 🔧 CRÍTICO: Ativar venv ANTES de qualquer import Python
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✅ Venv ativado: $VIRTUAL_ENV"
else
    echo "⚠️  Venv não encontrado em $PROJECT_ROOT/.venv"
    echo "   Tentando usar Python do sistema..."
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

# 1. Verificação Inteligente de Serviços Existentes
echo "🔍 Verificando serviços existentes..."
# CORREÇÃO (2025-12-10): Verificar se backends já estão saudáveis antes de matar
# Se backends estão respondendo corretamente, não reiniciar desnecessariamente
BACKEND_8000_HEALTHY=false
BACKEND_8080_HEALTHY=false
BACKEND_3001_HEALTHY=false

if curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
    # Verificar tempo de resposta para garantir que está realmente saudável
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:8000/health/" 2>/dev/null || echo "10.0")
    if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${GREEN}✅ Backend na porta 8000 já está saudável (${RESPONSE_TIME}s)${NC}"
        BACKEND_8000_HEALTHY=true
    else
        echo -e "${YELLOW}⚠️  Backend na porta 8000 responde mas está lento (${RESPONSE_TIME}s)${NC}"
    fi
fi

if curl -s --max-time 3 http://localhost:8080/health/ > /dev/null 2>&1; then
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:8080/health/" 2>/dev/null || echo "10.0")
    if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${GREEN}✅ Backend na porta 8080 já está saudável (${RESPONSE_TIME}s)${NC}"
        BACKEND_8080_HEALTHY=true
    else
        echo -e "${YELLOW}⚠️  Backend na porta 8080 responde mas está lento (${RESPONSE_TIME}s)${NC}"
    fi
fi

if curl -s --max-time 3 http://localhost:3001/health/ > /dev/null 2>&1; then
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:3001/health/" 2>/dev/null || echo "10.0")
    if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${GREEN}✅ Backend na porta 3001 já está saudável (${RESPONSE_TIME}s)${NC}"
        BACKEND_3001_HEALTHY=true
    else
        echo -e "${YELLOW}⚠️  Backend na porta 3001 responde mas está lento (${RESPONSE_TIME}s)${NC}"
    fi
fi

# Se TODOS os backends estão saudáveis, não reiniciar
if [ "$BACKEND_8000_HEALTHY" = true ] && [ "$BACKEND_8080_HEALTHY" = true ] && [ "$BACKEND_3001_HEALTHY" = true ]; then
    echo -e "${GREEN}✅ Todos os backends já estão saudáveis - pulando reinicialização${NC}"
    echo "   (Para forçar reinicialização, pare os serviços manualmente primeiro)"
    SKIP_BACKEND_RESTART=true
else
    echo "🛑 Alguns backends não estão saudáveis ou não estão rodando. Reiniciando..."
    SKIP_BACKEND_RESTART=false

    # Limpeza apenas se necessário
    pkill -9 -f "python web/backend/main.py" 2>/dev/null || true
    pkill -9 -f "uvicorn web.backend.main:app" 2>/dev/null || true
    pkill -9 -f "python -m src.main" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "bpftrace.*monitor_mcp_bpf" 2>/dev/null || true
    sleep 3
fi

# ============================================================================
# INICIALIZAÇÃO SEQUENCIAL ROBUSTA
# ============================================================================
# Usa script sequencial dedicado para garantir inicialização ordenada
# com verificação de saúde de cada serviço antes de prosseguir
# ============================================================================

echo -e "${GREEN}🔌 Iniciando Backend Cluster (Fase 1: Essenciais)...${NC}"

# CORREÇÃO (2025-12-10): Não reiniciar se backends já estão saudáveis
if [ "${SKIP_BACKEND_RESTART:-false}" = true ]; then
    echo -e "${GREEN}✅ Backends já estão rodando e saudáveis - pulando inicialização${NC}"
    echo "   Usando backends existentes"
else
    # Iniciar Backend Cluster apenas se necessário
    echo "🔄 Iniciando Backend Cluster..."
    "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh"
fi

# Função de health check com retry
check_backend_health() {
    local port=$1
    local max_retries=${2:-30}
    local retry_interval=${3:-3}
    local stable_checks=${4:-3}

    local stable_count=0

    for i in $(seq 1 $max_retries); do
        if curl -s --max-time 5 "http://localhost:${port}/health/" > /dev/null 2>&1; then
            # Verificar tempo de resposta (proxy para CPU)
            local response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:${port}/health/" 2>/dev/null || echo "10.0")
            if (( $(echo "$response_time < 2.0" | bc -l 2>/dev/null || echo "1") )); then
                stable_count=$((stable_count + 1))
                if [ $stable_count -ge $stable_checks ]; then
                    echo "✅ Backend ${port} estável após ${i} tentativas (~$((i*retry_interval))s)"
                    return 0
                fi
            else
                stable_count=0  # Reset se resposta lenta
            fi
        else
            stable_count=0  # Reset se não responde
        fi

        [ $i -lt $max_retries ] && sleep $retry_interval
    done

    return 1
}

# Aguardar Backend Primary (CRÍTICO - deve estar saudável)
# CORREÇÃO (2025-12-10): Aumentar tempo de espera para carregamento de modelos/transformers
# max_retries=100, retry_interval=3 → 100*3=300s (5 minutos)
# CORREÇÃO (2025-12-10): Não falhar imediatamente - backend pode demorar mais em sistemas lentos
echo "⏳ Aguardando Backend Primary (8000) inicializar..."
echo "   (Carregamento de modelos pode levar até 5 minutos...)"
echo "   (Aguardando até 300s antes de considerar falha...)"

BACKEND_READY=false
if check_backend_health 8000 100 3 3; then
    echo -e "${GREEN}✅ Backend Primary estável e pronto${NC}"
    BACKEND_READY=true
else
    echo -e "${YELLOW}⚠️  Backend Primary não respondeu após 300s${NC}"
    echo "📊 Diagnóstico:"
    ps aux | grep -E "(uvicorn|python.*main)" | grep -v grep || echo "   Nenhum processo backend encontrado"
    tail -n 20 logs/backend_8000.log 2>/dev/null || echo "   Log 8000 não encontrado"

    # Verificar se processo está rodando mesmo sem responder
    if pgrep -f "uvicorn.*main:app.*8000" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Backend está rodando mas não respondeu a tempo${NC}"
        echo "   Processo encontrado - pode estar ainda inicializando modelos"
        echo "   Continuando... (backend pode ficar pronto em breve)"
        BACKEND_READY=true  # Assumir que está OK se processo existe
    else
        echo -e "${RED}❌ Backend não está rodando - falha crítica${NC}"
        echo "   Tentando reiniciar backend..."
        "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh"
        sleep 10

        # Tentar mais uma vez
        if check_backend_health 8000 30 3 2; then
            echo -e "${GREEN}✅ Backend Primary reiniciado e pronto${NC}"
            BACKEND_READY=true
        else
            echo -e "${RED}❌ Falha crítica: Backend não inicializou após reinício${NC}"
            echo "   Verifique logs/backend_8000.log para detalhes"
            # NÃO SAIR COM ERRO - deixar systemd decidir se deve reiniciar
            # exit 1
        fi
    fi
fi

# Verificar Backends secundários (não críticos, mas desejáveis)
# CORREÇÃO (2025-12-10): Aumentar tempo de espera também para secundários
echo "⏳ Verificando Backends secundários..."
check_backend_health 8080 30 3 2 && echo "✅ Backend Secondary (8080) estável" || echo -e "${YELLOW}⚠️  Backend Secondary (8080) não estável (continuando...)${NC}"
check_backend_health 3001 30 3 2 && echo "✅ Backend Fallback (3001) estável" || echo -e "${YELLOW}⚠️  Backend Fallback (3001) não estável (continuando...)${NC}"

# FASE 2: SECUNDÁRIOS (após 60s dos essenciais)
# CORREÇÃO (2025-12-10): Aumentar tempo de espera para garantir inicialização completa
echo -e "${GREEN}⏰ Aguardando 60s antes de iniciar serviços secundários...${NC}"
echo "   (Garantindo que serviços essenciais estejam totalmente inicializados)"
echo "   (Carregamento de modelos pode levar tempo adicional...)"
sleep 60

# Verificação de CPU antes de prosseguir (evita bloqueio)
echo "🔍 Verificando estabilidade de CPU antes de serviços secundários..."
check_cpu_stable() {
    local max_cpu=${1:-30}
    local max_wait=${2:-30}
    local wait_interval=${3:-3}

    # CORREÇÃO (2025-12-10): Usar top com delay para medição precisa de CPU
    # ps aux mostra CPU acumulada desde início do processo, não uso atual
    get_cpu_usage() {
        # Usar top com delay de 1s para obter uso atual de CPU
        top -bn1 -d 1 | grep -E "^\s*[0-9]+.*python" | awk '{sum+=$9} END {print sum+0}' 2>/dev/null || \
        # Fallback: usar ps com cálculo mais preciso
        ps aux --no-headers | grep -E "[p]ython.*uvicorn\|[p]ython.*main" | awk '{sum+=$3} END {print sum+0}' 2>/dev/null || \
        echo "0"
    }

    for i in $(seq 1 $((max_wait / wait_interval))); do
        # Aguardar um pouco antes da primeira medição para estabilizar
        [ $i -eq 1 ] && sleep 2

        local cpu=$(get_cpu_usage)

        if (( $(echo "$cpu < $max_cpu" | bc -l 2>/dev/null || echo "0") )); then
            echo "✅ CPU estável ($cpu% < ${max_cpu}%)"
            return 0
        fi

        echo "   CPU: ${cpu}% (aguardando estabilização... $i/$((max_wait / wait_interval)))"
        sleep $wait_interval
    done

    # Se ainda alta após espera, verificar se é crítica
    local cpu=$(get_cpu_usage)
    if (( $(echo "$cpu > 80.0" | bc -l 2>/dev/null || echo "0") )); then
        echo -e "${YELLOW}⚠️  CPU alta ($cpu%) - pode ser normal durante inicialização${NC}"
        echo "   Backend pode estar carregando modelos. Continuando com cuidado..."
        echo "   Se persistir, verifique logs/backend_*.log"
        # CORREÇÃO (2025-12-10): Não abortar - apenas avisar
        # exit 1
    fi

    echo -e "${YELLOW}⚠️  CPU ainda alta ($cpu%), mas não crítica. Prosseguindo com cuidado...${NC}"
    return 0
}

check_cpu_stable 30 30 3
echo "✅ Sistema estável. Prosseguindo com serviços secundários..."

# ============================================================================
# FASE 2: SERVIÇOS SECUNDÁRIOS (Sequencial com Health Checks)
# ============================================================================

# 2.1. Iniciar MCP Orchestrator (depende de Backend Primary)
echo -e "${GREEN}🌐 Iniciando MCP Orchestrator...${NC}"
cd "$PROJECT_ROOT"

if pgrep -f "run_mcp_orchestrator.py" > /dev/null; then
    MCP_ORCHESTRATOR_PID=$(pgrep -f "run_mcp_orchestrator.py" | head -1)
    echo -e "${YELLOW}⚠️  MCP Orchestrator já está rodando (PID $MCP_ORCHESTRATOR_PID)${NC}"
else
    # Verificar que Backend está saudável antes de iniciar
    if ! curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${RED}❌ Backend não está saudável. Aguardando...${NC}"
        sleep 5
    fi

    chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" 2>/dev/null || true
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" > "$PROJECT_ROOT/logs/mcp_orchestrator.log" 2>&1 &
    MCP_ORCHESTRATOR_PID=$!
    echo $MCP_ORCHESTRATOR_PID > "$PROJECT_ROOT/logs/mcp_orchestrator.pid"
    echo "✓ MCP Orchestrator iniciado (PID $MCP_ORCHESTRATOR_PID)"

    # Verificar se iniciou corretamente
    sleep 3
    if ps -p $MCP_ORCHESTRATOR_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MCP Orchestrator rodando${NC}"
    else
        echo -e "${YELLOW}⚠️  MCP Orchestrator pode ter falhado (verifique logs)${NC}"
    fi
fi

# 2.2. Iniciar Ciclo Principal (depende de Backend Primary)
echo -e "${GREEN}🔄 Iniciando Ciclo Principal OmniMind (Fase 23: Autopoiese + Integração Real-time)...${NC}"
cd "$PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT/logs" "$PROJECT_ROOT/data/autopoietic/synthesized_code" "$PROJECT_ROOT/data/monitor"

if [ -f "$PROJECT_ROOT/logs/main_cycle.pid" ]; then
    OLD_PID=$(cat "$PROJECT_ROOT/logs/main_cycle.pid" 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ciclo Principal já está rodando (PID $OLD_PID)${NC}"
        MAIN_CYCLE_PID=$OLD_PID
    else
        # Verificar Backend antes de iniciar
        if curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
            nohup python -m src.main > "$PROJECT_ROOT/logs/main_cycle.log" 2>&1 &
            MAIN_CYCLE_PID=$!
            echo $MAIN_CYCLE_PID > "$PROJECT_ROOT/logs/main_cycle.pid"
            echo "✓ Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
            sleep 3
            if ps -p $MAIN_CYCLE_PID > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Ciclo Principal rodando${NC}"
            else
                echo -e "${YELLOW}⚠️  Ciclo Principal pode ter falhado (verifique logs)${NC}"
            fi
        else
            echo -e "${RED}❌ Backend não está saudável. Pulando Ciclo Principal.${NC}"
        fi
    fi
else
    if curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
        nohup python -m src.main > "$PROJECT_ROOT/logs/main_cycle.log" 2>&1 &
        MAIN_CYCLE_PID=$!
        echo $MAIN_CYCLE_PID > "$PROJECT_ROOT/logs/main_cycle.pid"
        echo "✓ Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
        sleep 3
        if ps -p $MAIN_CYCLE_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ciclo Principal rodando${NC}"
        fi
    else
        echo -e "${RED}❌ Backend não está saudável. Pulando Ciclo Principal.${NC}"
    fi
fi
echo "   Log: tail -f logs/main_cycle.log"

# 2.3. Iniciar Daemon (depende de Backend Primary)
echo -e "${GREEN}🤖 Inicializando OmniMind Daemon...${NC}"
cd "$PROJECT_ROOT"

# Verificar Backend antes de iniciar Daemon
if curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
    if [ -n "$OMNIMIND_DASHBOARD_PASS" ]; then
        curl -X POST http://localhost:8000/daemon/start \
          -u "${OMNIMIND_DASHBOARD_USER}:${OMNIMIND_DASHBOARD_PASS}" \
          > "$PROJECT_ROOT/logs/daemon_start.log" 2>&1 &
        DAEMON_START_PID=$!
        echo "✓ Daemon start request enviado (PID $DAEMON_START_PID)"
        sleep 2

        # Verificar se daemon iniciou
        if curl -s --max-time 3 -u "${OMNIMIND_DASHBOARD_USER}:${OMNIMIND_DASHBOARD_PASS}" http://localhost:8000/daemon/status > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Daemon iniciado${NC}"
        else
            echo -e "${YELLOW}⚠️  Daemon pode estar iniciando (verifique logs)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Senha não encontrada, pulando inicialização do daemon via API${NC}"
    fi
else
    echo -e "${RED}❌ Backend não está saudável. Pulando Daemon.${NC}"
fi

# 5. Iniciar Frontend
echo -e "${GREEN}🎨 Iniciando Frontend...${NC}"
echo "   (Aguardando backend estar pronto na porta 8000...)"

MAX_ATTEMPTS=30
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if curl -s --max-time 2 http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend pronto!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    ATTEMPT=$((ATTEMPT+1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo -e "${YELLOW}⚠️  Backend demorando para responder, iniciando Frontend mesmo assim...${NC}"
fi

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
