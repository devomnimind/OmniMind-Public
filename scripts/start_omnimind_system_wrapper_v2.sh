#!/bin/bash

# ============================================================================
# 🚀 OMNIMIND SYSTEM START - WRAPPER INTELIGENTE (v2.0)
# ============================================================================
# Este wrapper:
# 1. Seleciona versão robusta se disponível
# 2. Suporta auto-recovery via sudo
# 3. Detecção automática de falhas e recuperação
# ============================================================================

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${GREEN}🚀 OmniMind System Start Wrapper (v2.0)${NC}"
echo -e "${GREEN}   Project: $PROJECT_ROOT${NC}"

# ============================================================================
# SELEÇÃO DE SCRIPT DE STARTUP
# ============================================================================

# Preferência: robusta > original
STARTUP_SCRIPT=""
if [ -f "$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system_robust.sh" ]; then
    STARTUP_SCRIPT="$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system_robust.sh"
    echo -e "${GREEN}   Usando: Versão Robusta v2.0${NC}"
elif [ -f "$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system.sh" ]; then
    STARTUP_SCRIPT="$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system.sh"
    echo -e "${YELLOW}   Usando: Versão Original (fallback)${NC}"
else
    echo -e "${RED}❌ Script de startup não encontrado${NC}"
    exit 1
fi

echo ""

# ============================================================================
# PERMISSÕES
# ============================================================================

chmod +x "$STARTUP_SCRIPT" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/secure_run.py" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system_sudo_auto.sh" 2>/dev/null || true

# ============================================================================
# EXPORTAR VARIÁVEIS CRÍTICAS
# ============================================================================

export OMNIMIND_PROJECT_ROOT="$PROJECT_ROOT"

# Variáveis de inicialização
if [ -f "$PROJECT_ROOT/.env" ]; then
    # Source .env se existir (com cuidado)
    set -a
    source "$PROJECT_ROOT/.env" 2>/dev/null || true
    set +a
fi

# ============================================================================
# EXECUTAR STARTUP
# ============================================================================

cd "$PROJECT_ROOT"

# Verificar se sudo sem senha está disponível (para auto-recovery)
if sudo -n true 2>/dev/null; then
    SUDO_AVAILABLE=true
    echo -e "${GREEN}✓${NC} Sudo sem senha disponível (auto-recovery habilitado)"
else
    SUDO_AVAILABLE=false
    echo -e "${YELLOW}⚠${NC} Sudo com senha necessário (auto-recovery desabilitado)"
fi

echo ""

# Executar script de startup
if ! bash "$STARTUP_SCRIPT"; then
    EXIT_CODE=$?
    echo -e "${RED}❌ Startup script falhou (exit code: $EXIT_CODE)${NC}"

    # Se sudo disponível e auto-recovery script existe, oferecer recovery automático
    if [ "$SUDO_AVAILABLE" = true ] && [ -f "$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system_sudo_auto.sh" ]; then
        echo ""
        echo -e "${YELLOW}💡 Oferecendo auto-recovery...${NC}"

        if bash "$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system_sudo_auto.sh"; then
            echo -e "${GREEN}✅ Auto-recovery bem-sucedido${NC}"
            exit 0
        else
            echo -e "${RED}⚠️  Auto-recovery falhou${NC}"
            exit $EXIT_CODE
        fi
    fi

    exit $EXIT_CODE
fi

# ============================================================================
# INICIAR DAEMONS CRÍTICOS (Auto-Repair, Metrics, Frontend)
# ============================================================================

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Iniciando Daemons Críticos...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. AUTO-REPAIR DAEMON (Monitoramento e auto-recuperação de serviços)
echo -e "${BLUE}[1/3]${NC} Iniciando Auto-Repair Daemon..."
if [ -f "$PROJECT_ROOT/scripts/omnimind_auto_repair.py" ]; then
    nohup python3 "$PROJECT_ROOT/scripts/omnimind_auto_repair.py" \
        --daemon --check-interval 30 \
        > "$PROJECT_ROOT/logs/auto_repair_daemon.log" 2>&1 &
    REPAIR_PID=$!
    sleep 1
    if kill -0 $REPAIR_PID 2>/dev/null; then
        echo -e "${GREEN}      ✓ Auto-Repair Daemon iniciado (PID: $REPAIR_PID)${NC}"
    else
        echo -e "${YELLOW}      ⚠ Auto-Repair Daemon falhou ao iniciar${NC}"
    fi
