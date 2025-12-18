#!/bin/bash
# Script para validar que o frontend pode se autenticar automaticamente

set -e

echo "================================"
echo "🔐 Frontend Auto-Auth Validation"
echo "================================"
echo

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="${VITE_API_URL:-http://localhost:8000}"

echo "🔧 Configuração:"
echo "  API_URL: $API_URL"
echo

# 1. Verificar se backend está rodando
echo "1️⃣  Verificando se backend está rodando..."
if ! curl -s "$API_URL/health/" > /dev/null 2>&1; then
  echo -e "${RED}❌ Backend não está respondendo em $API_URL/health/${NC}"
  echo "   Inicie o backend com:"
  echo "   python -m uvicorn web.backend.main:app --port 8000"
  exit 1
fi
echo -e "${GREEN}✅ Backend respondendo${NC}"
echo

# 2. Testar endpoint público de credenciais
echo "2️⃣  Testando endpoint público /auth/credentials..."
RESPONSE=$(curl -s "$API_URL/auth/credentials")
echo "   Resposta: $RESPONSE"

USER=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('user', ''))" 2>/dev/null || echo "")
PASS=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('pass', ''))" 2>/dev/null || echo "")

if [ -z "$USER" ] || [ -z "$PASS" ]; then
  echo -e "${RED}❌ Não conseguiu extrair credenciais${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Credenciais carregadas${NC}"
echo "   User: ${USER:0:8}..."
echo "   Pass: ${PASS:0:8}..."
echo

# 3. Testar autenticação com credenciais obtidas
echo "3️⃣  Testando autenticação com credenciais obtidas..."
AUTH_RESPONSE=$(curl -s -u "$USER:$PASS" "$API_URL/daemon/status" | head -c 100)

if [ -z "$AUTH_RESPONSE" ]; then
  echo -e "${YELLOW}⚠️  Resposta vazia (backend pode estar carregando)${NC}"
else
  if echo "$AUTH_RESPONSE" | grep -q "error\|Error"; then
    echo -e "${RED}❌ Erro na autenticação: $AUTH_RESPONSE${NC}"
    exit 1
  fi
  echo -e "${GREEN}✅ Autenticação funcionou${NC}"
  echo "   Resposta: ${AUTH_RESPONSE:0:100}..."
fi
echo

# 4. Verificar arquivo de credenciais
echo "4️⃣  Verificando arquivo de credenciais (config/dashboard_auth.json)..."
if [ -f "config/dashboard_auth.json" ]; then
  echo -e "${GREEN}✅ Arquivo existe${NC}"
  cat config/dashboard_auth.json | head -3
else
  echo -e "${YELLOW}⚠️  Arquivo não encontrado (será criado automaticamente)${NC}"
fi
echo

# 5. Resumo
echo "================================"
echo -e "${GREEN}✅ VALIDAÇÃO COMPLETA${NC}"
echo "================================"
echo
echo "Frontend está pronto para:"
echo "  1️⃣  Fazer fetch em /auth/credentials"
echo "  2️⃣  Extrair {user, pass}"
echo "  3️⃣  Configurar apiService.setCredentials()"
echo "  4️⃣  Chamar login(user, pass)"
echo "  5️⃣  Dashboard renderiza com autenticação ✅"
echo
echo "Próximos passos:"
echo "  cd web/frontend"
echo "  npm run dev"
echo "  Abrir http://localhost:5173"
echo "  Dashboard deve carregar automaticamente!"
echo
