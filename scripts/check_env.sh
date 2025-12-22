#!/bin/bash
# ============================================================================
# 🛡️ OMNIMIND CANONICAL ENV CHECK
# ============================================================================
# Este script garante a integridade do ambiente de execução.
# Deve ser chamado por todos os serviços e scripts de produção.

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[*] Validando Ambiente OmniMind...${NC}"

# 1. Determinar RAIZ DO PROJETO
if [ -z "${OMNIMIND_PROJECT_ROOT:-}" ]; then
    # Tentar inferir se estiver em scripts/
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ "$SCRIPT_DIR" == *"/scripts" ]]; then
        export OMNIMIND_PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    else
        export OMNIMIND_PROJECT_ROOT="/home/fahbrain/projects/omnimind"
    fi
fi

if [ ! -d "$OMNIMIND_PROJECT_ROOT" ]; then
    echo -e "${RED}[!] ERRO: OMNIMIND_PROJECT_ROOT não encontrado em $OMNIMIND_PROJECT_ROOT${NC}"
    exit 1
fi

# 2. Carregar .env se existir
if [ -f "$OMNIMIND_PROJECT_ROOT/.env" ]; then
    # Usar export para garantir que as variáveis se propaguem
    set -a
    source "$OMNIMIND_PROJECT_ROOT/.env"
    set +a
    echo -e "${GREEN}[✓] .env carregado.${NC}"
else
    echo -e "${YELLOW}[!] AVISO: .env não encontrado.${NC}"
fi

# 3. Validar Python Venv
python_path=$(which python3)
if [[ "$python_path" != *"$OMNIMIND_PROJECT_ROOT/.venv"* ]]; then
    if [ -f "$OMNIMIND_PROJECT_ROOT/.venv/bin/activate" ]; then
        source "$OMNIMIND_PROJECT_ROOT/.venv/bin/activate"
        echo -e "${GREEN}[✓] Venv ativado explicitamente.${NC}"
    else
        echo -e "${RED}[!] ERRO: Virtualenv não encontrado ou não ativado corretamente.${NC}"
        exit 1
    fi
fi

# 4. Validar PYTHONPATH
if [[ "$PYTHONPATH" != *"$OMNIMIND_PROJECT_ROOT"* ]]; then
    export PYTHONPATH="$OMNIMIND_PROJECT_ROOT:$OMNIMIND_PROJECT_ROOT/src"
    echo -e "${YELLOW}[!] PYTHONPATH ajustado.${NC}"
fi

# 5. Exportar variáveis críticas se faltarem
export OMNIMIND_ROOT="$OMNIMIND_PROJECT_ROOT"
export PROJECT_ROOT="$OMNIMIND_PROJECT_ROOT"

echo -e "${GREEN}[✓] Ambiente Estável: $OMNIMIND_PROJECT_ROOT${NC}"
echo -e "    Python: $(which python3)"
echo -e "    Venv: ${VIRTUAL_ENV:-N/A}"
