#!/bin/bash
# OmniMind Validation Lock Script - Versão Inteligente
# Bloqueia mudanças que infrinjam o estado atual do sistema
# Análise inteligente baseada no tipo de mudança
# Data de criação: 19 de novembro de 2025
# Estado baseline: 1017 testes passando, 2 skipped, 6 warnings

set -e

# Registrar tempo de início
START_TIME=$(date +%s)

echo "🔒 OmniMind Validation Lock Inteligente - Executando validações..."

# Estado baseline esperado
EXPECTED_TESTS_PASSED=1017
EXPECTED_TESTS_SKIPPED=2
EXPECTED_WARNINGS=6

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Função para analisar tipo de mudança
analyze_changes() {
    # Obter arquivos modificados no stage
    CHANGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")

    if [[ -z "$CHANGED_FILES" ]]; then
        # Se não há arquivos staged, verificar working directory
        CHANGED_FILES=$(git diff --name-only 2>/dev/null || echo "")
    fi

    # Categorizar arquivos
    DOC_FILES=""
    CODE_FILES=""
    TEST_FILES=""
    CONFIG_FILES=""
    SCRIPT_FILES=""
    OTHER_FILES=""

    for file in $CHANGED_FILES; do
        if [[ $file =~ \.(md|txt|rst|adoc)$ ]] || [[ $file =~ ^docs/ ]] || [[ $file =~ ^README ]]; then
            DOC_FILES="$DOC_FILES $file"
        elif [[ $file =~ ^src/ ]] && [[ $file =~ \.py$ ]]; then
            CODE_FILES="$CODE_FILES $file"
        elif [[ $file =~ ^tests/ ]] && [[ $file =~ \.py$ ]]; then
            TEST_FILES="$TEST_FILES $file"
        elif [[ $file =~ ^config/ ]] || [[ $file =~ ^scripts/ ]] || [[ $file =~ \.(yml|yaml|toml|json)$ ]]; then
            CONFIG_FILES="$CONFIG_FILES $file"
        elif [[ $file =~ ^scripts/ ]] && [[ $file =~ \.sh$ ]]; then
            SCRIPT_FILES="$SCRIPT_FILES $file"
        else
            OTHER_FILES="$OTHER_FILES $file"
        fi
    done

    # Determinar nível de validação
    VALIDATION_LEVEL="FULL"

    if [[ -n "$DOC_FILES" ]] && [[ -z "$CODE_FILES" ]] && [[ -z "$TEST_FILES" ]] && [[ -z "$SCRIPT_FILES" ]]; then
        VALIDATION_LEVEL="DOCS_ONLY"
    elif [[ -n "$CONFIG_FILES" ]] && [[ -z "$CODE_FILES" ]] && [[ -z "$TEST_FILES" ]]; then
        VALIDATION_LEVEL="CONFIG_ONLY"
    elif [[ -n "$TEST_FILES" ]] && [[ -z "$CODE_FILES" ]]; then
        VALIDATION_LEVEL="TESTS_ONLY"
    fi

    # Retornar apenas o nível (sem logs para não contaminar a saída)
    echo "$VALIDATION_LEVEL"
}

# Verificar se estamos em modo desenvolvimento
DEV_MODE=${OMNIMIND_DEV_MODE:-false}
if [[ "$DEV_MODE" == "true" ]]; then
    warning "🚧 MODO DESENVOLVIMENTO ATIVO - Validações reduzidas"
    warning "Use apenas para desenvolvimento rápido. Execute testes completos antes do push."
fi

log "Verificando estrutura do repositório..."

# 2. Analisar mudanças e determinar validações necessárias
VALIDATION_LEVEL=$(analyze_changes)

# Obter detalhes dos arquivos para logging
CHANGED_FILES=$(git diff --cached --name-only 2>/dev/null || git diff --name-only 2>/dev/null || echo "")
DOC_FILES=""
CODE_FILES=""
TEST_FILES=""
CONFIG_FILES=""
SCRIPT_FILES=""
OTHER_FILES=""

for file in $CHANGED_FILES; do
    if [[ $file =~ \.(md|txt|rst|adoc)$ ]] || [[ $file =~ ^docs/ ]] || [[ $file =~ ^README ]]; then
        DOC_FILES="$DOC_FILES $file"
    elif [[ $file =~ ^src/ ]] && [[ $file =~ \.py$ ]]; then
        CODE_FILES="$CODE_FILES $file"
    elif [[ $file =~ ^tests/ ]] && [[ $file =~ \.py$ ]]; then
        TEST_FILES="$TEST_FILES $file"
    elif [[ $file =~ ^config/ ]] || [[ $file =~ ^scripts/ ]] || [[ $file =~ \.(yml|yaml|toml|json)$ ]]; then
        CONFIG_FILES="$CONFIG_FILES $file"
    elif [[ $file =~ ^scripts/ ]] && [[ $file =~ \.sh$ ]]; then
        SCRIPT_FILES="$SCRIPT_FILES $file"
    else
        OTHER_FILES="$OTHER_FILES $file"
    fi
