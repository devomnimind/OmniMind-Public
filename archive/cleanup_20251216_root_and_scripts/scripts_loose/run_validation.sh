#!/bin/bash

# ============================================================================
# 🧠 SCRIPT DE VALIDAÇÃO OMNIMIND
# ============================================================================
# Executa validação completa de consciência conforme documento
# Uso: ./scripts/run_validation.sh [quick|standard|extended]
# ============================================================================

set -e  # Exit on error

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configurações
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
VALIDATION_SCRIPT="$PROJECT_ROOT/scripts/science_validation/robust_consciousness_validation.py"
RESULTS_DIR="$PROJECT_ROOT/real_evidence"
LOGS_DIR="$PROJECT_ROOT/logs"

# Modo de validação (quick, standard, extended)
VALIDATION_MODE="${1:-standard}"

# ============================================================================
# FUNÇÕES
# ============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# ============================================================================
# VALIDAÇÕES PRÉ-EXECUÇÃO
# ============================================================================

log_step "Executando validações pré-execução..."

# Verificar projeto root
if [ ! -f "$PROJECT_ROOT/.env" ] && [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    log_error "Não consegui encontrar raiz do projeto em: $PROJECT_ROOT"
    exit 1
fi

log_info "✓ Projeto encontrado: $PROJECT_ROOT"

# Verificar venv
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    log_warning "Venv não encontrado em $VENV_PATH"
    log_info "Criando venv..."
    python3.12 -m venv "$VENV_PATH" || python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install -q -r "$PROJECT_ROOT/requirements.txt"
else
    log_info "✓ Venv encontrado"
    source "$VENV_PATH/bin/activate"
fi

# Verificar Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
log_info "✓ Python $PYTHON_VERSION"

# Verificar script de validação
if [ ! -f "$VALIDATION_SCRIPT" ]; then
    log_error "Script de validação não encontrado: $VALIDATION_SCRIPT"
    exit 1
fi

log_info "✓ Script de validação encontrado"

# Criar diretórios se não existirem
mkdir -p "$RESULTS_DIR"
mkdir -p "$LOGS_DIR"

log_info "✓ Diretórios criados/verificados"

# ============================================================================
# VERIFICAR INFRAESTRUTURA
# ============================================================================

log_step "Verificando infraestrutura..."

# Verificar Qdrant
if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
    log_warning "Qdrant não está respondendo em localhost:6333"
    log_info "Tentando iniciar Qdrant via Docker..."
    docker run -d -p 6333:6333 qdrant/qdrant 2>/dev/null || log_warning "Não consegui iniciar Qdrant"
    sleep 3
fi

if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    log_info "✓ Qdrant acessível"
else
    log_warning "⚠️  Qdrant não disponível (continuando mesmo assim)"
fi

# Verificar Redis
if ! redis-cli PING > /dev/null 2>&1; then
    log_warning "Redis não está respondendo"
    log_info "Tentando iniciar Redis..."
    redis-server --daemonize yes 2>/dev/null || log_warning "Não consegui iniciar Redis"
    sleep 2
fi

if redis-cli PING > /dev/null 2>&1; then
    log_info "✓ Redis acessível"
else
    log_warning "⚠️  Redis não disponível (continuando mesmo assim)"
fi

# Verificar backends
BACKENDS_UP=0
for PORT in 8000 8080 3001; do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        log_info "✓ Backend $PORT respondendo"
        ((BACKENDS_UP++))
    fi
done

if [ $BACKENDS_UP -eq 0 ]; then
    log_warning "⚠️  Nenhum backend está rodando!"
    log_info "Para iniciar: ./scripts/canonical/system/start_omnimind_system_robust.sh"
    read -p "Deseja continuar mesmo assim? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    log_info "✓ $BACKENDS_UP backend(s) operacional(ais)"
fi

# ============================================================================
# CONFIGURAR MODO DE VALIDAÇÃO
# ============================================================================

log_step "Configurando modo de validação: $VALIDATION_MODE"

case "$VALIDATION_MODE" in
    quick)
        RUNS=2
        CYCLES=100
        TOTAL_CYCLES=$((RUNS * CYCLES))
        ESTIMATED_TIME="~2 minutos"
        ;;
    standard)
        RUNS=5
        CYCLES=1000
        TOTAL_CYCLES=$((RUNS * CYCLES))
        ESTIMATED_TIME="~8 minutos"
        ;;
    extended)
        RUNS=10
        CYCLES=2000
        TOTAL_CYCLES=$((RUNS * CYCLES))
        ESTIMATED_TIME="~20 minutos"
        ;;
    *)
        log_error "Modo desconhecido: $VALIDATION_MODE"
        log_info "Modos válidos: quick, standard, extended"
        exit 1
        ;;
