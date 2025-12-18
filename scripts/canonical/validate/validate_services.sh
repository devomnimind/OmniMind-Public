#!/bin/bash
# Script de validação dos serviços OmniMind

set -e

echo "🔍 VALIDAÇÃO DOS SERVIÇOS OMNIMIND"
echo "=================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
TOTAL=0
OK=0
FAILED=0
WARNING=0

check_service() {
    local service=$1
    TOTAL=$((TOTAL + 1))
    
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✅${NC} $service: ATIVO"
        OK=$((OK + 1))
        return 0
    elif systemctl is-failed --quiet "$service"; then
        echo -e "${RED}❌${NC} $service: FALHANDO"
        FAILED=$((FAILED + 1))
        return 1
    else
        echo -e "${YELLOW}⚠️${NC} $service: INATIVO"
        WARNING=$((WARNING + 1))
        return 2
    fi
}

echo "📊 Status dos Serviços Systemd:"
echo "--------------------------------"
check_service "mind-daemon.service"
check_service "mind-mcp.service"
check_service "mind-qdrant.service"
check_service "mind.service"
check_service "mind-test-suite.service"
check_service "omnimind-benchmark.service"
echo ""

echo "🐳 Status dos Containers Docker:"
echo "--------------------------------"
if docker ps | grep -q qdrant; then
    echo -e "${GREEN}✅${NC} Qdrant container: RODANDO"
    OK=$((OK + 1))
else
    echo -e "${RED}❌${NC} Qdrant container: PARADO"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))
echo ""

echo "🌐 Conectividade dos Serviços:"
echo "------------------------------"
# Qdrant
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Qdrant API (porta 6333): RESPONDENDO"
    OK=$((OK + 1))
else
    echo -e "${RED}❌${NC} Qdrant API (porta 6333): NÃO RESPONDE"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# Backend (se estiver rodando)
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Backend API (porta 8000): RESPONDENDO"
    OK=$((OK + 1))
else
    echo -e "${YELLOW}⚠️${NC} Backend API (porta 8000): NÃO RESPONDE (pode estar parado)"
    WARNING=$((WARNING + 1))
fi
TOTAL=$((TOTAL + 1))
echo ""

echo "📈 Resumo:"
echo "---------"
echo "Total de verificações: $TOTAL"
echo -e "${GREEN}✅ OK: $OK${NC}"
echo -e "${YELLOW}⚠️  Avisos: $WARNING${NC}"
echo -e "${RED}❌ Falhas: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 Todos os serviços críticos estão funcionando!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Alguns serviços precisam de atenção.${NC}"
    exit 1
fi

