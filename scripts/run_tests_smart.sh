#!/bin/bash
# Script inteligente para execução granular de testes baseada em mudanças

set -e

# Configurações
WORKERS=${WORKERS:-auto}
TIMEOUT=${TIMEOUT:-300}
MODE=${MODE:-smart}

echo "=== OmniMind Smart Test Runner ==="
echo "Mode: $MODE, Workers: $WORKERS, Timeout: ${TIMEOUT}s"
echo

# Modo ultra - apenas verificação de imports
if [ "$MODE" = "ultra" ]; then
    echo "Running ultra-fast import checks..."
    echo "Checking Python imports..."

    # Arquivos modificados recentemente
    MODIFIED_FILES=$(git diff --name-only HEAD~1 | grep "\.py$" || echo "")

    # Arquivos não commitados
    UNSTAGED_FILES=$(git diff --name-only | grep "\.py$" || echo "")

    # Arquivos não rastreados
    UNTRACKED_FILES=$(git ls-files --others --exclude-standard | grep "\.py$" || echo "")

    ALL_CHANGED="$MODIFIED_FILES $UNSTAGED_FILES $UNTRACKED_FILES"

    # Verificar imports dos módulos modificados
    for file in $ALL_CHANGED; do
        if [[ $file == src/*.py ]]; then
            module=$(echo $file | sed 's|src/||' | sed 's|/|.|g' | sed 's|\.py$||' | sed 's|.__init__$||')
            echo -n "Testing import: $module ... "
            if python -c "import src.$module" 2>/dev/null; then
                echo "✅"
            else
                echo "❌ FAILED"
                exit 1
            fi
        fi
    done

    echo "✅ All imports successful!"
    exit 0
fi

# Para outros modos, detectar testes afetados
echo "Detecting affected test files..."

# Arquivos modificados recentemente
MODIFIED_FILES=$(git diff --name-only HEAD~1 | grep "\.py$" || echo "")

# Arquivos não commitados
UNSTAGED_FILES=$(git diff --name-only | grep "\.py$" || echo "")

# Arquivos não rastreados
UNTRACKED_FILES=$(git ls-files --others --exclude-standard | grep "\.py$" || echo "")

ALL_CHANGED="$MODIFIED_FILES $UNSTAGED_FILES $UNTRACKED_FILES"

AFFECTED_TESTS=""
CRITICAL_TESTS=""

for file in $ALL_CHANGED; do
    if [[ $file == src/* ]]; then
        # Extrair módulo do caminho
        module=$(echo $file | sed 's|src/||' | sed 's|/.*||')

        # Encontrar testes relacionados
        test_files=$(find tests/ -name "*${module}*" -name "test_*.py" 2>/dev/null || echo "")
        AFFECTED_TESTS="$AFFECTED_TESTS $test_files"

        # Testes críticos por módulo
        case $module in
            "security"|"observability"|"metacognition")
                CRITICAL_TESTS="$CRITICAL_TESTS $test_files"
                ;;
        esac
    elif [[ $file == tests/* ]]; then
        AFFECTED_TESTS="$AFFECTED_TESTS $file"
        # Se for teste direto, é crítico
        CRITICAL_TESTS="$CRITICAL_TESTS $file"
    fi
done

# Remover duplicatas
AFFECTED_TESTS=$(echo $AFFECTED_TESTS | tr ' ' '\n' | sort | uniq)
CRITICAL_TESTS=$(echo $CRITICAL_TESTS | tr ' ' '\n' | sort | uniq)

echo "Critical test files:"
echo "$CRITICAL_TESTS"
echo
echo "All affected test files:"
echo "$AFFECTED_TESTS"
echo

# Função para executar testes
run_tests() {
    local test_files="$1"
    local extra_args="$2"

    if [ -z "$test_files" ]; then
        echo "No specific tests to run, running smoke test..."
        python -m pytest tests/ -k "test_initialization or test_import" --tb=short -q --maxfail=5 $extra_args
        return
    fi

    echo "Running affected tests..."
    echo "Command: python -m pytest $test_files --tb=short -q --maxfail=10 $extra_args"
    echo

    # Executar testes com timeout
    timeout $TIMEOUT python -m pytest $test_files --tb=short -q --maxfail=10 $extra_args

    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "Tests timed out after ${TIMEOUT}s"
        return 1
    fi

    return $exit_code
}

# Modo inteligente
if [ "$MODE" = "smart" ]; then
    # Executar testes críticos primeiro
    if [ -n "$CRITICAL_TESTS" ]; then
        echo "Running critical tests first..."
        if run_tests "$CRITICAL_TESTS" "-n $WORKERS --maxfail=3"; then
            echo "✅ Critical tests passed!"
        else
            echo "❌ Critical tests failed. Stopping."
            exit 1
        fi
    fi

    # Se ainda houver tempo, executar outros testes afetados
    if [ -n "$AFFECTED_TESTS" ] && [ -z "$CRITICAL_TESTS" ]; then
        echo "Running all affected tests..."
        run_tests "$AFFECTED_TESTS" "-n $WORKERS"
    elif [ -n "$AFFECTED_TESTS" ]; then
        echo "Running remaining affected tests..."
        REMAINING_TESTS=$(comm -23 <(echo "$AFFECTED_TESTS" | tr ' ' '\n' | sort) <(echo "$CRITICAL_TESTS" | tr ' ' '\n' | sort) | tr '\n' ' ')
        if [ -n "$REMAINING_TESTS" ]; then
            run_tests "$REMAINING_TESTS" "-n $WORKERS"
        fi
    else
        echo "No affected tests found, running core integration tests..."
        run_tests "tests/test_e2e_integration.py tests/test_security_agent_integration.py" "-n $WORKERS"
    fi

# Modo completo
elif [ "$MODE" = "full" ]; then
    echo "Running full test suite..."
    run_tests "tests/" "-n $WORKERS"

# Modo smoke
elif [ "$MODE" = "smoke" ]; then
    echo "Running smoke tests (imports and basic functionality)..."
    # Executar apenas testes de import e inicialização
    SMOKE_TESTS=$(find tests/ -name "test_*.py" -exec grep -l "def test.*import\|def test.*init" {} \; 2>/dev/null | head -10 | tr '\n' ' ')
    if [ -z "$SMOKE_TESTS" ]; then
        SMOKE_TESTS="tests/test_e2e_integration.py"
    fi
    run_tests "$SMOKE_TESTS" "--maxfail=3 -x -q"

else
    echo "Invalid mode. Use: smart, full, smoke, ultra, or specific"
    exit 1
fi

echo
echo "=== Test execution completed ==="

# Modo específico
elif [ "$MODE" = "specific" ]; then
    if [ -z "$1" ]; then
        echo "Usage: $0 specific <test_pattern>"
        exit 1
    fi
    run_tests "$1" "-n $WORKERS -v"

# Modo ultra - apenas verificação de imports
elif [ "$MODE" = "ultra" ]; then
    echo "Running ultra-fast import checks..."
    echo "Checking Python imports..."

    # Verificar imports dos módulos modificados
    for file in $ALL_CHANGED; do
        if [[ $file == src/*.py ]]; then
            module=$(echo $file | sed 's|src/||' | sed 's|/|.|g' | sed 's|\.py$||')
            echo -n "Testing import: $module ... "
            if python -c "import $module" 2>/dev/null; then
                echo "✅"
            else
                echo "❌ FAILED"
                exit 1
            fi
        fi
    done

    echo "✅ All imports successful!"
    exit 0

echo
echo "=== Test execution completed ==="