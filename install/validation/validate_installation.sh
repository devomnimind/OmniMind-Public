#!/bin/bash
# Script de validação completa da instalação OmniMind
set -euo pipefail

echo "🔍 Iniciando validação da instalação OmniMind..."
echo "==============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funções de validação
check_service() {
    local service=$1
    echo -n "Verificando $service... "
    if sudo systemctl is-active --quiet "$service" 2>/dev/null || sudo systemctl show "$service" --property=ActiveState --value | grep -q -E "(activating|active)"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHA${NC}"
        return 1
    fi
}

check_endpoint() {
    local url=$1
    local expected=$2
    echo -n "Testando $url... "
    if curl -s --max-time 5 "$url" | grep -q "$expected"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHA${NC}"
        return 1
    fi
}

check_port() {
    local port=$1
    echo -n "Verificando porta $port... "
    if sudo netstat -tlnp | grep -q ":$port "; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHA${NC}"
        return 1
    fi
}

# Validação dos serviços
echo "📦 Verificando serviços systemd..."
FAILED=0

SERVICES=(
    "omnimind-qdrant:Qdrant Vector Database"
    "omnimind-backend:OmniMind Backend API"
    "omnimind-frontend:OmniMind Frontend Dashboard"
    "omnimind-mcp:OmniMind MCP Servers"
)

for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service desc <<< "$service_info"
    if ! check_service "$service"; then
        FAILED=1
    fi
done

# Validação das portas
echo ""
echo "🔌 Verificando portas..."
PORTS=(6333 8000 3000)

for port in "${PORTS[@]}"; do
    if ! check_port "$port"; then
        FAILED=1
    fi
done

# Validação dos endpoints
echo ""
echo "🌐 Testando endpoints..."

ENDPOINTS=(
    "http://localhost:6333/collections|result"
    "http://localhost:8000/health|status"
    "http://localhost:3000|<!doctype"
)

for endpoint_info in "${ENDPOINTS[@]}"; do
    IFS='|' read -r url expected <<< "$endpoint_info"
    if ! check_endpoint "$url" "$expected"; then
        FAILED=1
    fi
done

# Validação dos containers Docker
echo ""
echo "🐳 Verificando containers Docker..."

CONTAINERS=(
    "deploy-qdrant-1:qdrant"
    "deploy-backend-1:deploy-backend"
    "deploy-frontend-1:deploy-frontend"
)

for container_info in "${CONTAINERS[@]}"; do
    IFS=':' read -r container expected <<< "$container_info"
    echo -n "Verificando container $container... "
    if docker ps --format "table {{.Names}}\t{{.Image}}" | grep -q "$container" && docker ps --format "table {{.Names}}\t{{.Image}}" | grep "$container" | grep -q "$expected"; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FALHA${NC}"
        FAILED=1
    fi
done

# Resultado final
echo ""
echo "==============================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 VALIDAÇÃO COMPLETA - Todos os testes passaram!${NC}"
    echo "✅ Instalação OmniMind validada com sucesso"
    exit 0
else
    echo -e "${RED}❌ VALIDAÇÃO FALHADA - Alguns testes falharam${NC}"
    echo "🔧 Verifique os logs acima e consulte docs/TROUBLESHOOTING.md"
    exit 1
fi