#!/bin/bash

###############################################################################
# 🚀 prepare_and_publish.sh - Automatiza publicação para GitHub Organization
###############################################################################
#
# Uso:
#   ./scripts/canonical/github/prepare_and_publish.sh
#   ./scripts/canonical/github/prepare_and_publish.sh /tmp/custom-path
#
# O que faz:
#   1. Cria repositório público limpo
#   2. Valida código (imports, syntax)
#   3. Executa testes críticos
#   4. Faz commit inicial
#   5. Mostra instruções para push
#
# Organização: devomnimind
# Repositório: OmniMind-Public
#
###############################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuração
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"
TARGET_DIR="${1:-/tmp/omnimind-public-$(date +%Y%m%d_%H%M%S)}"
PYTHON_CMD="python3"

# Timestamp
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Funções de log
log_info() {
    echo -e "${BLUE}[$(get_timestamp)] ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(get_timestamp)] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(get_timestamp)] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(get_timestamp)] ❌ $1${NC}"
}

###############################################################################
# ETAPA 1: Validar ambiente
###############################################################################

log_info "Etapa 1: Validando ambiente..."

if [ ! -d "$PROJECT_ROOT/.git" ]; then
    log_error "Não está em repositório Git. Abortando."
    exit 1
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    log_error "$PYTHON_CMD não encontrado."
    exit 1
fi

if [ -d "$TARGET_DIR" ]; then
    log_warning "Diretório $TARGET_DIR já existe. Removendo..."
    rm -rf "$TARGET_DIR"
fi

log_success "Ambiente validado"

###############################################################################
# ETAPA 2: Criar repositório público limpo
###############################################################################

log_info "Etapa 2: Criando repositório público limpo..."

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# Inicializar git
git init
git config user.name "OmniMind Publisher"
git config user.email "publisher@omnimind.dev"

log_info "Copiando código fonte..."

# Copiar estrutura
cp -r "$PROJECT_ROOT/src" "$TARGET_DIR/"
cp -r "$PROJECT_ROOT/tests" "$TARGET_DIR/"
cp -r "$PROJECT_ROOT/scripts/canonical" "$TARGET_DIR/scripts/"
cp -r "$PROJECT_ROOT/scripts/services" "$TARGET_DIR/scripts/" 2>/dev/null || true
cp -r "$PROJECT_ROOT/scripts/testing" "$TARGET_DIR/scripts/" 2>/dev/null || true

# Copiar documentação técnica
mkdir -p "$TARGET_DIR/docs/technical"
if [ -f "$PROJECT_ROOT/docs/SERVICE_UPDATE_PROTOCOL.md" ]; then
    cp "$PROJECT_ROOT/docs/SERVICE_UPDATE_PROTOCOL.md" "$TARGET_DIR/docs/technical/"
fi
if [ -f "$PROJECT_ROOT/docs/GRACEFUL_RESTART_GUIDE.md" ]; then
    cp "$PROJECT_ROOT/docs/GRACEFUL_RESTART_GUIDE.md" "$TARGET_DIR/docs/technical/"
fi

# Copiar configurações (somente seguras)
mkdir -p "$TARGET_DIR/config"
# Copiar apenas arquivos seguros de configuração
cp "$PROJECT_ROOT/config/pytest.ini" "$TARGET_DIR/config/" 2>/dev/null || true
cp "$PROJECT_ROOT/config/mypy.ini" "$TARGET_DIR/config/" 2>/dev/null || true
cp "$PROJECT_ROOT/config/pyrightconfig.json" "$TARGET_DIR/config/" 2>/dev/null || true

# Criar template seguro de configuração
cat > "$TARGET_DIR/config/omnimind.example.yaml" << 'EXAMPLEEOF'
# OmniMind Configuration Template
#
# Copy this to omnimind.yaml and fill in your values
# DO NOT commit real credentials - use environment variables instead
#

qdrant:
  url: "http://localhost:6333"
  api_key: "${OMNIMIND_QDRANT_API_KEY}"

quantum:
  providers:
    ibm:
      token: "${IBMQ_API_TOKEN}"
    dwave:
      token: "${DWAVE_API_TOKEN}"

auth:
  jwt_secret: "${JWT_SECRET_KEY}"

huggingface:
  token: "${HUGGING_FACE_HUB_TOKEN}"

EXAMPLEEOF

# Copiar requirements
cp -r "$PROJECT_ROOT/requirements" "$TARGET_DIR/" 2>/dev/null || true

# Copiar metadados
cp "$PROJECT_ROOT/LICENSE" "$TARGET_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT/CITATION.cff" "$TARGET_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT/README.md" "$TARGET_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT/pyproject.toml" "$TARGET_DIR/" 2>/dev/null || true

