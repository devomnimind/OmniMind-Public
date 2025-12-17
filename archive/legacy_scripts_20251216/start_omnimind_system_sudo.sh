#!/bin/bash

# ============================================================================
# 🔐 OMNIMIND SYSTEM START WITH SUDO ELEVATION
# ============================================================================
# Este script é um wrapper que:
# 1. Chama o script oficial em scripts/canonical/system/start_omnimind_system.sh
# 2. Detecta se precisa sudo (para operações eBPF, iptables)
# 3. Executa com sudo se necessário
# 4. Passa todas as variáveis de ambiente necessárias
# 5. Não pede senha (usa sudoers preauth via secure_run.py)
# ============================================================================
# ATUALIZADO: 2025-12-07 - Usa script oficial em canonical/system/
# ============================================================================

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Script oficial (canonical)
OFFICIAL_SCRIPT="$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system.sh"

echo -e "${GREEN}🚀 Iniciando Sistema OmniMind (Wrapper com Elevação Sudo)...${NC}"

# Verificar se script oficial existe
if [ ! -f "$OFFICIAL_SCRIPT" ]; then
    echo -e "${RED}❌ Script oficial não encontrado: $OFFICIAL_SCRIPT${NC}"
    exit 1
fi

# 1. Garantir permissões no script oficial e dependências
chmod +x "$OFFICIAL_SCRIPT" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/canonical/system/secure_run.py" 2>/dev/null || true

# 2. Preparar variáveis de ambiente para passar ao sudo
# O script oficial já gerencia venv, GPU, autenticação, etc.
# Mas precisamos garantir que variáveis importantes sejam preservadas

# 3. Executar script oficial
# CRÍTICO: O script oficial calcula PROJECT_ROOT baseado em $0
# Quando chamado pelo wrapper, $0 aponta para canonical/system/, causando paths errados
# Solução: Executar a partir do PROJECT_ROOT e passar como variável de ambiente

echo "   → Executando script oficial: $OFFICIAL_SCRIPT"
echo "   → PROJECT_ROOT: $PROJECT_ROOT"

# Exportar PROJECT_ROOT para garantir que seja usado corretamente
export OMNIMIND_PROJECT_ROOT="$PROJECT_ROOT"

# Mudar para PROJECT_ROOT antes de executar (garante paths relativos corretos)
cd "$PROJECT_ROOT"

# Tentar executar com sudo -E primeiro (para garantir elevação completa)
# Isso é especialmente importante para iptables e eBPF durante testes
if sudo -n true 2>/dev/null; then
    # Sudo sem senha disponível - executar com elevação completa
    # IMPORTANTE: Executar com caminho absoluto e a partir do PROJECT_ROOT
    echo "   → Usando sudo -E para elevação completa..."
    sudo -E bash "$OFFICIAL_SCRIPT"
else
    # Sudo requer senha - tentar sem sudo primeiro
    # O script oficial gerencia suas próprias elevações quando necessário
    echo "   → Executando sem sudo (script oficial gerencia elevações)..."
    bash "$OFFICIAL_SCRIPT"
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Sistema OmniMind iniciado com sucesso${NC}"
else
    echo -e "${RED}❌ Falha ao iniciar sistema (exit code: $EXIT_CODE)${NC}"
    exit $EXIT_CODE
fi
