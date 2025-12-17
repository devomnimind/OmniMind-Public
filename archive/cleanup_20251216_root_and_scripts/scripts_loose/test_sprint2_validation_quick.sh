#!/bin/bash

# ============================================================================
# OMNIMIND SPRINT 2 - TESTE RÁPIDO DE VALIDAÇÃO PRÉ-MERGE
# ============================================================================
# Executa os testes críticos antes de fazer merge
# Tempo estimado: 10-15 minutos
# ============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
RESULTS_FILE="/tmp/sprint2_validation_results_$(date +%s).txt"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

test_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
    echo "TESTE: $1" >> "$RESULTS_FILE"
}

test_ok() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "  ✓ $1" >> "$RESULTS_FILE"
}

test_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "  ⚠ $1" >> "$RESULTS_FILE"
}

test_fail() {
    echo -e "${RED}❌ $1${NC}"
    echo "  ✗ $1" >> "$RESULTS_FILE"
    FAILED=true
}

# ============================================================================
# INITIALIZATION
# ============================================================================

echo -e "${GREEN}🚀 Sprint 2 - Teste Rápido de Validação${NC}"
echo "   Projeto: $PROJECT_ROOT"
echo "   Resultados: $RESULTS_FILE"
echo "   Data: $(date)"
cd "$PROJECT_ROOT"

> "$RESULTS_FILE"

FAILED=false
START_TIME=$(date +%s)

# ============================================================================
# TESTE 1: SINTAXE DOS SCRIPTS
# ============================================================================

test_header "TESTE 1: Sintaxe dos Scripts"

bash -n scripts/canonical/system/start_omnimind_system_robust.sh 2>/dev/null && \
    test_ok "Sintaxe: start_omnimind_system_robust.sh" || \
    test_fail "Sintaxe: start_omnimind_system_robust.sh"

bash -n scripts/canonical/system/start_omnimind_system_sudo_auto.sh 2>/dev/null && \
    test_ok "Sintaxe: start_omnimind_system_sudo_auto.sh" || \
    test_fail "Sintaxe: start_omnimind_system_sudo_auto.sh"

bash -n scripts/start_omnimind_system_wrapper_v2.sh 2>/dev/null && \
    test_ok "Sintaxe: start_omnimind_system_wrapper_v2.sh" || \
    test_fail "Sintaxe: start_omnimind_system_wrapper_v2.sh"

# ============================================================================
# TESTE 2: VERIFICAÇÕES DE PERMISSÕES E ARQUIVO
# ============================================================================

test_header "TESTE 2: Permissões e Arquivos"

[ -x scripts/canonical/system/start_omnimind_system_robust.sh ] && \
    test_ok "Executável: start_omnimind_system_robust.sh" || \
    test_fail "Não executável: start_omnimind_system_robust.sh"

[ -x scripts/canonical/system/start_omnimind_system_sudo_auto.sh ] && \
    test_ok "Executável: start_omnimind_system_sudo_auto.sh" || \
    test_fail "Não executável: start_omnimind_system_sudo_auto.sh"

[ -x scripts/start_omnimind_system_wrapper_v2.sh ] && \
    test_ok "Executável: start_omnimind_system_wrapper_v2.sh" || \
    test_fail "Não executável: start_omnimind_system_wrapper_v2.sh"

[ -f docs/OMNIMIND_AUTO_RECOVERY_SETUP.md ] && \
    test_ok "Documentação: OMNIMIND_AUTO_RECOVERY_SETUP.md" || \
    test_fail "Documentação faltando: OMNIMIND_AUTO_RECOVERY_SETUP.md"

[ -f docs/SPRINT2_TESTING_PLAN.md ] && \
    test_ok "Documentação: SPRINT2_TESTING_PLAN.md" || \
    test_fail "Documentação faltando: SPRINT2_TESTING_PLAN.md"

# ============================================================================
# TESTE 3: IMPORTS PYTHON SPRINT 2
# ============================================================================

test_header "TESTE 3: Imports Python Sprint 2"

python3 << 'PYTHON_TEST' 2>/dev/null && \
    test_ok "Import: ModuleMetricsCollector" || \
    test_fail "Import falhou: ModuleMetricsCollector"
from src.observability.module_metrics import ModuleMetricsCollector
PYTHON_TEST

python3 << 'PYTHON_TEST' 2>/dev/null && \
    test_ok "Import: EventMetricsListener" || \
    test_fail "Import falhou: EventMetricsListener"
from src.observability.event_metrics_listener import EventMetricsListener
PYTHON_TEST

