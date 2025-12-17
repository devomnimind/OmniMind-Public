#!/bin/bash
# Script de inicialização SECUNDÁRIA do OmniMind
# Fase 2: Serviços não-essenciais (Daemon + Frontend + Monitor + Ciclo Principal)
# Executado após 30s da inicialização dos serviços essenciais
# Autor: Fabrício da Silva + assistência de IA

set -e

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Serviços Secundários OmniMind (Fase 2)...${NC}"

#!/bin/bash
# Script de inicialização SECUNDÁRIA do OmniMind
# Fase 2: Serviços não-essenciais (Daemon + Frontend + Monitor + Ciclo Principal)
# Executado após estabilização dos serviços essenciais
# Autor: Fabrício da Silva + assistência de IA

set -e

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Serviços Secundários OmniMind (Fase 2)...${NC}"

# 🔧 CRÍTICO: Calcular PROJECT_ROOT de forma robusta
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"

# Validar que encontrou a raiz do projeto
if [ ! -f "$PROJECT_ROOT/config/omnimind.yaml" ] && [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}❌ Não conseguiu encontrar raiz do projeto OmniMind${NC}"
    exit 1
fi

# 🔧 CRÍTICO: Ativar venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✅ Venv ativado: $VIRTUAL_ENV"
else
    echo -e "${RED}❌ Venv não encontrado em $PROJECT_ROOT/.venv${NC}"
    exit 1
fi

# Verificação Inteligente de Serviços Essenciais
echo "🔍 Verificando serviços essenciais..."
SERVICES_READY=false
STABLE_COUNT=0
REQUIRED_CHECKS=3

for i in {1..10}; do
    HEALTHY_INSTANCES=0

    # Verificar se pelo menos uma instância backend está respondendo
    if curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
        RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:8000/health/ 2>/dev/null || echo "5.0")
        if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l 2>/dev/null || echo "1") )); then
            HEALTHY_INSTANCES=$((HEALTHY_INSTANCES + 1))
        fi
    fi

    if curl -s --max-time 3 http://localhost:8080/health/ > /dev/null 2>&1; then
        RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:8080/health/ 2>/dev/null || echo "5.0")
        if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l 2>/dev/null || echo "1") )); then
            HEALTHY_INSTANCES=$((HEALTHY_INSTANCES + 1))
        fi
    fi

    if curl -s --max-time 3 http://localhost:3001/health/ > /dev/null 2>&1; then
        RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:3001/health/ 2>/dev/null || echo "5.0")
        if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l 2>/dev/null || echo "1") )); then
            HEALTHY_INSTANCES=$((HEALTHY_INSTANCES + 1))
        fi
    fi

    if [ "$HEALTHY_INSTANCES" -ge 1 ]; then
        STABLE_COUNT=$((STABLE_COUNT + 1))
        echo "   Verificação $i/10: $HEALTHY_INSTANCES instâncias saudáveis (estável: $STABLE_COUNT/$REQUIRED_CHECKS)"

        if [ "$STABLE_COUNT" -ge "$REQUIRED_CHECKS" ]; then
            SERVICES_READY=true
            echo "✅ Serviços essenciais confirmados e estáveis"
            break
        fi
    else
        STABLE_COUNT=0
        echo "   Verificação $i/10: Aguardando serviços essenciais..."
    fi

    sleep 3
done

if [ "$SERVICES_READY" = false ]; then
    echo -e "${RED}❌ Serviços essenciais não estão disponíveis ou estáveis. Abortando.${NC}"
    exit 1
fi

# Verificação de CPU antes de prosseguir
echo "🔍 Verificando carga do sistema..."
CPU_USAGE=$(ps aux --no-headers -o pcpu -C python | awk '{sum+=$1} END {print sum}' 2>/dev/null || echo "0")
CPU_USAGE=${CPU_USAGE:-0}

