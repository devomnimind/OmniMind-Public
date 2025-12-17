#!/bin/bash
################################################################################
# OmniMind Auto-Start Wrapper - Sem Prompts Sudo Redundantes
################################################################################
# Wrapper que:
# 1. Atualiza timestamp sudo (mantém credenciais ativas por 15 min)
# 2. Roda v2 com privilégios já adquiridos
# 3. Evita múltiplos prompts de senha
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
V2_SCRIPT="$SCRIPT_DIR/start_omnimind_system_wrapper_v2.sh"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 OmniMind Auto-Start (Sem Prompts Redundantes)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# 1️⃣ ATUALIZAR TIMESTAMP SUDO
echo -e "${YELLOW}[1/3] Atualizando credenciais sudo...${NC}"
if sudo -v 2>/dev/null; then
    echo -e "${GREEN}✅ Credenciais sudo atualizadas (válidas por 15 min)${NC}"
else
    echo -e "${RED}❌ Falha ao atualizar sudoers${NC}"
    exit 1
fi
echo ""

# 2️⃣ VALIDAR V2 SCRIPT
echo -e "${YELLOW}[2/3] Validando script v2...${NC}"
if [ ! -f "$V2_SCRIPT" ]; then
    echo -e "${RED}❌ Script não encontrado: $V2_SCRIPT${NC}"
    exit 1
fi

if [ ! -x "$V2_SCRIPT" ]; then
    echo -e "${YELLOW}⚠️  Script não é executável, tornando executável...${NC}"
    chmod +x "$V2_SCRIPT"
fi
echo -e "${GREEN}✅ Script v2 validado${NC}"
echo ""

# 3️⃣ EXECUTAR V2 COM PRIVILÉGIOS
echo -e "${YELLOW}[3/3] Iniciando sistema OmniMind com v2...${NC}"
echo -e "${BLUE}────────────────────────────────────────────────────────────${NC}"
echo ""

# Roda v2 sem sudo (já autenticado acima)
# Se precisar de sudo dentro do script, as credenciais já estão válidas
cd "$PROJECT_DIR"
sudo bash "$V2_SCRIPT"

EXIT_CODE=$?
echo ""
echo -e "${BLUE}────────────────────────────────────────────────────────────${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ OmniMind iniciado com sucesso!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
else
    echo -e "${RED}❌ OmniMind iniciou com erro (código: $EXIT_CODE)${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
fi

exit $EXIT_CODE
