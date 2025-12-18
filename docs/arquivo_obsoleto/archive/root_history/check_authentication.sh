#!/bin/bash

# Script para verificar e diagnosticar o sistema de autenticação
# Mostra credenciais, testa endpoints públicos vs privados

echo "════════════════════════════════════════════════════════════════"
echo "🔐 DIAGNÓSTICO DE AUTENTICAÇÃO - OmniMind"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Obter credenciais atuais
echo -e "${BLUE}1️⃣  CREDENCIAIS ATUAIS${NC}"
echo ""

AUTH_FILE="config/dashboard_auth.json"

if [ ! -f "$AUTH_FILE" ]; then
    echo -e "${RED}❌ Arquivo não encontrado: $AUTH_FILE${NC}"
    echo "   Backend deve gerar automaticamente na primeira execução"
    echo ""
else
    echo -e "${GREEN}✅ Arquivo encontrado: $AUTH_FILE${NC}"

    # Extrair credenciais
    CREDS=$(python3 -c "import json; f=open('$AUTH_FILE'); d=json.load(f); print(f\"{d['user']}:{d['pass']}\")" 2>&1)

    if [ $? -eq 0 ]; then
        USER=$(echo "$CREDS" | cut -d: -f1)
        PASS=$(echo "$CREDS" | cut -d: -f2)

        echo "   Usuário: $USER"
        echo "   Senha: $PASS"
        echo "   Base64: $(echo -n "$CREDS" | base64)"
        echo ""
    else
        echo -e "${RED}❌ Erro ao ler credenciais${NC}"
        echo ""
    fi
fi

# 2. Obter credenciais via API
echo -e "${BLUE}2️⃣  CREDENCIAIS VIA API${NC}"
echo ""

CREDS_API=$(curl -s http://127.0.0.1:8000/auth/credentials)
echo "Endpoint: GET /auth/credentials"
echo "Response:"
echo "$CREDS_API" | python3 -m json.tool 2>/dev/null || echo "$CREDS_API"
echo ""

# 3. Testar endpoints PÚBLICOS (sem auth)
echo -e "${BLUE}3️⃣  ENDPOINTS PÚBLICOS (SEM AUTENTICAÇÃO)${NC}"
echo ""

test_public() {
    local endpoint=$1
    local name=$2

    echo "Testing: $name"
    echo "  Endpoint: GET $endpoint"

    local status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000$endpoint)

    case $status in
        200) echo -e "  Status: ${GREEN}✅ 200 OK${NC}" ;;
        307) echo -e "  Status: ${YELLOW}⚠️  307 Redirect${NC} (Likely trailing slash issue)" ;;
        404) echo -e "  Status: ${RED}❌ 404 Not Found${NC}" ;;
        401) echo -e "  Status: ${RED}❌ 401 Unauthorized (Needs Auth!)${NC}" ;;
        *) echo -e "  Status: ${RED}❌ HTTP $status${NC}" ;;
    esac
    echo ""
}

test_public "/health/" "Health Check"
test_public "/daemon/status" "Daemon Status"
test_public "/api/metacognition/insights" "Metacognition Insights"
test_public "/api/tribunal/activity" "Tribunal Activity"

# 4. Testar endpoints PRIVADOS (com auth)
echo -e "${BLUE}4️⃣  ENDPOINTS PRIVADOS (COM AUTENTICAÇÃO)${NC}"
echo ""

test_private() {
    local endpoint=$1
    local name=$2
    local auth=$3

    echo "Testing: $name"
    echo "  Endpoint: GET $endpoint"
    echo "  Auth: Basic $auth"

    local status=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Basic $auth" \
        http://127.0.0.1:8000$endpoint)

    case $status in
        200) echo -e "  Status: ${GREEN}✅ 200 OK${NC}" ;;
        307) echo -e "  Status: ${YELLOW}⚠️  307 Redirect${NC}" ;;
        404) echo -e "  Status: ${RED}❌ 404 Not Found${NC}" ;;
        401) echo -e "  Status: ${RED}❌ 401 Unauthorized (Wrong Credentials)${NC}" ;;
        *) echo -e "  Status: ${RED}❌ HTTP $status${NC}" ;;
    esac
    echo ""
}

# Usar credenciais do arquivo
if [ ! -z "$CREDS" ]; then
    B64_CREDS=$(echo -n "$CREDS" | base64)

    test_private "/api/v1/autopoietic/consciousness/" "Autopoietic Consciousness" "$B64_CREDS"
    test_private "/api/tribunal/activity" "Tribunal Activity" "$B64_CREDS"
else
    echo -e "${RED}⚠️  Não conseguiu extrair credenciais, pulando testes privados${NC}"
    echo ""
fi

# 5. Resumo e recomendações
echo "════════════════════════════════════════════════════════════════"
echo "📋 RESUMO E RECOMENDAÇÕES"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "🔹 Endpoints PÚBLICOS (SEM autenticação necessária):"
echo "   ✅ /health/*"
echo "   ✅ /daemon/*"
echo "   ✅ /tasks/*"
echo "   ✅ /agents/*"
echo "   ✅ /api/metacognition/*"
echo "   ✅ /api/security/*"
echo "   ✅ /ws (WebSocket)"
echo ""

echo "🔹 Endpoints PRIVADOS (REQUEREM autenticação):"
echo "   🔐 /api/v1/autopoietic/* (HTTP Basic Auth)"
echo "   🔐 /api/tribunal/* (HTTP Basic Auth)"
echo ""

echo "🔹 Frontend Setup:"
echo "   1. Chamar GET /auth/credentials para obter user:pass"
echo "   2. Salvar em localStorage:"
echo "      localStorage.setItem('omnimind_user', user)"
echo "      localStorage.setItem('omnimind_pass', pass)"
echo "   3. Usar nas requisições com Authorization header:"
echo "      Authorization: Basic <base64(user:pass)>"
echo ""

echo "🔹 Para testar via curl:"
echo "   # Sem autenticação (público)"
echo "   curl http://127.0.0.1:8000/daemon/status"
echo ""
echo "   # Com autenticação (privado)"
echo "   curl -u username:password http://127.0.0.1:8000/api/v1/autopoietic/consciousness/"
echo ""

echo "🔹 Renovar credenciais (local dev):"
echo "   1. Editar $AUTH_FILE"
echo "   2. chmod 600 $AUTH_FILE"
echo "   3. Reiniciar backend"
echo ""
