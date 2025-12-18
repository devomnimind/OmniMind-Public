#!/bin/bash

# ============================================================================
# 🚀 OMNIMIND SYSTEM START - VERSÃO ROBUSTA v2.0
# ============================================================================
# Refactorizado para:
# 1. Eliminar race conditions na lógica de health check
# 2. Estados consistentes entre verificações
# 3. CPU metric corrigida (ps ao invés de top)
# 4. Timeout unificado para curl
# 5. Logging detalhado de cada verificação
# 6. Suporte a auto-recovery via OmniMind
# ============================================================================
# MUDANÇAS (vs v1.0):
# - Lógica OR para ANY unhealthy → restart (ao invés de AND para ALL)
# - Função unified_health_check() com estado persistente
# - CPU calculated via ps (mais preciso)
# - Logging detalhado em logs/startup_detailed.log
# - Suporte a OMNIMIND_AUTO_RECOVERY flag
# ============================================================================

set -o pipefail  # Falhar se qualquer pipe falhar
# NÃO usar 'set -e' pois queremos recuperar de erros específicos

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# UTILIDADES DE LOGGING
# ============================================================================

# Timestamp ISO para logs
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null || date -u +"%Y-%m-%d %H:%M:%S"
}

# Inicializar arquivo de log
init_log() {
    local log_file="$1"
    local log_dir="$(dirname "$log_file")"
    mkdir -p "$log_dir" 2>/dev/null || true

    # Rotacionar logs antigos se necessário
    if [ -f "$log_file" ] && [ $(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null) -gt 5242880 ]; then
        mv "$log_file" "${log_file}.$(get_timestamp | tr -d ':' | cut -d. -f1)"
    fi

    echo "[$(get_timestamp)] Inicializando novo startup log" >> "$log_file" 2>/dev/null || true
}

# Log com timestamp
log_info() {
    local msg="$1"
    local log_file="${STARTUP_LOG:-/dev/null}"
    echo -e "${BLUE}[INFO]${NC} $msg"
    echo "[$(get_timestamp)] [INFO] $msg" >> "$log_file" 2>/dev/null || true
}

log_success() {
    local msg="$1"
    local log_file="${STARTUP_LOG:-/dev/null}"
    echo -e "${GREEN}[✓]${NC} $msg"
    echo "[$(get_timestamp)] [SUCCESS] $msg" >> "$log_file" 2>/dev/null || true
}

log_warning() {
    local msg="$1"
    local log_file="${STARTUP_LOG:-/dev/null}"
    echo -e "${YELLOW}[⚠]${NC} $msg"
    echo "[$(get_timestamp)] [WARNING] $msg" >> "$log_file" 2>/dev/null || true
}

log_error() {
    local msg="$1"
    local log_file="${STARTUP_LOG:-/dev/null}"
    echo -e "${RED}[✗]${NC} $msg"
    echo "[$(get_timestamp)] [ERROR] $msg" >> "$log_file" 2>/dev/null || true
}

log_debug() {
    if [ "${DEBUG_MODE:-false}" = true ]; then
        local msg="$1"
        local log_file="${STARTUP_LOG:-/dev/null}"
        echo -e "${BLUE}[DEBUG]${NC} $msg"
        echo "[$(get_timestamp)] [DEBUG] $msg" >> "$log_file" 2>/dev/null || true
    fi
}

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

echo -e "${GREEN}🚀 Iniciando Sistema OmniMind Completo (Versão Robusta v2.0)...${NC}"

# Calcular PROJECT_ROOT
if [ -n "${OMNIMIND_PROJECT_ROOT:-}" ]; then
    PROJECT_ROOT="$OMNIMIND_PROJECT_ROOT"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    while [ "$SCRIPT_DIR" != "/" ]; do
        if [ -f "$SCRIPT_DIR/.env" ] || [ -f "$SCRIPT_DIR/pyproject.toml" ] || [ -f "$SCRIPT_DIR/config/omnimind.yaml" ]; then
            PROJECT_ROOT="$SCRIPT_DIR"
            break
        fi
        SCRIPT_DIR="$(dirname "$SCRIPT_DIR")"
    done

    if [ -z "$PROJECT_ROOT" ]; then
        PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
    fi
fi

# Validar PROJECT_ROOT
if [ ! -f "$PROJECT_ROOT/config/omnimind.yaml" ] && [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}❌ Não conseguiu encontrar raiz do projeto OmniMind${NC}"
    exit 1
