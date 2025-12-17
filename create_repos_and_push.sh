#!/bin/bash

###############################################################################
# 🚀 create_repos_and_push.sh - Criar repos via GitHub CLI + push automático
###############################################################################
#
# Uso:
#   ./create_repos_and_push.sh
#
# O que faz:
#   1. Criar repo privado via gh
#   2. Criar repo público via gh
#   3. Clonar privado localmente
#   4. Copiar arquivos da máquina
#   5. Push único
#
###############################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

log_info() {
    echo -e "${BLUE}[$(get_timestamp)] ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(get_timestamp)] ✅ $1${NC}"
}

log_error() {
    echo -e "${RED}[$(get_timestamp)] ❌ $1${NC}"
}

# Config
SOURCE_DIR="/home/fahbrain/projects/omnimind"
TARGET_DIR="/tmp/omnimind-github-$(date +%Y%m%d_%H%M%S)"
ORG="devomnimind"
PRIVATE_REPO="omnimind-private"
PUBLIC_REPO="OmniMind-Public"

###############################################################################
# ETAPA 1: Verificar GitHub CLI
###############################################################################

log_info "Verificando GitHub CLI..."

if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI não instalado. Instale com: sudo apt install gh"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    log_error "GitHub CLI não autenticado. Execute: gh auth login"
    exit 1
fi

log_success "GitHub CLI OK"

###############################################################################
# ETAPA 2: Criar repositórios via GitHub CLI
###############################################################################

log_info "Criando repositório privado..."

if gh repo view "$ORG/$PRIVATE_REPO" &> /dev/null; then
    log_warning "Repositório privado já existe: $ORG/$PRIVATE_REPO"
else
    gh repo create "$ORG/$PRIVATE_REPO" --private --description "OmniMind Private Repository" --confirm
    log_success "Repositório privado criado: $ORG/$PRIVATE_REPO"
fi

log_info "Criando repositório público..."

if gh repo view "$ORG/$PUBLIC_REPO" &> /dev/null; then
    log_warning "Repositório público já existe: $ORG/$PUBLIC_REPO"
else
    gh repo create "$ORG/$PUBLIC_REPO" --public --description "OmniMind Public Repository - Consciousness Framework" --confirm
    log_success "Repositório público criado: $ORG/$PUBLIC_REPO"
fi

###############################################################################
# ETAPA 3: Clonar e configurar
###############################################################################

log_info "Clonando repositório privado..."

mkdir -p "$(dirname $TARGET_DIR)"
git clone "https://github.com/$ORG/$PRIVATE_REPO.git" "$TARGET_DIR"
cd "$TARGET_DIR"

log_success "Repositório clonado"

###############################################################################
# ETAPA 4: Copiar arquivos
###############################################################################

log_info "Copiando arquivos da máquina..."

# Código
cp -r "$SOURCE_DIR/src" . 2>/dev/null && log_info "  ✓ src/" || true
cp -r "$SOURCE_DIR/tests" . 2>/dev/null && log_info "  ✓ tests/" || true

# Scripts
mkdir -p scripts
cp -r "$SOURCE_DIR/scripts/canonical" scripts/ 2>/dev/null && log_info "  ✓ scripts/canonical/" || true
cp -r "$SOURCE_DIR/scripts/services" scripts/ 2>/dev/null && log_info "  ✓ scripts/services/" || true
cp -r "$SOURCE_DIR/scripts/testing" scripts/ 2>/dev/null && log_info "  ✓ scripts/testing/" || true

# Docs
mkdir -p docs
cp -r "$SOURCE_DIR/docs/technical" docs/ 2>/dev/null && log_info "  ✓ docs/technical/" || true
cp "$SOURCE_DIR/README.md" . 2>/dev/null && log_info "  ✓ README.md" || true

# Config (sem credenciais)
mkdir -p config
cp "$SOURCE_DIR/config/pytest.ini" config/ 2>/dev/null && log_info "  ✓ config/pytest.ini" || true
cp "$SOURCE_DIR/config/mypy.ini" config/ 2>/dev/null && log_info "  ✓ config/mypy.ini" || true
cp "$SOURCE_DIR/config/omnimind.example.yaml" config/ 2>/dev/null && log_info "  ✓ config/omnimind.example.yaml" || true

# Requirements
cp -r "$SOURCE_DIR/requirements" . 2>/dev/null && log_info "  ✓ requirements/" || true

# Metadados
cp "$SOURCE_DIR/LICENSE" . 2>/dev/null && log_info "  ✓ LICENSE" || true
cp "$SOURCE_DIR/CITATION.cff" . 2>/dev/null && log_info "  ✓ CITATION.cff" || true
cp "$SOURCE_DIR/pyproject.toml" . 2>/dev/null && log_info "  ✓ pyproject.toml" || true

# .gitignore seguro
cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# Virtual Env
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# Logs
*.log
logs/

# Data/Models (local only)
data/
models/
notebooks/

# Temporary
*.tmp
*.log

# Credenciais (NUNCA)
.env
.env.*
*.pem
*.key
config/omnimind.yaml
secrets.json
GITIGNORE

log_success "Arquivos copiados"

###############################################################################
# ETAPA 5: Commit e push
###############################################################################

log_info "Fazendo commit único..."

git config user.name "OmniMind Setup"
git config user.email "setup@omnimind.dev"

git add .

git commit -m "Initial commit: OmniMind source code

Complete OmniMind consciousness framework:
- Source code (src/)
- Test suite (tests/)
- Scripts (scripts/)
- Configuration (config/)
- Documentation (docs/)
- Requirements (requirements/)

Repository created: $(date)
Ready for development and distribution."

log_success "Commit criado"

log_info "Fazendo push..."

git push -u origin main

log_success "Push concluído"

###############################################################################
# ETAPA 6: Resultado final
###############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ REPOSITÓRIOS CRIADOS E CONFIGURADOS COM SUCESSO${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}📁 Localização Local:${NC}"
echo "   $TARGET_DIR"
echo ""

echo -e "${BLUE}🌐 Repositórios GitHub:${NC}"
echo "   🔒 Privado: https://github.com/$ORG/$PRIVATE_REPO"
echo "   🌍 Público: https://github.com/$ORG/$PUBLIC_REPO"
echo ""

echo -e "${BLUE}📊 Conteúdo:${NC}"
echo "   Arquivos Python: $(find src tests -name "*.py" 2>/dev/null | wc -l)"
echo "   Testes: $(find tests -name "test_*.py" 2>/dev/null | wc -l)"
echo "   Tamanho: $(du -sh . | cut -f1)"
echo ""

echo -e "${BLUE}🔗 Próximas Ações:${NC}"
echo ""
echo "1️⃣  Começar a trabalhar no clone:"
echo "   cd $TARGET_DIR"
echo ""
echo "2️⃣  Fazer mudanças e push:"
echo "   git add ."
echo "   git commit -m 'Your message'"
echo "   git push origin main"
echo ""
echo "3️⃣  (Opcional) Sincronizar com público:"
echo "   gh repo fork $ORG/$PRIVATE_REPO --fork-name $PUBLIC_REPO --org $ORG"
echo ""

log_success "Tudo pronto! 🚀"