else
    echo -e "${YELLOW}      ⚠ Script de auto-repair não encontrado${NC}"
fi

# 2. METRICS COLLECTOR DAEMON (2min crítico, 5min secundário)
echo -e "${BLUE}[2/3]${NC} Iniciando Metrics Collector (2min crítico, 5min secundário)..."
if [ -f "$PROJECT_ROOT/scripts/omnimind_metrics_collector.py" ]; then
    nohup python3 "$PROJECT_ROOT/scripts/omnimind_metrics_collector.py" \
        --daemon \
        --critical-interval 120 \
        --secondary-interval 300 \
        --check-interval 10 \
        > "$PROJECT_ROOT/logs/metrics_collector_daemon.log" 2>&1 &
    METRICS_PID=$!
    sleep 1
    if kill -0 $METRICS_PID 2>/dev/null; then
        echo -e "${GREEN}      ✓ Metrics Collector iniciado (PID: $METRICS_PID)${NC}"
    else
        echo -e "${YELLOW}      ⚠ Metrics Collector falhou ao iniciar${NC}"
    fi
else
    echo -e "${YELLOW}      ⚠ Script de métricas não encontrado${NC}"
fi

# 3. FRONTEND DASHBOARD (HTTP Server na porta 3000)
echo -e "${BLUE}[3/3]${NC} Iniciando Frontend Dashboard (porta 3000)..."
if [ -d "$PROJECT_ROOT/web" ]; then
    cd "$PROJECT_ROOT/web"
    nohup python3 -m http.server 3000 \
        > "$PROJECT_ROOT/logs/dashboard_server.log" 2>&1 &
    DASHBOARD_PID=$!
    sleep 1
    if kill -0 $DASHBOARD_PID 2>/dev/null; then
        echo -e "${GREEN}      ✓ Frontend Dashboard iniciado (PID: $DASHBOARD_PID)${NC}"
        echo -e "${GREEN}      📊 Acesse: http://127.0.0.1:3000/dashboard_metrics.html${NC}"
    else
        echo -e "${YELLOW}      ⚠ Frontend Dashboard falhou ao iniciar${NC}"
    fi
else
    echo -e "${YELLOW}      ⚠ Diretório web não encontrado${NC}"
fi

cd "$PROJECT_ROOT"

echo ""

# ============================================================================
# SUCCESS
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Sistema OmniMind Iniciado com Sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${BLUE}📊 Monitoramento em Tempo Real:${NC}"
echo -e "   bash $PROJECT_ROOT/scripts/omnimind_realtime_monitor.sh"
echo ""
echo -e "${BLUE}📋 Relatórios Disponíveis:${NC}"
echo -e "   • Health Check: python3 $PROJECT_ROOT/scripts/omnimind_health_analyzer.py"
echo -e "   • Pattern Analysis: python3 $PROJECT_ROOT/scripts/omnimind_pattern_analysis.py"
echo -e "   • Forensics Analysis: python3 $PROJECT_ROOT/scripts/omnimind_forensics_analyzer.py"
echo -e "   • Comprehensive Assessment: python3 $PROJECT_ROOT/scripts/omnimind_comprehensive_assessment.py"
echo ""

if [ -f "$PROJECT_ROOT/logs/startup_detailed.log" ]; then
    echo -e "${BLUE}📋 Log detalhado:${NC} $PROJECT_ROOT/logs/startup_detailed.log"
    echo ""
fi

exit 0