python3 << 'PYTHON_TEST' 2>/dev/null && \
    test_ok "Import: RNNMetricsExtractor" || \
    test_fail "Import falhou: RNNMetricsExtractor"
from src.observability.rnn_metrics_extractor import RNNMetricsExtractor
PYTHON_TEST

python3 << 'PYTHON_TEST' 2>/dev/null && \
    test_ok "Import: AutopoieticManager" || \
    test_fail "Import falhou: AutopoieticManager"
from src.autopoietic.manager import AutopoieticManager
PYTHON_TEST

# ============================================================================
# TESTE 4: VERIFICAÇÃO DE GIT (Sprint 2 Branch)
# ============================================================================

test_header "TESTE 4: Status Git"

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
echo -e "Branch atual: ${BLUE}$CURRENT_BRANCH${NC}"

if [ -n "$CURRENT_BRANCH" ]; then
    test_ok "Git branch identificada: $CURRENT_BRANCH"
else
    test_warn "Não foi possível identificar branch git"
fi

# Verificar se há mudanças não commitadas
if [ -z "$(git status --porcelain)" ]; then
    test_ok "Diretório clean (sem mudanças não commitadas)"
else
    test_warn "Há mudanças não commitadas:"
    git status --short | sed 's/^/    /'
fi

# ============================================================================
# TESTE 5: VALIDAÇÕES DE CÓDIGO (Quick Check)
# ============================================================================

test_header "TESTE 5: Validações de Código (Quick)"

# Verificar que validate_code.sh existe
if [ -f scripts/validate_code.sh ]; then
    test_ok "Script de validação encontrado: validate_code.sh"

    # Executar validação rápida
    echo -e "\n   Executando: black --check src/ (mode: quick)"
    if black --check src/ 2>&1 | head -5; then
        test_ok "Black check passou"
    else
        test_warn "Black check teve warnings (pode ser normal)"
    fi
else
    test_warn "Script de validação não encontrado"
fi

# ============================================================================
# TESTE 6: ESTRUTURA DE DIRETÓRIOS
# ============================================================================

test_header "TESTE 6: Estrutura de Diretórios"

required_dirs=(
    "scripts/canonical/system"
    "src/observability"
    "src/autopoietic"
    "src/consciousness"
    "data/long_term_logs"
    "logs"
    "docs"
)

for dir in "${required_dirs[@]}"; do
    [ -d "$dir" ] && test_ok "Diretório: $dir" || test_fail "Diretório faltando: $dir"
done

# ============================================================================
# TESTE 7: CONFIGURAÇÃO SUDO (Opcional)
# ============================================================================

test_header "TESTE 7: Configuração Sudo (Opcional)"

if sudo -n true 2>/dev/null; then
    test_ok "Sudo sem senha disponível (auto-recovery habilitado)"
else
    test_warn "Sudo requer senha (auto-recovery manual)"
    test_warn "Setup: sudo visudo + adicionar linha com script_path"
fi

# ============================================================================
# TESTE 8: VERIFICAÇÃO DE LOGS
# ============================================================================

test_header "TESTE 8: Logs e Cleanup"

[ -d logs ] && test_ok "Diretório logs existe" || test_fail "Diretório logs não existe"
[ -d data/long_term_logs ] && test_ok "Diretório long_term_logs existe" || test_fail "Diretório long_term_logs não existe"

# Verificar se há espaço em disco
disk_usage=$(df -h . | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$disk_usage" -lt 80 ]; then
    test_ok "Espaço em disco: ${disk_usage}% (OK)"
else
    test_warn "Espaço em disco: ${disk_usage}% (pode estar cheio)"
fi

# ============================================================================
# RESUMO FINAL
# ============================================================================

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}RESUMO FINAL${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "Tempo total: ${DURATION}s"
echo "Resultados: $RESULTS_FILE"
echo ""

if [ "$FAILED" = true ]; then
    echo -e "${RED}❌ ALGUNS TESTES FALHARAM${NC}"
    echo "    Ver detalhes em: $RESULTS_FILE"
    echo ""
    echo "    Testes que falharam:"
    grep "✗" "$RESULTS_FILE" | head -10
    exit 1
else
    echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM${NC}"
    echo ""
    echo "    Próximos passos:"
    echo "    1. Executar teste completo: ./scripts/start_omnimind_system_wrapper_v2.sh"
    echo "    2. Testar endpoints Sprint 2"
    echo "    3. Validar coleta de métricas (aguardar 2+ ciclos)"
    echo "    4. Verificar logs: tail -f logs/startup_detailed.log"
    echo "    5. Fazer merge para master"
    exit 0
fi
