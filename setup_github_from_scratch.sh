#!/bin/bash

###############################################################################
# 🚀 setup_github_from_scratch.sh - Criar repos vazios + push único
###############################################################################
#
# Uso:
#   ./setup_github_from_scratch.sh
#
# O que faz:
#   1. Clone repo privado vazio do GitHub
#   2. Copia arquivos da máquina
#   3. Um commit único
#   4. Um push único
#   5. Ready para começar do zero
#
# PRÉ-REQUISITOS:
#   1. Criar repos VAZIOS no GitHub:
#      - https://github.com/devomnimind/omnimind-private (privado)
#      - https://github.com/devomnimind/OmniMind-Public (público)
#   2. GitHub CLI instalado (gh auth login)
#   3. SSH configurado para GitHub
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
PRIVATE_REPO="https://github.com/devomnimind/omnimind-private.git"
PUBLIC_REPO="https://github.com/devomnimind/OmniMind-Public.git"

###############################################################################
# ETAPA 1: Validar pré-requisitos
###############################################################################

log_info "Validando pré-requisitos..."

if [ ! -d "$SOURCE_DIR" ]; then
    log_error "Diretório origem não encontrado: $SOURCE_DIR"
    exit 1
fi

if ! command -v git &> /dev/null; then
    log_error "Git não instalado"
    exit 1
fi

log_success "Pré-requisitos OK"

###############################################################################
# ETAPA 2: Clone repo privado vazio
###############################################################################

log_info "Clonando repositório privado vazio..."

mkdir -p "$(dirname $TARGET_DIR)"
git clone "$PRIVATE_REPO" "$TARGET_DIR"
cd "$TARGET_DIR"

log_success "Repositório clonado"

###############################################################################
# ETAPA 3: Copiar arquivos da máquina
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

# .gitignore (seguro)
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
# ETAPA 4: Verificar estrutura
###############################################################################

log_info "Verificando estrutura..."

PYTHON_FILES=$(find src tests -name "*.py" 2>/dev/null | wc -l)
TEST_FILES=$(find tests -name "test_*.py" 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh . | cut -f1)

echo "  • Arquivos Python: $PYTHON_FILES"
echo "  • Testes: $TEST_FILES"
echo "  • Tamanho: $TOTAL_SIZE"
echo "  • Localização: $TARGET_DIR"

###############################################################################
# ETAPA 5: Um commit único
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

###############################################################################
# ETAPA 6: Um push único
###############################################################################

log_info "Fazendo push para GitHub..."

git branch -M main
git push -u origin main

log_success "Push concluído"

###############################################################################
# ETAPA 7: Resultado Final
###############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ REPOSITÓRIO CRIADO COM SUCESSO${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}📁 Localização Local:${NC}"
echo "   $TARGET_DIR"
echo ""

echo -e "${BLUE}🌐 Repositório GitHub:${NC}"
echo "   https://github.com/devomnimind/omnimind-private"
echo ""

echo -e "${BLUE}📊 Conteúdo:${NC}"
echo "   Arquivos Python: $PYTHON_FILES"
echo "   Testes: $TEST_FILES"
echo "   Tamanho: $TOTAL_SIZE"
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
echo "3️⃣  (Opcional) Criar fork público:"
echo "   https://github.com/devomnimind/omnimind-private > Fork"
echo "   Name: OmniMind-Public"
echo "   Visibility: Public"
echo ""

log_success "Tudo pronto! 🚀"