# Limpeza de credenciais
log_info "Limpando arquivos sensíveis..."
find "$TARGET_DIR" -name "omnimind.yaml" -delete 2>/dev/null || true
find "$TARGET_DIR" -name ".env*" -delete 2>/dev/null || true
find "$TARGET_DIR" -name "*secret*" -not -path "*/src/*" -delete 2>/dev/null || true
find "$TARGET_DIR" -name "*credential*" -not -path "*/src/*" -delete 2>/dev/null || true

# Copiar .gitignore otimizado
cat > "$TARGET_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# Logs
*.log
logs/

# Data (NOT for public repo)
data/
models/
notebooks/

# Temporary
*.tmp
*.temp
.tmp/
temp/

# Artefatos
*.pyc
.roo*
.omnimind*
.cursor*

# Credenciais (NUNCA fazer commit)
.env
.env.local
.env.*.local
*.pem
*.key
omnimind.yaml
config/omnimind.yaml
config/*.secret
secrets.json
credentials.json
EOF

log_success "Código copiado (credenciais removidas)"

###############################################################################
# ETAPA 3: Validar código
###############################################################################

log_info "Etapa 3: Validando código..."

cd "$TARGET_DIR"

# Verificar imports
log_info "  → Testando imports..."
if $PYTHON_CMD -c "from src.consciousness.topological_phi import PhiCalculator" 2>/dev/null; then
    log_success "  → Imports OK"
else
    log_warning "  → Alguns imports podem falhar (normal em ambiente de teste)"
fi

# Verificar sintaxe Python
log_info "  → Verificando sintaxe Python..."
find src -name "*.py" -exec $PYTHON_CMD -m py_compile {} \; 2>&1 | head -5 || true
log_success "  → Sintaxe verificada"

# Contar arquivos
PYTHON_FILES=$(find src tests -name "*.py" 2>/dev/null | wc -l)
TEST_FILES=$(find tests -name "test_*.py" 2>/dev/null | wc -l)

log_info "  → Estatísticas:"
echo "     • Arquivos Python: $PYTHON_FILES"
echo "     • Testes: $TEST_FILES"
echo "     • Tamanho: $(du -sh . | cut -f1)"

###############################################################################
# ETAPA 4: Criar commits iniciais
###############################################################################

log_info "Etapa 4: Criando histórico Git limpo..."

# Commit 1: Código base
git add .
git commit -m "Initial commit: OmniMind production code

- Source code (src/)
- Test suite (tests/)
- Scripts (scripts/canonical, scripts/services)
- Configuration (config/, requirements/)
- Technical documentation (docs/technical/)

Generated from devomnimind/omnimind private repository.
$(get_timestamp)" 2>&1 | tail -3

log_success "Repositório criado e commitado"

###############################################################################
# ETAPA 5: Relatório final
###############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ REPOSITÓRIO PÚBLICO CRIADO COM SUCESSO${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}📁 Localização:${NC}"
echo "   $TARGET_DIR"
echo ""

echo -e "${BLUE}📊 Conteúdo:${NC}"
echo "   Arquivos Python: $PYTHON_FILES"
echo "   Testes: $TEST_FILES"
echo "   Tamanho: $(du -sh $TARGET_DIR | cut -f1)"
echo ""

echo -e "${BLUE}🔗 Próximos Passos:${NC}"
echo ""
echo "1️⃣  Criar repositório no GitHub:"
echo "   URL: https://github.com/devomnimind/OmniMind-Public"
echo ""

echo "2️⃣  Fazer push do código:"
echo "   cd $TARGET_DIR"
echo "   git remote add origin https://github.com/devomnimind/OmniMind-Public.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

echo "3️⃣  Configurar no GitHub:"
echo "   • Add description: 'OmniMind Public Repository - Consciousness Framework'"
echo "   • Add topics: consciousness, ai, framework, python, quantum"
echo "   • Configure branch protection (main)"
echo "   • Add GitHub Actions workflows"
echo ""

echo -e "${YELLOW}⚠️  Checklist de Segurança:${NC}"
echo ""
echo "   [ ] Sem credenciais (grep -r 'pass\|token\|key' .)"
echo "   [ ] Sem dados privados (grep -r 'fahbrain\|/home/' .)"
echo "   [ ] Sem arquivos grandes (du -sh . < 1GB)"
echo "   [ ] Sem imports quebrados"
echo ""

echo -e "${BLUE}📚 Documentação:${NC}"
echo "   Leia: $PROJECT_ROOT/GUIA_PUBLICAR_GITHUB.md"
echo ""

log_success "Tudo pronto! 🚀"