if (( $(echo "$CPU_USAGE > 30.0" | bc -l 2>/dev/null || echo "0") )); then
    echo -e "${YELLOW}⚠️  CPU elevada ($CPU_USAGE%). Aguardando estabilização...${NC}"
    sleep 10

    CPU_USAGE=$(ps aux --no-headers -o pcpu -C python | awk '{sum+=$1} END {print sum}' 2>/dev/null || echo "0")
    if (( $(echo "$CPU_USAGE > 20.0" | bc -l 2>/dev/null || echo "0") )); then
        echo -e "${RED}❌ CPU ainda crítica ($CPU_USAGE%). Abortando serviços secundários.${NC}"
        exit 1
    fi
fi

echo "✅ Sistema pronto para serviços secundários"

# Ler credenciais de forma robusta
AUTH_FILE="$PROJECT_ROOT/config/dashboard_auth.json"
DASH_USER=""
DASH_PASS=""

if [ -f "$AUTH_FILE" ]; then
    DASH_USER=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('user', ''))" 2>/dev/null || echo "")
    DASH_PASS=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('pass', ''))" 2>/dev/null || echo "")
fi

# Fallback para .env
if [ -z "$DASH_USER" ] && [ -f "$PROJECT_ROOT/.env" ]; then
    DASH_USER=$(grep "^OMNIMIND_DASHBOARD_USER=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "admin")
    DASH_PASS=$(grep "^OMNIMIND_DASHBOARD_PASS=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "")
fi

# Último fallback
if [ -z "$DASH_USER" ]; then
    DASH_USER="admin"
fi

export OMNIMIND_DASHBOARD_USER="$DASH_USER"
export OMNIMIND_DASHBOARD_PASS="$DASH_PASS"

# 1. Iniciar Ciclo Principal com Autopoiese
echo -e "${GREEN}🔄 Iniciando Ciclo Principal OmniMind...${NC}"
cd "$PROJECT_ROOT"
mkdir -p logs data/autopoietic/synthesized_code data/monitor

# Verificar se já está rodando (verificação mais robusta)
MAIN_CYCLE_RUNNING=false
if [ -f "logs/main_cycle.pid" ]; then
    OLD_PID=$(cat logs/main_cycle.pid 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ciclo Principal já está rodando (PID $OLD_PID)${NC}"
        MAIN_CYCLE_RUNNING=true
    else
        echo "🧹 Removendo PID file obsoleto (processo $OLD_PID não existe)"
        rm -f logs/main_cycle.pid
    fi
fi

# Verificar também por processos python -m src.main
if ! $MAIN_CYCLE_RUNNING; then
    MAIN_PID=$(pgrep -f "python -m src.main" | head -1 || echo "")
    if [ -n "$MAIN_PID" ]; then
        echo -e "${YELLOW}⚠️  Ciclo Principal já está rodando (PID $MAIN_PID)${NC}"
        echo $MAIN_PID > logs/main_cycle.pid
        MAIN_CYCLE_RUNNING=true
    fi
fi

if ! $MAIN_CYCLE_RUNNING; then
    echo "🚀 Iniciando Ciclo Principal..."
    nohup python -m src.main > logs/main_cycle.log 2>&1 &
    MAIN_CYCLE_PID=$!
    echo $MAIN_CYCLE_PID > logs/main_cycle.pid
    echo "✓ Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
    echo "   Log: logs/main_cycle.log"

    # Aguardar inicialização
    sleep 5

    # Verificar se iniciou corretamente
    if ! ps -p $MAIN_CYCLE_PID > /dev/null 2>&1; then
        echo -e "${RED}❌ Ciclo Principal falhou ao iniciar. Verifique logs/main_cycle.log${NC}"
        tail -n 10 logs/main_cycle.log 2>/dev/null || echo "   Log não disponível"
        exit 1
    fi
else
    MAIN_CYCLE_PID=$(cat logs/main_cycle.pid 2>/dev/null || echo "desconhecido")
    echo "✅ Ciclo Principal já ativo (PID $MAIN_CYCLE_PID)"
fi

# 2. Iniciar Daemon
echo -e "${GREEN}🤖 Iniciando OmniMind Daemon...${NC}"

if [ -n "$DASH_PASS" ]; then
    echo "📡 Enviando requisição de inicialização do daemon..."
    DAEMON_RESPONSE=$(curl -s -X POST http://localhost:8000/daemon/start \
        -u "${DASH_USER}:${DASH_PASS}" \
        -w "HTTPSTATUS:%{http_code}" 2>/dev/null || echo "HTTPSTATUS:000")

    HTTP_CODE=$(echo $DAEMON_RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
        echo "✅ Daemon iniciado via API"
    else
        echo -e "${YELLOW}⚠️  Falha ao iniciar daemon via API (HTTP $HTTP_CODE)${NC}"
        echo "   Verifique se o backend está totalmente inicializado"
    fi
else
    echo -e "${YELLOW}⚠️  Credenciais não encontradas, pulando inicialização do daemon${NC}"
fi

sleep 2

# 3. Iniciar Frontend
echo -e "${GREEN}🎨 Iniciando Frontend...${NC}"

# Verificar se diretório frontend existe
if [ ! -d "web/frontend" ]; then
    echo -e "${RED}❌ Diretório web/frontend não encontrado!${NC}"
    echo "   Verificando estrutura do projeto..."
    ls -la web/ 2>/dev/null | head -5
    FRONTEND_AVAILABLE=false
else
    cd web/frontend
    FRONTEND_AVAILABLE=true

    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependências do Frontend..."
        if npm install; then
            echo "✅ Dependências instaladas"
        else
            echo -e "${YELLOW}⚠️  Falha ao instalar dependências do frontend${NC}"
            FRONTEND_AVAILABLE=false
        fi
    fi

    if $FRONTEND_AVAILABLE; then
        # Verificar se já está rodando (verificação robusta)
        FRONTEND_RUNNING=false

        # Verificar PID file
        if [ -f "../../logs/frontend.pid" ]; then
            OLD_PID=$(cat ../../logs/frontend.pid 2>/dev/null || echo "")
            if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  Frontend já está rodando (PID $OLD_PID)${NC}"
                FRONTEND_RUNNING=true
            else
                echo "🧹 Removendo PID file obsoleto do frontend"
                rm -f ../../logs/frontend.pid
            fi
        fi

        # Verificar processos npm/vite
        if ! $FRONTEND_RUNNING; then
            FRONTEND_PID=$(pgrep -f "npm run dev" | head -1 || echo "")
            if [ -n "$FRONTEND_PID" ]; then
                echo -e "${YELLOW}⚠️  Frontend já está rodando (PID $FRONTEND_PID)${NC}"
                echo $FRONTEND_PID > ../../logs/frontend.pid
                FRONTEND_RUNNING=true
            fi
        fi

        if ! $FRONTEND_RUNNING; then
            echo "🚀 Iniciando servidor de desenvolvimento..."
            nohup npm run dev > ../../logs/frontend.log 2>&1 &
            FRONTEND_PID=$!
            echo $FRONTEND_PID > ../../logs/frontend.pid
            echo "✓ Frontend iniciado (PID $FRONTEND_PID)"
            echo "   Log: logs/frontend.log"
            echo "   URL: http://localhost:3000"

            # Aguardar inicialização
            sleep 5

            # Verificar se iniciou corretamente
            if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
                echo -e "${RED}❌ Frontend falhou ao iniciar. Verifique logs/frontend.log${NC}"
                tail -n 10 ../../logs/frontend.log 2>/dev/null || echo "   Log não disponível"
            fi
        else
            FRONTEND_PID=$(cat ../../logs/frontend.pid 2>/dev/null || echo "desconhecido")
            echo "✅ Frontend já ativo (PID $FRONTEND_PID)"
        fi
    fi

    # Voltar para raiz
    cd "$PROJECT_ROOT"
fi

# 4. Iniciar eBPF Monitor (se disponível)
echo -e "${GREEN}📊 Verificando eBPF Monitor...${NC}"

if command -v bpftrace &> /dev/null; then
    EBPF_LOG="$PROJECT_ROOT/logs/ebpf_monitor.log"
    mkdir -p "$PROJECT_ROOT/logs"

    # Verificar se já está rodando
    EBPF_RUNNING=$(pgrep -f "bpftrace.*monitor_mcp_bpf" | wc -l)
    if [ "$EBPF_RUNNING" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  eBPF Monitor já está rodando${NC}"
    else
        # Garantir permissões no arquivo de log
        if [ -f "$EBPF_LOG" ]; then
            touch "$EBPF_LOG" 2>/dev/null || true
        fi

        # Parar qualquer instância anterior
        pkill -f "bpftrace.*monitor_mcp_bpf" || true
        sleep 1

        # Iniciar em background
        cd "$PROJECT_ROOT"
        if [ -f "scripts/canonical/system/secure_run.py" ]; then
            python3 scripts/canonical/system/secure_run.py bpftrace scripts/canonical/system/monitor_mcp_bpf.bt > "${EBPF_LOG}" 2>&1 &
            EBPF_PID=$!
        else
            sudo bpftrace scripts/canonical/system/monitor_mcp_bpf.bt > "${EBPF_LOG}" 2>&1 &
            EBPF_PID=$!
        fi

        sleep 2

        # Verificar se iniciou
        if ps -p $EBPF_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ eBPF Monitor ativo (PID $EBPF_PID)${NC}"
            echo "   Log: logs/ebpf_monitor.log"
        else
            echo -e "${YELLOW}⚠️  eBPF Monitor falhou ao iniciar${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  bpftrace não encontrado - eBPF Monitor não disponível${NC}"
fi

# Status Final
echo -e "${GREEN}✅ Serviços Secundários Iniciados!${NC}"
echo ""
echo -e "${GREEN}📋 STATUS DOS SERVIÇOS:${NC}"

# Verificar status do Ciclo Principal
if [ -f "logs/main_cycle.pid" ] && ps -p $(cat logs/main_cycle.pid 2>/dev/null) > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ciclo Principal: Ativo (PID $(cat logs/main_cycle.pid))${NC}"
    echo "   Log: logs/main_cycle.log"
else
    echo -e "${RED}❌ Ciclo Principal: Inativo${NC}"
fi

# Verificar status do Frontend
if [ -f "logs/frontend.pid" ] && ps -p $(cat logs/frontend.pid 2>/dev/null) > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend: Ativo (PID $(cat logs/frontend.pid))${NC}"
    echo "   URL: http://localhost:3000"
    echo "   Log: logs/frontend.log"
else
    echo -e "${YELLOW}⚠️  Frontend: Inativo ou ainda inicializando${NC}"
fi

# Verificar status do eBPF Monitor
if pgrep -f "bpftrace.*monitor_mcp_bpf" > /dev/null; then
    EBPF_PID=$(pgrep -f "bpftrace.*monitor_mcp_bpf")
    echo -e "${GREEN}✅ eBPF Monitor: Ativo (PID $EBPF_PID)${NC}"
    echo "   Log: logs/ebpf_monitor.log"
else
    echo -e "${YELLOW}⚠️  eBPF Monitor: Não disponível${NC}"
fi

echo ""
echo -e "${GREEN}🎯 Sistema OmniMind Pronto!${NC}"
echo "   Backend: http://localhost:8000"
echo "   Dashboard: http://localhost:3000"
echo "   Logs: logs/"
echo ""
echo -e "${GREEN}💡 Comandos Úteis:${NC}"
echo "   Monitor: tail -f logs/backend_8000.log"
echo "   Status: curl http://localhost:8000/health/"
echo "   Parar: pkill -f omnimind"

