#!/bin/bash
################################################################################
# OmniMind Status Quick Check - Sem Travar
################################################################################

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🧠 OmniMind Status Check${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Verificar cada porta com timeout de 1s
echo -e "${YELLOW}Serviços:${NC}"

# Backend Primary
echo -n "  Backend Primary (8000):        "
if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/8000" 2>/dev/null; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${YELLOW}⏳ Carregando...${NC}"
fi

# Backend Secondary
echo -n "  Backend Secondary (8080):      "
if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/8080" 2>/dev/null; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${YELLOW}⏳ Carregando...${NC}"
fi

# Backend Fallback
echo -n "  Backend Fallback (3001):       "
if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/3001" 2>/dev/null; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${YELLOW}⏳ Carregando...${NC}"
fi

# Frontend
echo -n "  Frontend (3000):               "
if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/3000" 2>/dev/null; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${YELLOW}⏳ Carregando...${NC}"
fi

# Redis
echo -n "  Redis (6379):                  "
if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/6379" 2>/dev/null; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${RED}❌ OFFLINE${NC}"
fi

echo ""
echo -e "${YELLOW}Processos Python:${NC}"
ps aux | grep -E "python.*uvicorn|python.*src.main|python.*daemon" | grep -v grep | wc -l | xargs echo "  Total:"

echo ""
echo -e "${YELLOW}Log Recente:${NC}"
tail -3 /home/fahbrain/projects/omnimind/logs/startup_production.log 2>/dev/null || echo "  (log ainda não disponível)"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Sistema inicializando (pode levar 2-5 min para carregar modelos)${NC}"
echo -e "${GREEN}   Monitorar: tail -f logs/startup_production.log${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