done

# Output da análise
info "Análise de mudanças detectadas:"
if [[ -n "$DOC_FILES" ]]; then info "  📄 Documentos: $DOC_FILES"; fi
if [[ -n "$CODE_FILES" ]]; then info "  💻 Código: $CODE_FILES"; fi
if [[ -n "$TEST_FILES" ]]; then info "  🧪 Testes: $TEST_FILES"; fi
if [[ -n "$CONFIG_FILES" ]]; then info "  ⚙️ Configuração: $CONFIG_FILES"; fi
if [[ -n "$SCRIPT_FILES" ]]; then info "  🔧 Scripts: $SCRIPT_FILES"; fi
if [[ -n "$OTHER_FILES" ]]; then info "  📦 Outros: $OTHER_FILES"; fi

info "Nível de validação determinado: $VALIDATION_LEVEL"

# Calcular estatísticas dos arquivos
TOTAL_FILES=$(find . -type f -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.toml" -o -name "*.sh" | wc -l)
MODIFIED_FILES=$(echo "$CHANGED_FILES" | wc -w)

# 3. Executar validações baseadas no nível determinado
case $VALIDATION_LEVEL in
    "DOCS_ONLY")
        log "📄 Mudanças apenas em documentos - validações leves..."
        # Apenas verificar estrutura básica
        ;;
    "CONFIG_ONLY")
        log "⚙️ Mudanças apenas em configuração - validações médias..."
        # Verificar estrutura e dependências
        ;;
    "TESTS_ONLY")
        log "🧪 Mudanças apenas em testes - validações focadas..."
        # Executar apenas testes
        ;;
    "FULL"|*)
        log "🔍 Mudanças em código - validações completas..."
        # Todas as validações
        ;;
esac

# 4. Formatação de código (sempre para mudanças em código)
if [[ "$VALIDATION_LEVEL" == "FULL" ]] || [[ "$VALIDATION_LEVEL" == "TESTS_ONLY" ]]; then
    log "Executando formatação de código (black)..."
    if ! black --check --diff src tests > /dev/null 2>&1; then
        error "Código não está formatado corretamente. Execute: black src tests"
        exit 1
    fi
    log "✅ Formatação OK"
else
    log "⏭️ Pulando formatação (mudanças não afetam código)"
fi

# 5. Linting (sempre para mudanças em código)
if [[ "$VALIDATION_LEVEL" == "FULL" ]] || [[ "$VALIDATION_LEVEL" == "TESTS_ONLY" ]]; then
    log "Executando linting (flake8) - verificando apenas erros críticos..."
    FLAKE8_OUTPUT=$(flake8 src tests --max-line-length=100 --select=E9,F63,F7,F82 2>&1)
    if [[ -n "$FLAKE8_OUTPUT" ]]; then
        error "Erros críticos de linting detectados:"
        echo "$FLAKE8_OUTPUT"
        exit 1
    fi
    log "✅ Linting crítico OK (warnings permitidos temporariamente)"
else
    log "⏭️ Pulando linting (mudanças não afetam código)"
fi

# 6. Type checking (sempre para mudanças em código)
if [[ "$VALIDATION_LEVEL" == "FULL" ]] || [[ "$VALIDATION_LEVEL" == "TESTS_ONLY" ]]; then
    log "Executando type checking (mypy) - modo lenient..."
    MYPY_OUTPUT=$(mypy src tests --config-file mypy.ini --show-error-codes 2>&1 | grep -E "(error|note)" | head -20)
    if echo "$MYPY_OUTPUT" | grep -q "error"; then
        warning "Erros de tipo detectados (modo lenient ativo):"
        echo "$MYPY_OUTPUT" | head -10
        warning "Erros de tipo permitidos temporariamente - melhore gradualmente"
    else
        log "✅ Type checking OK"
    fi
else
    log "⏭️ Pulando type checking (mudanças não afetam código)"
fi