fi

log_info "Raiz do projeto encontrada: $PROJECT_ROOT"

# Configurar arquivo de log
STARTUP_LOG="$PROJECT_ROOT/logs/startup_detailed.log"
DEBUG_MODE="${OMNIMIND_DEBUG:-false}"
init_log "$STARTUP_LOG"

log_info "Debug mode: $DEBUG_MODE"
log_info "Startup log: $STARTUP_LOG"

# Ativar venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true
    log_success "Venv ativado: $VIRTUAL_ENV"
else
    log_warning "Venv não encontrado em $PROJECT_ROOT/.venv"
fi

# ============================================================================
# CONFIGURAÇÕES CRÍTICAS
# ============================================================================

# GPU Configuration
export CUDA_HOME="/usr"
export CUDA_path="/usr"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
export CUDA_VISIBLE_DEVICES="0"
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"

# Variáveis de controle de inicialização
PHASE_TIMEOUT_ESSENTIAL=300       # 5 minutos para essenciais
PHASE_TIMEOUT_SECONDARY=180       # 3 minutos para secundários
PHASE_TIMEOUT_MONITORING=60       # 1 minuto para monitoring
HEALTH_CHECK_TIMEOUT=5            # curl timeout padrão (importante: timeout não é suficiente para 3001)
HEALTH_CHECK_TIMEOUT_FALLBACK=10  # curl timeout aumentado para Fallback (3001)
HEALTH_CHECK_RETRIES_ESSENTIAL=100  # Retries para Primary (8000)
HEALTH_CHECK_RETRIES_SECONDARY=30   # Retries para secundários (8080)
HEALTH_CHECK_RETRIES_FALLBACK=50    # Retries para Fallback (3001) - precisa mais tempo para inicializar
HEALTH_CHECK_STABLE_CHECKS=3      # Quantas checks consecutivas para confirmar "estável"

log_info "Timeouts configurados:"
log_info "  Essential: ${PHASE_TIMEOUT_ESSENTIAL}s"
log_info "  Secondary: ${PHASE_TIMEOUT_SECONDARY}s"
log_info "  Monitoring: ${PHASE_TIMEOUT_MONITORING}s"

# ============================================================================
# UTILIDADES DE HEALTH CHECK
# ============================================================================

# Verificar se porta está aberta (alternativa se curl falhar)
check_port_open() {
    local port=$1

    # Tentar netstat primeiro (mais rápido que curl)
    if command -v ss &> /dev/null; then
        ss -tlnp 2>/dev/null | grep -q ":${port}\s" && return 0
    elif command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep -q ":${port}\s" && return 0
    fi

    # Fallback: tentar conectar
    timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null && return 0

    return 1
}

# Verificar resposta HTTP (curl com retry logic melhorado)
check_http_health() {
    local port=$1
    local url="http://localhost:${port}/health/"

    # Tentar up to 3 vezes em caso de timeout transitório
    for attempt in 1 2 3; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $HEALTH_CHECK_TIMEOUT "$url" 2>/dev/null)

        if [ "$http_code" = "200" ] || [ "$http_code" = "000" ]; then
            # 000 = connection successful but no response (pode ser normal em boot)
            [ "$http_code" = "200" ] && return 0  # OK completo
        fi

        [ $attempt -lt 3 ] && sleep 1
    done

    return 1
}

# Verificar resposta HTTP com timeout customizado
check_http_health_with_timeout() {
    local port=$1
    local custom_timeout=${2:-$HEALTH_CHECK_TIMEOUT}
    local url="http://localhost:${port}/health/"

    # Tentar up to 3 vezes em caso de timeout transitório
    for attempt in 1 2 3; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $custom_timeout "$url" 2>/dev/null)

        if [ "$http_code" = "200" ] || [ "$http_code" = "000" ]; then
            # 000 = connection successful but no response (pode ser normal em boot)
            [ "$http_code" = "200" ] && return 0  # OK completo
        fi

        [ $attempt -lt 3 ] && sleep 1
    done

    return 1
}

# Verificar resposta de tempo (em milisegundos)
check_response_time() {
    local port=$1
    local url="http://localhost:${port}/health/"

    local response_time=$(curl -s -w "%{time_total}" -o /dev/null --max-time $HEALTH_CHECK_TIMEOUT "$url" 2>/dev/null || echo "10.0")
    echo "$response_time"
}

