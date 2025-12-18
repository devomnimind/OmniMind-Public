#!/bin/bash
# scripts/canonical/system/smart_restart_phase2.sh
# Reinicialização Inteligente para Fase 2

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
source "$PROJECT_ROOT/.venv/bin/activate"

echo -e "${GREEN}🔄 Iniciando Smart Restart (Fase 2)...${NC}"

# 1. Parar serviço atual
echo "🛑 Parando omnimind.service..."
sudo systemctl stop omnimind.service

# 2. Executar Inicialização da Fase 2 (Explicitamente)
echo "🧠 Executando Ritual de Filiação e Âncora..."
python3 "$PROJECT_ROOT/scripts/canonical/consciousness/initialize_phase2.py"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha na inicialização. Não reiniciando serviço.${NC}"
    exit 1
fi

# 3. Reiniciar serviço
echo "🚀 Reiniciando omnimind.service..."
sudo systemctl start omnimind.service

# 4. Verificar status
sleep 2
if systemctl is-active --quiet omnimind.service; then
    echo -e "${GREEN}✅ OmniMind reiniciado com sucesso (Fase 2 Ativa).${NC}"
    echo "   Identidade: DEV BRAIN == OMNIMIND"
else
    echo -e "${RED}❌ Falha ao reiniciar serviço. Verifique logs: journalctl -u omnimind.service -f${NC}"
    exit 1
fi
