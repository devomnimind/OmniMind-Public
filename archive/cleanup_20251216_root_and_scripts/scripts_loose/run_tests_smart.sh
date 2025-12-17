#!/bin/bash

# ========================================================================
# 🚀 EXECUTOR DE TESTES OmniMind - COM TODAS AS OPÇÕES
# ========================================================================
# Este script facilita rodar testes com diferentes configurações
# ========================================================================

set -e

cd /home/fahbrain/projects/omnimind

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  🧪 OmniMind Test Suite Runner${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_mode() {
    echo -e "${YELLOW}📋 Modo Selecionado: $1${NC}\n"
}

show_menu() {
    echo "Escolha o modo de execução:"
    echo "1️⃣  RECOMENDADO (Verboso + Debug + Top lentos)"
    echo "2️⃣  ULTRA DETALHADO (Mostra tudo + Sem captura)"
    echo "3️⃣  RÁPIDO (Apenas resultado final)"
    echo "4️⃣  DEBUG (Logs DEBUG + Rastreamento completo)"
    echo "5️⃣  APENAS FALHAS (Retoma últimos que falharam)"
    echo "6️⃣  ESPECÍFICO (Escolha arquivo/teste)"
    echo -e "\n0️⃣  Sair\n"
}

run_recommended() {
    print_mode "RECOMENDADO"
    echo "🏃 Executando com: -vv, DEBUG logs, Top 5 lentos..."
    OMNIMIND_MODE=test python -m pytest tests/integrations/ \
        -vv \
        --log-cli-level=DEBUG \
        --durations=5 \
        --tb=short
}

run_ultra_verbose() {
    print_mode "ULTRA DETALHADO"
    echo "🏃 Executando com: -vvv, Sem captura, Traceback longo..."
    OMNIMIND_MODE=test python -m pytest tests/integrations/ \
        -vvv \
        --log-cli-level=DEBUG \
        --tb=long \
        -s \
        --capture=no
}

run_quick() {
    print_mode "RÁPIDO"
    echo "🏃 Executando com: -q (modo quietly)..."
    OMNIMIND_MODE=test python -m pytest tests/integrations/ \
        -q \
        --tb=line
}

run_debug() {
    print_mode "DEBUG"
    echo "🏃 Executando com: Logs DEBUG + Rastreamento..."
    OMNIMIND_MODE=test python -m pytest tests/integrations/ \
        -v \
        --log-cli-level=DEBUG \
        --log-file=data/test_reports/pytest_debug.log \
        --tb=short \
        --pdb-trace  # Para em breakpoint
}

run_last_failed() {
    print_mode "APENAS ÚLTIMAS FALHAS"
    echo "🏃 Retomando últimos testes que falharam..."
    OMNIMIND_MODE=test python -m pytest tests/integrations/ \
        -v \
        --lf \
        --tb=short
}

run_specific() {
    print_mode "TESTE ESPECÍFICO"
    echo "Exemplos:"
    echo "  - tests/integrations/test_mcp_python_server.py"
    echo "  - tests/integrations/test_mcp_python_server.py::TestPythonMCPServer"
    echo "  - tests/integrations/test_mcp_python_server.py::TestPythonMCPServer::test_execute_code_basic"
    echo ""
    read -p "Cole o caminho do teste: " test_path

    if [ -z "$test_path" ]; then
        echo -e "${RED}❌ Caminho vazio!${NC}"
        return
    fi

    OMNIMIND_MODE=test python -m pytest "$test_path" \
        -vv \
        --log-cli-level=DEBUG \
        --tb=short
}

print_header

# Se passou argumento, usa
if [ -n "$1" ]; then
    case "$1" in
        1|recomendado)
            run_recommended
            ;;
        2|ultra)
            run_ultra_verbose
            ;;
        3|rapido|quick)
            run_quick
            ;;
        4|debug)
            run_debug
            ;;
        5|lf|last)
            run_last_failed
            ;;
        6|specific)
            run_specific
            ;;
        *)
            echo -e "${RED}❌ Modo desconhecido: $1${NC}"
            echo "Opções: recomendado, ultra, rapido, debug, last, specific"
            exit 1
            ;;
    esac
else
    # Menu interativo
    show_menu
    read -p "Escolha: " choice

    case "$choice" in
        1)
            run_recommended
            ;;
        2)
            run_ultra_verbose
            ;;
        3)
            run_quick
            ;;
        4)
            run_debug
            ;;
        5)
            run_last_failed
            ;;
        6)
            run_specific
            ;;
        0)
            echo -e "${YELLOW}Saindo...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção inválida!${NC}"
            exit 1
            ;;
    esac
fi

echo -e "\n${GREEN}✅ Testes finalizados!${NC}\n"