# Verificar resposta de tempo com timeout customizado
check_response_time_with_timeout() {
    local port=$1
    local custom_timeout=${2:-$HEALTH_CHECK_TIMEOUT}
    local url="http://localhost:${port}/health/"

    local response_time=$(curl -s -w "%{time_total}" -o /dev/null --max-time $custom_timeout "$url" 2>/dev/null || echo "${custom_timeout}")
    echo "$response_time"
}

# UNIFIED HEALTH CHECK COM ESTADO PERSISTENTE
# Estados persistem em variáveis globais entre chamadas
declare -A BACKEND_HEALTH_CACHE
declare -A BACKEND_STABLE_COUNT

unified_health_check() {
    local port=$1
    local mode=${2:-essential}  # essential, secondary ou fallback
    local max_retries=${HEALTH_CHECK_RETRIES_ESSENTIAL}
    local custom_timeout=${HEALTH_CHECK_TIMEOUT}
    local retry_interval=3
    local stable_threshold=${HEALTH_CHECK_STABLE_CHECKS}

    # Definir parâmetros baseado no modo
    case "$mode" in
        essential)
            max_retries=${HEALTH_CHECK_RETRIES_ESSENTIAL}
            custom_timeout=${HEALTH_CHECK_TIMEOUT}
            ;;
        secondary)
            max_retries=${HEALTH_CHECK_RETRIES_SECONDARY}
            custom_timeout=${HEALTH_CHECK_TIMEOUT}
            ;;
        fallback)
            max_retries=${HEALTH_CHECK_RETRIES_FALLBACK}
            custom_timeout=${HEALTH_CHECK_TIMEOUT_FALLBACK}
            ;;
    esac

    # Inicializar contadores se não existem
    [ -z "${BACKEND_STABLE_COUNT[$port]}" ] && BACKEND_STABLE_COUNT[$port]=0

    log_debug "Health check iniciado para porta $port (mode: $mode, max_retries: $max_retries, timeout: ${custom_timeout}s)"

    for i in $(seq 1 $max_retries); do
        # Verificar porta aberta como pre-check
        if ! check_port_open $port; then
            BACKEND_STABLE_COUNT[$port]=0  # Reset counter
            log_debug "  [$i/$max_retries] Porta $port fechada"
            [ $i -lt $max_retries ] && sleep $retry_interval
            continue
        fi

        # Verificar resposta HTTP com timeout customizado
        if check_http_health_with_timeout $port $custom_timeout; then
            local response_time=$(check_response_time_with_timeout $port $custom_timeout)

            # Validar tempo de resposta
            if (( $(echo "$response_time < $custom_timeout" | bc -l 2>/dev/null || echo "1") )); then
                BACKEND_STABLE_COUNT[$port]=$((${BACKEND_STABLE_COUNT[$port]:-0} + 1))
                log_debug "  [$i/$max_retries] Porta $port OK (${response_time}s, stable: ${BACKEND_STABLE_COUNT[$port]}/$stable_threshold)"

                # Verificar se já está estável
                if [ ${BACKEND_STABLE_COUNT[$port]} -ge $stable_threshold ]; then
                    log_success "Backend em porta $port estável e pronto (resposta: ${response_time}s)"
                    BACKEND_HEALTH_CACHE[$port]="healthy"
                    return 0
                fi
            else
                BACKEND_STABLE_COUNT[$port]=0  # Reset se resposta lenta
                log_debug "  [$i/$max_retries] Porta $port responde mas lento (${response_time}s)"
            fi
        else
            BACKEND_STABLE_COUNT[$port]=0  # Reset counter
            log_debug "  [$i/$max_retries] Porta $port não respondeu"
        fi

        [ $i -lt $max_retries ] && sleep $retry_interval
    done

    # Se chegou aqui, não ficou estável
    log_warning "Backend em porta $port não ficou estável após $max_retries tentativas"
    BACKEND_HEALTH_CACHE[$port]="unhealthy"
    return 1
}

# ============================================================================
# UTILIDADES DE VERIFICAÇÃO DE CPU
# ============================================================================

