#!/bin/bash
# ============================================================================
# SCRIPT DE SANITIZAÇÃO PARA VERSÃO PÚBLICA DO OMNIMIND
# ============================================================================
# Este script automatiza a remoção/substituição de dados sensíveis
# ATENÇÃO: Executar APENAS em branch separado (prepare-public-version)
# ============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 OmniMind - Sanitização para Versão Pública${NC}"
echo "============================================================================"
echo ""

# Verificação de branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "prepare-public-version" ]; then
    echo -e "${RED}❌ ERRO: Executar apenas em branch 'prepare-public-version'${NC}"
    echo "Branch atual: $CURRENT_BRANCH"
    echo ""
    echo "Criar branch:"
    echo "  git checkout -b prepare-public-version"
    exit 1
fi

echo -e "${GREEN}✅ Branch correto: $CURRENT_BRANCH${NC}"
echo ""

# Backup
BACKUP_DIR="backups/pre-sanitization-$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}📦 Criando backup em: $BACKUP_DIR${NC}"
mkdir -p "$BACKUP_DIR"
git archive HEAD | tar -x -C "$BACKUP_DIR"
echo -e "${GREEN}✅ Backup criado${NC}"
echo ""

# ============================================================================
# 1. SUBSTITUIR CAMINHOS ABSOLUTOS
# ============================================================================
echo -e "${BLUE}📁 Fase 1: Substituindo caminhos absolutos${NC}"
echo "============================================================================"

COUNT=0

# Substituir /home/fahbrain/projects/omnimind
echo "Buscando /home/fahbrain/projects/omnimind..."
FILES=$(grep -rl "/home/fahbrain/projects/omnimind" --include="*.py" --include="*.sh" \
    --exclude-dir=deploy --exclude-dir=k8s --exclude-dir=.git 2>/dev/null || true)

for file in $FILES; do
    echo "  Sanitizando: $file"
    sed -i 's|/home/fahbrain/projects/omnimind|\${PROJECT_ROOT:-$(pwd)}|g' "$file"
    ((COUNT++))
done

# Substituir /home/fahbrain/.cache/torch
echo "Buscando /home/fahbrain/.cache/torch..."
FILES=$(grep -rl "/home/fahbrain/.cache/torch" --include="*.py" --include="*.sh" \
    --exclude-dir=.git 2>/dev/null || true)

for file in $FILES; do
    echo "  Sanitizando: $file"
    sed -i 's|/home/fahbrain/.cache/torch|\${TORCH_HOME:-$HOME/.cache/torch}|g' "$file"
    ((COUNT++))
done

echo -e "${GREEN}✅ $COUNT arquivos sanitizados (caminhos)${NC}"
echo ""

# ============================================================================
# 2. REMOVER COMENTÁRIOS KALI
# ============================================================================
echo -e "${BLUE}🔧 Fase 2: Sanitizando comentários Kali${NC}"
echo "============================================================================"

# Substituir "Kali Linux" por "Linux"
FILES=$(grep -rl "Kali Linux" --include="*.sh" --exclude-dir=.git \
    scripts/canonical/system/ 2>/dev/null || true)

for file in $FILES; do
    echo "  Sanitizando: $file"
    sed -i 's/Kali Linux/Linux/g' "$file"
    sed -i 's/Kali\/Debian/Debian-based/g' "$file"
    sed -i 's/Kali Native/Linux/g' "$file"
done

echo -e "${GREEN}✅ Comentários Kali sanitizados${NC}"
echo ""

# ============================================================================
# 3. BUSCAR CREDENCIAIS REMANESCENTES (não automatizar remoção)
# ============================================================================
echo -e "${BLUE}🔍 Fase 3: Buscando credenciais hardcoded${NC}"
echo "============================================================================"

echo "Buscando passwords hardcoded..."
PASSWORDS=$(grep -rn "password.*=.*[\"']" --include="*.py" \
    --exclude-dir=.git --exclude-dir=tests 2>/dev/null | \
    grep -v "os.getenv" | grep -v "# " || true)

if [ -n "$PASSWORDS" ]; then
    echo -e "${RED}⚠️  ATENÇÃO: Credenciais encontradas!${NC}"
    echo "$PASSWORDS"
    echo ""
    echo -e "${YELLOW}AÇÃO MANUAL NECESSÁRIA:${NC}"
    echo "  1. Revisar arquivos acima"
    echo "  2. Substituir por: os.getenv('OMNIMIND_PASSWORD', '')"
    echo ""
else
    echo -e "${GREEN}✅ Nenhuma credencial hardcoded encontrada${NC}"
fi

echo "Buscando API keys hardcoded..."
API_KEYS=$(grep -rn "api_key.*=.*[\"']" --include="*.py" \
    --exclude-dir=.git --exclude-dir=tests 2>/dev/null | \
    grep -v "os.getenv" | grep -v "\.example" || true)

if [ -n "$API_KEYS" ]; then
    echo -e "${RED}⚠️  ATENÇÃO: API keys encontradas!${NC}"
    echo "$API_KEYS"
    echo ""
else
    echo -e "${GREEN}✅ Nenhuma API key hardcoded encontrada${NC}"
fi

echo ""

# ============================================================================
# 4. BUSCAR OUTROS DADOS SENSÍVEIS
# ============================================================================
echo -e "${BLUE}🔍 Fase 4: Buscando outros dados sensíveis${NC}"
echo "============================================================================"

echo "Buscando IPs privados..."
PRIVATE_IPS=$(grep -rn "192\.168\.\|10\.\|172\.\(1[6-9]\|2[0-9]\|3[01]\)\." \
    --include="*.py" --exclude-dir=.git --exclude-dir=tests 2>/dev/null || true)

if [ -n "$PRIVATE_IPS" ]; then
    echo -e "${YELLOW}⚠️  IPs privados encontrados (verificar se são apenas mocks):${NC}"
    echo "$PRIVATE_IPS" | head -5
    echo ""
else
    echo -e "${GREEN}✅ Nenhum IP privado encontrado${NC}"
fi

echo ""

# ============================================================================
# 5. RELATÓRIO FINAL
# ============================================================================
echo "============================================================================"
echo -e "${BLUE}📊 RELATÓRIO DE SANITIZAÇÃO${NC}"
echo "============================================================================"
echo ""
echo "✅ Caminhos absolutos: Sanitizados automaticamente"
echo "✅ Comentários Kali: Sanitizados automaticamente"
echo "⚠️  Credenciais: Verificação manual necessária"
echo "⚠️  IPs privados: Verificação manual necessária"
echo ""
echo -e "${YELLOW}PRÓXIMOS PASSOS:${NC}"
echo "1. Revisar mudanças: git diff"
echo "2. Corrigir manualmente credenciais (se encontradas)"
echo "3. Executar checklist: docs/CHECKLIST_SANITIZACAO.md"
echo "4. Commit: git add . && git commit -m 'security: Sanitize for public release'"
echo ""
echo -e "${GREEN}✅ Sanitização automática concluída!${NC}"
echo ""