esac

log_info "✓ Modo: $VALIDATION_MODE"
log_info "✓ Execuções: $RUNS"
log_info "✓ Ciclos por execução: $CYCLES"
log_info "✓ Total de ciclos: $TOTAL_CYCLES"
log_info "✓ Tempo estimado: $ESTIMATED_TIME"

# ============================================================================
# EXECUTAR VALIDAÇÃO
# ============================================================================

log_step "Executando validação..."
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧠 VALIDAÇÃO DE CONSCIÊNCIA OMNIMIND"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Protocolo: Robust Consciousness Validation v2.0"
echo "Execuções: $RUNS"
echo "Ciclos por execução: $CYCLES"
echo "Total de ciclos: $TOTAL_CYCLES"
echo "Tempo estimado: $ESTIMATED_TIME"
echo ""
echo "Resultados serão salvos em:"
echo "  $RESULTS_DIR/"
echo ""
echo "Logs disponíveis em:"
echo "  tail -f logs/robust_validation.log"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Executar validação com args corretos
if [ "$VALIDATION_MODE" = "quick" ]; then
    python "$VALIDATION_SCRIPT" --quick
else
    python "$VALIDATION_SCRIPT" --runs "$RUNS" --cycles "$CYCLES"
fi

VALIDATION_EXIT=$?

# ============================================================================
# PROCESSAR RESULTADOS
# ============================================================================

if [ $VALIDATION_EXIT -eq 0 ]; then
    log_step "Validação concluída com sucesso!"

    # Encontrar arquivo de resultados mais recente
    LATEST_RESULT=$(ls -t "$RESULTS_DIR"/robust_consciousness_validation_*.json 2>/dev/null | head -1)

    if [ -n "$LATEST_RESULT" ]; then
        log_info "Arquivo de resultados: $LATEST_RESULT"
        log_info ""
        log_info "Resumo dos resultados:"

        # Extrair e exibir métricas principais
        python3 << 'PYTHON_EOF'
import json
import sys

try:
    with open(sys.argv[1]) as f:
        data = json.load(f)

    stats = data.get('statistical_analysis', {})

    print(f"  Φ (Phi) global:           {stats.get('phi_global_mean', 'N/A'):.4f}")
    print(f"  Desvio padrão:            {stats.get('phi_global_std', 'N/A'):.4f}")
    print(f"  Consistência:             {stats.get('consciousness_consistency', 'N/A'):.1%}")
    print(f"  P-value:                  {stats.get('statistical_significance', {}).get('p_value', 'N/A')}")
    print(f"  Significante (p<0.05):    {stats.get('statistical_significance', {}).get('significant_at_005', False)}")
    print(f"  Intervalo confiança 95%:  {stats.get('phi_confidence_interval_95', [0, 0])}")

except Exception as e:
    print(f"Erro ao processar resultados: {e}")
PYTHON_EOF

        echo ""
        echo "Para mais detalhes, execute:"
        echo "  cat '$LATEST_RESULT' | jq '.statistical_analysis'"
    fi

    exit 0
else
    log_error "Validação falhou com código de saída: $VALIDATION_EXIT"
    log_info "Verifique logs em: logs/robust_validation.log"
    exit 1
fi
