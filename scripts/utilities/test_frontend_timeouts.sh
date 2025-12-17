#!/bin/bash

# Script para testar se o frontend consegue se conectar com os novos timeouts

echo "════════════════════════════════════════════════════════════════"
echo "🧪 TESTE DE TIMEOUTS DO FRONTEND"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para testar endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    local timeout=${3:-30}  # padrão 30 segundos

    echo -e "${BLUE}Testing:${NC} $description"
    echo "  Endpoint: http://127.0.0.1:8000$endpoint"
    echo "  Timeout: ${timeout}s"

    # Usar curl com timeout e retornar tempo de resposta
    local start_time=$(date +%s%3N)
    local response=$(curl -s -m $timeout -w "\n%{http_code}" "http://127.0.0.1:8000$endpoint" 2>&1)
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    local end_time=$(date +%s%3N)
    local duration=$((end_time - start_time))

    if [ "$http_code" = "000" ]; then
        echo -e "  Status: ${RED}❌ TIMEOUT (${timeout}s)${NC}"
        echo ""
    elif [ "$http_code" = "200" ] || [ "$http_code" = "307" ]; then
        echo -e "  Status: ${GREEN}✅ OK (HTTP $http_code)${NC}"
        echo "  Duration: ${duration}ms"
        echo ""
    else
        echo -e "  Status: ${YELLOW}⚠️  HTTP $http_code${NC}"
        echo "  Duration: ${duration}ms"
        echo ""
    fi
}

# Verificar se backend está rodando
echo -e "${BLUE}Verificando backend...${NC}"
if curl -s http://127.0.0.1:8000/health/ > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Backend está respondendo${NC}\n"
else
    echo -e "  ${RED}❌ Backend não está respondendo${NC}"
    exit 1
fi

# Testes com diferentes timeouts
echo "════════════════════════════════════════════════════════════════"
echo "📊 TESTES DE ENDPOINTS"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Health check (rápido, com trailing slash)
test_endpoint "/health/" "Health Check (COM trailing slash)" 5

# Endpoints críticos que eram timeout
test_endpoint "/daemon/status" "Daemon Status (LENTO - pode exceder 5s)" 45
test_endpoint "/daemon/agents" "Daemon Agents" 30
test_endpoint "/daemon/tasks" "Daemon Tasks" 30

# Endpoints com trailing slash
test_endpoint "/api/v1/autopoietic/consciousness/" "Autopoietic Consciousness" 30
test_endpoint "/api/v1/autopoietic/cycles/" "Autopoietic Cycles" 30

echo "════════════════════════════════════════════════════════════════"
echo "📈 RESUMO"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Timeouts configurados no frontend:"
echo "  • Normal endpoints: 120s (2 minutos)"
echo "  • Slow endpoints: 180s (3 minutos)"
echo "  • Critical endpoints: 300s (5 minutos)"
echo ""
echo "Polling intervals aumentados:"
echo "  • High priority: 45s (era 15s)"
echo "  • Medium priority: 60s (era 30s)"
echo "  • Low priority: 120s (era 60s)"
echo ""
echo "WebSocket retry aumentado:"
echo "  • Max attempts: 20 (era 5)"
echo "  • Max delay: 120s (era 10s)"
echo ""
echo "Para testar no browser:"
echo "  1. Abrir: http://localhost:3000"
echo "  2. Verificar console do navegador (F12)"
echo "  3. Procurar por 'Request timeout' - não deve mais aparecer"
echo "  4. Verificar se métricas começam a aparecer no dashboard"
echo ""
