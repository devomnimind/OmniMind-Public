#!/bin/bash

# 🧪 Script para testar todos os endpoints sincronizados
# Frontend ↔ Backend: Verificar que todas as chamadas funcionam

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 TESTE DE SINCRONIZAÇÃO FRONTEND ↔ BACKEND${NC}"
echo "=================================================="
echo ""

# 1. Ler credenciais
AUTH_FILE="config/dashboard_auth.json"
if [ -f "$AUTH_FILE" ]; then
    USER=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('user', ''))" 2>/dev/null)
    PASS=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('pass', ''))" 2>/dev/null)
    echo -e "${GREEN}✓ Credenciais lidas de $AUTH_FILE${NC}"
    echo "  User: $USER"
    echo "  Pass: ${PASS:0:8}...${PASS: -4}"
else
    echo -e "${RED}✗ Arquivo $AUTH_FILE não encontrado${NC}"
    echo "  Use: ./scripts/canonical/system/start_omnimind_system.sh"
    exit 1
fi

API_URL="http://localhost:8000"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Função para testar um endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local description=$4

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -ne "${YELLOW}[${TOTAL_TESTS}]${NC} Testando: $name ... "

    if [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -u "$USER:$PASS" -X POST "$API_URL$endpoint" 2>/dev/null || echo "")
    else
        response=$(curl -s -w "\n%{http_code}" -u "$USER:$PASS" "$API_URL$endpoint" 2>/dev/null || echo "")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [[ "$http_code" == "200" ]] || [[ "$http_code" == "201" ]] || [[ "$http_code" == "202" ]]; then
        echo -e "${GREEN}✓ (HTTP $http_code)${NC}"
        echo "  $description"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    elif [[ "$http_code" == "401" ]] || [[ "$http_code" == "403" ]]; then
        echo -e "${RED}✗ (HTTP $http_code - Autenticação)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    elif [[ "$http_code" == "404" ]]; then
        echo -e "${RED}✗ (HTTP $http_code - NÃO ENCONTRADO)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    elif [[ "$http_code" == "503" ]]; then
        echo -e "${YELLOW}⚠ (HTTP $http_code - Serviço indisponível)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    else
        echo -e "${RED}✗ (HTTP $http_code - Erro desconhecido)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo -e "${BLUE}🔐 AUTENTICAÇÃO${NC}"
echo "---"
test_endpoint "Health Check" "GET" "/status" "Status geral do sistema"
echo ""

echo -e "${BLUE}🛡️  SEGURANÇA${NC}"
echo "---"
test_endpoint "Security Overview" "GET" "/api/security" "Visão geral de segurança"
test_endpoint "Security Status" "GET" "/api/security/status" "Status detalhado de segurança"
test_endpoint "Security Events" "GET" "/api/security/events" "Lista de eventos de segurança"
test_endpoint "Security Events Stats" "GET" "/api/security/events/stats" "Estatísticas de eventos"
test_endpoint "Security Analytics" "GET" "/api/security/analytics" "Análises de segurança"
test_endpoint "Security Dashboard" "GET" "/api/security/monitoring/dashboard" "Dashboard de monitoramento"
test_endpoint "Security Correlated Events" "GET" "/api/security/events/correlated" "Eventos correlacionados"
test_endpoint "Security Automated Response" "GET" "/api/security/response/automated" "Resposta automatizada de segurança"
echo ""

echo -e "${BLUE}🧠 METACOGNIÇÃO${NC}"
echo "---"
test_endpoint "Metacognition Overview" "GET" "/api/metacognition" "Visão geral de metacognição"
test_endpoint "Metacognition Insights" "GET" "/api/metacognition/insights" "Insights de metacognição"
test_endpoint "Metacognition Suggestions" "GET" "/api/metacognition/suggestions" "Sugestões de metacognição"
test_endpoint "Metacognition Stats" "GET" "/api/metacognition/stats" "Estatísticas de metacognição"
test_endpoint "Metacognition Last Analysis" "GET" "/api/metacognition/last-analysis" "Última análise"
test_endpoint "Metacognition Goals" "GET" "/api/metacognition/goals/generate" "Geração de objetivos"
test_endpoint "Metacognition Homeostasis" "GET" "/api/metacognition/homeostasis/status" "Status de homeostase"
echo ""

echo -e "${BLUE}🔄 AUTOPOIÉTICO (FASE 22)${NC}"
echo "---"
test_endpoint "Autopoietic Status" "GET" "/api/v1/autopoietic/status" "Status autopoiético"
test_endpoint "Autopoietic Cycles" "GET" "/api/v1/autopoietic/cycles" "Ciclos autopoiéticos"
test_endpoint "Autopoietic Cycle Stats" "GET" "/api/v1/autopoietic/cycles/stats" "Estatísticas de ciclos"
test_endpoint "Autopoietic Components" "GET" "/api/v1/autopoietic/components" "Componentes sintetizados"
test_endpoint "Autopoietic Health" "GET" "/api/v1/autopoietic/health" "Saúde autopoiética"
test_endpoint "Consciousness Metrics (SEM raw)" "GET" "/api/v1/autopoietic/consciousness/metrics" "Métricas de consciência (Φ, Anxiety, Flow, Entropy, ICI, PRS)"
test_endpoint "Consciousness Metrics (COM raw)" "GET" "/api/v1/autopoietic/consciousness/metrics?include_raw=true" "Métricas + dados brutos (25 predições, módulos, etc)"
echo ""

echo -e "${BLUE}🤖 DAEMON & TAREFAS${NC}"
echo "---"
test_endpoint "Daemon Status" "GET" "/daemon/status" "Status do daemon"
test_endpoint "Daemon Tasks" "GET" "/daemon/tasks" "Tarefas do daemon"
test_endpoint "Daemon Agents" "GET" "/daemon/agents" "Agentes do daemon"
test_endpoint "Daemon Start" "POST" "/daemon/start" "Iniciar daemon"
echo ""

echo -e "${BLUE}🌐 GERAIS${NC}"
echo "---"
test_endpoint "Root" "GET" "/" "Raiz do servidor"
test_endpoint "API v1 Status" "GET" "/api/v1/status" "Status API v1"
test_endpoint "Snapshot" "GET" "/snapshot" "Snapshot do sistema"
test_endpoint "Plan" "GET" "/plan" "Plano do sistema"
test_endpoint "Metrics" "GET" "/metrics" "Métricas em tempo real"
test_endpoint "Observability" "GET" "/observability" "Observabilidade do sistema"
test_endpoint "Audit Stats" "GET" "/audit/stats" "Estatísticas de auditoria"
test_endpoint "API Metrics (público)" "GET" "/api/metrics" "Métricas API (público, sem auth)"
test_endpoint "WebSocket Stats" "GET" "/ws/stats" "Estatísticas de WebSocket"
echo ""

# Resumo
echo "=================================================="
echo -e "${BLUE}📊 RESUMO DOS TESTES${NC}"
echo "=================================================="
echo -e "Total:  ${BLUE}$TOTAL_TESTS${NC} testes"
echo -e "Passou: ${GREEN}$PASSED_TESTS${NC} testes"
echo -e "Falhou: ${RED}$FAILED_TESTS${NC} testes"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ SINCRONIZAÇÃO PERFEITA!${NC}"
    echo "   Frontend e Backend estão em sintonia"
    exit 0
else
    echo -e "${RED}❌ FALHAS DETECTADAS!${NC}"
    echo "   Verifique os endpoints com erro acima"
    echo "   Dica: Verifique logs/backend_8000.log"
    exit 1
fi