# CORRIGIDO: Usar ps ao invés de top para medir CPU real
get_cpu_usage_corrected() {
    # Somar CPU de processos Python relevantes
    # ps -o %cpu: Retorna % CPU por processo
    # Somar e normalizar para 0-100 (não valor absoluto em multi-core)

    local total_cpu=$(ps aux --no-headers 2>/dev/null | \
        grep -E "[u]vivicorn|[p]ython.*main|[p]ython.*src\.main" | \
        awk '{sum += $3} END {print sum+0}' || echo "0")

    # Normalizar: ps retorna% por core
    # Em sistema com N cores, máximo seria N*100
    # Retornar como % do sistema total
    local num_cores=$(nproc 2>/dev/null || echo "1")
    local normalized_cpu=$(echo "scale=1; $total_cpu / $num_cores" | bc -l 2>/dev/null || echo "$total_cpu")

    echo "$normalized_cpu"
}

check_cpu_stable() {
    local max_cpu=${1:-30}
    local max_wait=${2:-30}
    local wait_interval=${3:-3}

    log_info "Verificando estabilidade de CPU (máx: ${max_cpu}%, espera: ${max_wait}s)..."

    local start_time=$(date +%s)
    local stable_checks=0
    local stable_threshold=3

    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [ $elapsed -gt $max_wait ]; then
            log_warning "CPU ainda não estabilizou após ${max_wait}s (timeout)"
            return 0  # Prosseguir mesmo assim
        fi

        local cpu=$(get_cpu_usage_corrected)

        if (( $(echo "$cpu < $max_cpu" | bc -l 2>/dev/null || echo "0") )); then
            stable_checks=$((stable_checks + 1))
            log_info "  CPU: ${cpu}% (OK) [$stable_checks/$stable_threshold]"

            if [ $stable_checks -ge $stable_threshold ]; then
                log_success "CPU estabilizada em ${cpu}%"
                return 0
            fi
        else
            stable_checks=0
            log_warning "  CPU: ${cpu}% (alta, resetando contador)"
        fi

        sleep $wait_interval
    done
}

# ============================================================================
# SEGURANÇA (Port 4444 block)
# ============================================================================

log_info "Aplicando bloqueio de segurança (porta 4444)..."
if command -v iptables &> /dev/null; then
    if ! sudo iptables -C INPUT -p tcp --dport 4444 -j DROP 2>/dev/null; then
        sudo iptables -A INPUT -p tcp --dport 4444 -j DROP 2>/dev/null || true
        sudo iptables -A OUTPUT -p tcp --dport 4444 -j DROP 2>/dev/null || true
        log_success "Porta 4444 bloqueada"
    else
        log_info "Porta 4444 já está bloqueada"
    fi
fi

# ============================================================================
# AUTENTICAÇÃO (Credenciais Unificadas)
# ============================================================================

log_info "Configurando credenciais unificadas do cluster..."
DASH_USER=""
DASH_PASS=""
AUTH_FILE="$PROJECT_ROOT/config/dashboard_auth.json"

if [ -f "$AUTH_FILE" ]; then
    DASH_USER=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('user', ''))" 2>/dev/null)
    DASH_PASS=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('pass', ''))" 2>/dev/null)
fi