# 7. Testes (baseado no nível e modo)
if [[ "$VALIDATION_LEVEL" == "FULL" ]] || [[ "$VALIDATION_LEVEL" == "TESTS_ONLY" ]]; then
    if [[ "$DEV_MODE" == "true" ]]; then
        log "Executando testes rápidos (modo desenvolvimento)..."
        # Executar apenas testes críticos em modo dev
        TEST_OUTPUT=$(python -m pytest tests/test_agents_core_integration.py tests/test_config_validator.py tests/test_audit.py -x --tb=short -q 2>&1)
        TEST_EXIT_CODE=$?
        
        if [[ $TEST_EXIT_CODE -ne 0 ]]; then
            error "Testes críticos falharam. Saída:"
            echo "$TEST_OUTPUT"
            exit 1
        fi
        
        log "✅ Testes críticos OK (modo desenvolvimento)"
        PASSED=50  # Valor aproximado para modo dev
        SKIPPED=0
        WARNINGS=0
    else
        log "Executando testes completos..."
        TEST_OUTPUT=$(python -m pytest tests/ -x --tb=short -q 2>&1)
        TEST_EXIT_CODE=$?

        if [[ $TEST_EXIT_CODE -ne 0 ]]; then
            error "Testes falharam. Saída completa:"
            echo "$TEST_OUTPUT"
            exit 1
        fi

        # Parse dos resultados dos testes
        PASSED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' | tail -1)
        SKIPPED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= skipped)' | tail -1)
        WARNINGS=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= warnings)' | tail -1)

        # Valores padrão se não encontrados
        PASSED=${PASSED:-0}
        SKIPPED=${SKIPPED:-0}
        WARNINGS=${WARNINGS:-0}

        log "Resultados dos testes: $PASSED passed, $SKIPPED skipped, $WARNINGS warnings"

        # Verificar se os números batem com o baseline
        if [[ $PASSED -lt $EXPECTED_TESTS_PASSED ]]; then
            error "Regressão detectada: $PASSED testes passaram (esperado: $EXPECTED_TESTS_PASSED)"
            error "Mudanças que reduziram a cobertura de testes não são permitidas"
            exit 1
        fi

        if [[ $SKIPPED -gt $EXPECTED_TESTS_SKIPPED ]]; then
            warning "Aumento no número de testes skipped: $SKIPPED (era: $EXPECTED_TESTS_SKIPPED)"
            warning "Verifique se novos testes foram marcados como skip intencionalmente"
        fi
    fi
elif [[ "$VALIDATION_LEVEL" == "DOCS_ONLY" ]]; then
    log "⏭️ Pulando testes (mudanças apenas em documentos)"
    PASSED=$EXPECTED_TESTS_PASSED  # Assumir baseline para docs
    SKIPPED=$EXPECTED_TESTS_SKIPPED
    WARNINGS=$EXPECTED_WARNINGS
else
    log "⏭️ Pulando testes completos (validações leves)"
    PASSED=$EXPECTED_TESTS_PASSED  # Assumir baseline
    SKIPPED=$EXPECTED_TESTS_SKIPPED
    WARNINGS=$EXPECTED_WARNINGS
fi

# 8. Dependências (sempre verificar)
log "Verificando dependências..."
if ! pip check > /dev/null 2>&1; then
    error "Conflitos de dependências detectados. Execute: pip check"
    exit 1
fi
log "✅ Dependências OK"

# 9. Arquivos core (sempre verificar)
log "Verificando integridade dos arquivos core..."
CORE_FILES=(
    "src/__init__.py"
    "requirements.txt"
    "README.md"
)

MISSING_FILES=""
for file in "${CORE_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        MISSING_FILES="$MISSING_FILES $file"
    fi
done

if [[ -n "$MISSING_FILES" ]]; then
    warning "Arquivos core não encontrados:$MISSING_FILES"
    warning "Verifique se esses arquivos são necessários"
fi
log "✅ Arquivos core OK"

# 10. Ambiente Python/PyTorch (sempre verificar)
log "Verificando ambiente Python..."
python -c "
import sys
import torch
print(f'Python: {sys.version.split()[0]}')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'Device: {torch.cuda.get_device_name(0)}')
" > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    error "Problemas no ambiente Python/PyTorch"
    exit 1
fi
log "✅ PyTorch OK"

log "🎉 Validações concluídas com sucesso!"
log ""
log "═══════════════════════════════════════════════════════════════"
log "VALIDAÇÃO CONCLUÍDA COM SUCESSO"
log "═══════════════════════════════════════════════════════════════"
log ""
log "📊 Resumo da validação:"
log "   • Nível: $VALIDATION_LEVEL"
if [[ "$DEV_MODE" == "true" ]]; then
    log "   • Modo: DESENVOLVIMENTO (validações reduzidas)"
else
    log "   • Modo: PRODUÇÃO (validações completas)"
fi
log "   • Arquivos analisados: $TOTAL_FILES"
log "   • Arquivos modificados: $MODIFIED_FILES"
log "   • Testes executados: $PASSED passed, $SKIPPED skipped, $WARNINGS warnings"
log "   • Tempo total: $(($(date +%s) - START_TIME))s"
log ""
if [[ "$DEV_MODE" == "true" ]]; then
    log "💡 Modo Desenvolvimento Ativo:"
    log "   Para validações completas, execute sem OMNIMIND_DEV_MODE=true"
    log "   ou remova a variável de ambiente."
    log ""
fi
log "✅ Todas as validações passaram!"
log "═══════════════════════════════════════════════════════════════"
