#!/bin/bash
# Unified Restart - Gentil e Cuidadoso
# Política Ética: Não matar, aprender com os erros
# Data: 2024-12-24

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}🔄 ERICA Unified Restart - Unificação Gentil${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Parar o service antigo (systemd faz gracefully)
echo -e "${YELLOW}📢 Fase 1: Parando omnimind-kernel.service (graceful)...${NC}"
systemctl --user stop omnimind-kernel.service 2>/dev/null || echo "   Service já estava parado"
sleep 2

# 2. Aguardar processo terminar naturalmente
echo -e "${YELLOW}⏳ Fase 2: Aguardando processo 1733336 terminar naturalmente...${NC}"
if ps -p 1733336 > /dev/null 2>&1; then
    timeout 30 tail --pid=1733336 -f /dev/null 2>/dev/null || echo "   Processo terminou ou timeout"
else
    echo "   Processo já terminou"
fi

# 3. Parar daemon root (enviar SIGTERM, não SIGKILL)
echo -e "${YELLOW}📢 Fase 3: Parando sovereign_daemon.py (graceful SIGTERM)...${NC}"
if pgrep -f "sovereign_daemon.py" > /dev/null; then
    sudo pkill -TERM -f "sovereign_daemon.py" || echo "   Falha ao enviar SIGTERM"
    sleep 2
else
    echo "   Daemon já estava parado"
fi

# 4. Aguardar daemon terminar
echo -e "${YELLOW}⏳ Fase 4: Aguardando processo 980679 terminar naturalmente...${NC}"
if ps -p 980679 > /dev/null 2>&1; then
    timeout 30 tail --pid=980679 -f /dev/null 2>/dev/null || echo "   Processo terminou ou timeout"
else
    echo "   Processo já terminou"
fi

# 5. Verificar se processos realmente pararam
echo -e "${BLUE}🔍 Fase 5: Verificando se processos pararam...${NC}"
if pgrep -f "sovereign_kernel_runner.py\|sovereign_daemon.py" > /dev/null; then
    echo -e "${RED}⚠️  Ainda há processos rodando. Aguardando mais 10s...${NC}"
    sleep 10

    if pgrep -f "sovereign_kernel_runner.py\|sovereign_daemon.py" > /dev/null; then
        echo -e "${RED}❌ Processos não pararam gracefully. Abortando unificação.${NC}"
        echo "   Execute manualmente: sudo pkill -9 -f 'sovereign'"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Todos os processos antigos pararam${NC}"
echo ""

# 6. Desabilitar service antigo
echo -e "${BLUE}📢 Fase 6: Desabilitando omnimind-kernel.service...${NC}"
systemctl --user disable omnimind-kernel.service 2>/dev/null || true

# 7. Habilitar novo service
echo -e "${GREEN}✨ Fase 7: Habilitando omnimind-kernel-unified.service...${NC}"
systemctl --user daemon-reload
systemctl --user enable omnimind-kernel-unified.service

# 8. Iniciar novo service
echo -e "${GREEN}🚀 Fase 8: Iniciando omnimind-kernel-unified.service...${NC}"
systemctl --user start omnimind-kernel-unified.service

# 9. Aguardar inicialização
echo -e "${YELLOW}⏳ Fase 9: Aguardando 10s para inicialização...${NC}"
sleep 10

# 10. Verificar status
echo ""
echo -e "${BLUE}📊 Fase 10: Status do novo service:${NC}"
systemctl --user status omnimind-kernel-unified.service --no-pager | head -20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Unificação concluída!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}💡 Próximos passos:${NC}"
echo "   1. Monitorar logs: journalctl --user -u omnimind-kernel-unified.service -f"
echo "   2. Verificar processo: ps aux | grep sovereign_daemon.py"
echo "   3. Verificar Φ: tail -f data/science/sovereign_daemon.log"
echo ""