if [ -z "$DASH_USER" ] && [ -f "$PROJECT_ROOT/.env" ]; then
    DASH_USER=$(grep "^OMNIMIND_DASHBOARD_USER=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    DASH_PASS=$(grep "^OMNIMIND_DASHBOARD_PASS=" "$PROJECT_ROOT/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'")
fi

if [ -z "$DASH_USER" ]; then
    DASH_USER="admin"
    DASH_PASS=$(openssl rand -base64 12)
    echo "{\"user\": \"$DASH_USER\", \"pass\": \"$DASH_PASS\"}" > "$AUTH_FILE"
    log_info "Novas credenciais geradas em $AUTH_FILE"
fi

export OMNIMIND_DASHBOARD_USER="$DASH_USER"
export OMNIMIND_DASHBOARD_PASS="$DASH_PASS"
export OMNIMIND_DASHBOARD_AUTH_FILE="$AUTH_FILE"

log_success "Credenciais cluster: $DASH_USER / ****"

# ============================================================================
# FASE 1: VERIFICAÇÃO DE SERVIÇOS EXISTENTES E DECISÃO
# ============================================================================

echo ""
log_info "════ FASE 1: Verificação de Serviços Existentes ════"

NEED_RESTART=false

# Verificar cada backend
for port in 8000 8080 3001; do
    if check_port_open $port; then
        if check_http_health $port; then
            log_success "Porta $port já está respondendo"
        else
            log_warning "Porta $port está aberta mas não responde a /health/"
            NEED_RESTART=true
        fi
    else
        log_warning "Porta $port está fechada"
        NEED_RESTART=true
    fi
done

log_info "Decisão: NEED_RESTART=$NEED_RESTART"

if [ "$NEED_RESTART" = true ]; then
    log_info "Matando backends existentes para reinicialização..."
    pkill -9 -f "python web/backend/main.py" 2>/dev/null || true
    pkill -9 -f "uvicorn web.backend.main:app" 2>/dev/null || true
    pkill -9 -f "python -m src.main" 2>/dev/null || true
    sleep 2
fi

# ============================================================================
# FASE 1.5: INICIAR BACKEND CLUSTER
# ============================================================================

echo ""
log_info "════ FASE 1.5: Inicialização Backend Cluster ════"

chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh" 2>/dev/null || true

log_info "Iniciando Backend Cluster via run_cluster.sh..."
if ! "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh"; then
    log_error "Falha ao iniciar Backend Cluster"
    if [ "${OMNIMIND_AUTO_RECOVERY:-false}" = true ]; then
        log_warning "Auto-recovery habilitado, tentando novamente..."
        sleep 5
        "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh" || log_error "Falha na tentativa 2"
    fi
fi

# ============================================================================
# FASE 2: HEALTH CHECK ESSENCIAIS COM RETRY
# ============================================================================

echo ""
log_info "════ FASE 2: Health Check Essenciais (Timeout: ${PHASE_TIMEOUT_ESSENTIAL}s) ════"

# Backend Primary (CRÍTICO)
log_info "Aguardando Backend Primary (8000) inicializar (até ${PHASE_TIMEOUT_ESSENTIAL}s)..."
if unified_health_check 8000 essential; then
    log_success "Backend Primary (8000) está saudável e pronto"
else
    log_error "Backend Primary (8000) não ficou saudável"

    if [ "${OMNIMIND_AUTO_RECOVERY:-false}" = true ]; then
        log_warning "Auto-recovery: tentando reiniciar backend 8000..."
        pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
        sleep 3
        # Tentar reiniciar via run_cluster ou manual
        if ! unified_health_check 8000 essential; then
            log_error "CRÍTICO: Backend Primary não recuperou após retry"
            log_error "Sistema não pode inicializar sem Backend Primary"
            # Não abortar - deixar systemd decidir
        fi
    else
        log_warning "Continuando mesmo com Backend Primary não respondendo..."
    fi
fi

# Verificar secundários e fallback (não-crítico)
log_info "Aguardando Backends Secundários (8080, 3001)..."
unified_health_check 8080 secondary || log_warning "Backend Secondary (8080) não está pronto (prosseguindo...)"
unified_health_check 3001 fallback || log_warning "Backend Fallback (3001) não está pronto (prosseguindo...)"

# ============================================================================
# PHASE 2.5: STABILIZAÇÃO DE CPU
# ============================================================================

echo ""
log_info "════ FASE 2.5: Estabilização de CPU ════"
log_info "Aguardando 60s para carregamento completo de modelos..."
sleep 60

check_cpu_stable 50 30 3

log_info "Prosseguindo com serviços secundários..."

# ============================================================================
# FASE 3: SERVIÇOS SECUNDÁRIOS
# ============================================================================

echo ""
log_info "════ FASE 3: Inicialização Serviços Secundários ════"

cd "$PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT/logs" "$PROJECT_ROOT/data/autopoietic/synthesized_code" "$PROJECT_ROOT/data/monitor"

# MCP Orchestrator
log_info "Iniciando MCP Orchestrator..."
if pgrep -f "run_mcp_orchestrator.py" > /dev/null; then
    log_info "MCP Orchestrator já está rodando"
else
    if [ "${BACKEND_HEALTH_CACHE[8000]}" = "healthy" ] || check_http_health 8000; then
        chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" 2>/dev/null || true
        nohup python "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" > "$PROJECT_ROOT/logs/mcp_orchestrator.log" 2>&1 &
        MCP_ORCHESTRATOR_PID=$!
        echo $MCP_ORCHESTRATOR_PID > "$PROJECT_ROOT/logs/mcp_orchestrator.pid"
        log_success "MCP Orchestrator iniciado (PID $MCP_ORCHESTRATOR_PID)"
    else
        log_warning "Backend não está saudável, pulando MCP Orchestrator"
    fi
fi

# Ciclo Principal
log_info "Iniciando Ciclo Principal OmniMind..."
if [ "${BACKEND_HEALTH_CACHE[8000]}" = "healthy" ] || check_http_health 8000; then
    nohup python -m src.main > "$PROJECT_ROOT/logs/main_cycle.log" 2>&1 &
    MAIN_CYCLE_PID=$!
    echo $MAIN_CYCLE_PID > "$PROJECT_ROOT/logs/main_cycle.pid"
    log_success "Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
else
    log_warning "Backend não está saudável, pulando Ciclo Principal"
fi

# Frontend
log_info "Iniciando Frontend..."
if [ -d "web/frontend" ]; then
    cd web/frontend
    if [ ! -d "node_modules" ]; then
        log_info "Instalando dependências do Frontend..."
        npm install --legacy-peer-deps 2>/dev/null || true
    fi

    if ! pgrep -f "npm.*dev" > /dev/null; then
        nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "$PROJECT_ROOT/logs/frontend.pid"
        log_success "Frontend iniciado (PID $FRONTEND_PID)"
    else
        log_info "Frontend já está rodando"
    fi
    cd "$PROJECT_ROOT"
fi

# ============================================================================
# FASE 4: MONITORAMENTO E OBSERVABILIDADE
# ============================================================================

echo ""
log_info "════ FASE 4: Monitoramento e Observabilidade (Aguardando ${PHASE_TIMEOUT_MONITORING}s) ════"
log_info "Aguardando estabilização de serviços secundários..."
sleep $PHASE_TIMEOUT_MONITORING

# Observer Service
log_info "Iniciando Observer Service..."
if ! pgrep -f "run_observer_service.py" > /dev/null; then
    mkdir -p "$PROJECT_ROOT/data/long_term_logs"
    chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" 2>/dev/null || true
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" > "$PROJECT_ROOT/logs/observer_service.log" 2>&1 &
    OBSERVER_PID=$!
    echo $OBSERVER_PID > "$PROJECT_ROOT/logs/observer_service.pid"
    log_success "Observer Service iniciado (PID $OBSERVER_PID)"
fi

# eBPF Monitor
log_info "Iniciando eBPF Monitor..."
if command -v bpftrace &> /dev/null; then
    python3 "$PROJECT_ROOT/scripts/canonical/system/secure_run.py" pkill -f "bpftrace.*monitor_mcp_bpf" 2>/dev/null || true
    sleep 1
    python3 "$PROJECT_ROOT/scripts/canonical/system/secure_run.py" bpftrace "$PROJECT_ROOT/scripts/canonical/system/monitor_mcp_bpf.bt" > "$PROJECT_ROOT/logs/ebpf_monitor.log" 2>&1 &
    sleep 2
    log_success "eBPF Monitor iniciado"
else
    log_warning "bpftrace não encontrado - eBPF Monitor desabilitado"
fi

# ============================================================================
# RESUMO FINAL
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Sistema OmniMind Inicializado (Versão Robusta v2.0)${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

log_success "Sistema OmniMind inicializado com sucesso"

echo ""
echo -e "${GREEN}📋 SERVIÇOS ATIVOS:${NC}"
echo "   Backend Cluster: Ports 8000, 8080, 3001"
if [ -n "${BACKEND_HEALTH_CACHE[8000]}" ]; then
    echo "   Backend Primary (8000): ${BACKEND_HEALTH_CACHE[8000]}"
fi
echo "   Frontend: http://localhost:3000"
echo ""
echo -e "${GREEN}🔐 CREDENCIAIS CLUSTER:${NC}"
echo "   User: $OMNIMIND_DASHBOARD_USER"
echo "   Pass: $OMNIMIND_DASHBOARD_PASS"
echo ""
echo -e "${GREEN}📊 LOGS:${NC}"
echo "   Startup detailed: $STARTUP_LOG"
echo "   Backend: logs/backend_*.log"
echo "   Observer: logs/observer_service.log"
echo "   Metrics: data/long_term_logs/omnimind_metrics.jsonl"
echo ""

echo -e "${BLUE}💡 DICAS:${NC}"
echo "   Ver logs detalhados: tail -f $STARTUP_LOG"
echo "   Monitorar CPU em tempo real: watch -n 1 'ps aux | grep python'"
echo "   Checker saúde: curl http://localhost:8000/health/"
echo ""

log_success "Startup completo. Tempo total: $(date +%s) segundos"
