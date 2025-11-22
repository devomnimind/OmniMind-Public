#!/bin/bash
# OmniMind Environment Initialization Script
# Inicializa ambiente virtual e serviços essenciais

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar se estamos no diretório correto
if [[ ! -f "requirements.txt" ]]; then
    error "Execute este script do diretório raiz do projeto OmniMind"
    exit 1
fi

log "🚀 Inicializando Ambiente OmniMind..."

# 1. Verificar/Criar ambiente virtual
if [[ ! -d ".venv" ]]; then
    log "Criando ambiente virtual..."
    python3 -m venv .venv
    success "Ambiente virtual criado"
else
    log "Ambiente virtual já existe"
fi

# 2. Ativar ambiente virtual
log "Ativando ambiente virtual..."
source .venv/bin/activate

# 3. Atualizar pip
log "Atualizando pip..."
python -m pip install --upgrade pip

# 4. Instalar dependências
log "Instalando dependências..."
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir -r requirements-dev.txt

# 5. Verificar instalação
log "Verificando instalação..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import qdrant_client; print('Qdrant Client: OK')"

# 6. Verificar serviços essenciais
log "Verificando serviços essenciais..."

# Verificar se portas estão livres
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        warning "Porta $port ($service) já está em uso"
        return 1
    else
        success "Porta $port ($service) está livre"
        return 0
    fi
}

check_port 3000 "Dashboard Web"
check_port 8000 "API FastAPI"
check_port 6333 "Qdrant Vector DB"
check_port 6379 "Redis Cache"

# 7. Inicializar serviços base (se disponíveis)
log "Tentando inicializar serviços base..."

# Qdrant (se docker-compose estiver disponível)
if command -v docker-compose >/dev/null 2>&1 && [[ -f "docker-compose.yml" ]]; then
    log "Iniciando Qdrant via Docker..."
    docker-compose up -d qdrant 2>/dev/null || warning "Falha ao iniciar Qdrant"
fi

# Redis (se docker-compose estiver disponível)
if command -v docker-compose >/dev/null 2>&1 && [[ -f "docker-compose.redis.yml" ]]; then
    log "Iniciando Redis via Docker..."
    docker-compose -f docker-compose.redis.yml up -d 2>/dev/null || warning "Falha ao iniciar Redis"
fi

# 8. Executar validações básicas
log "Executando validações básicas..."
python -c "import src.omnimind_core; print('✅ Core module imports successfully')"

# 9. Verificar status final
log "Verificação final do ambiente..."

# Verificar se podemos executar testes básicos
if python -m pytest tests/ -x --tb=line -q | grep -q "passed"; then
    success "Testes básicos passando"
else
    warning "Alguns testes podem estar falhando - verifique com 'pytest tests/'"
fi

success "🎉 Ambiente OmniMind inicializado com sucesso!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Execute: ./scripts/start_dashboard.sh"
echo "2. Acesse: http://localhost:3000"
echo "3. Para desenvolvimento: use as tasks do VS Code"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "- Testes: ./scripts/run_tests_parallel.sh fast"
echo "- Validação: ./scripts/validate_code.sh"
echo "- Dashboard: ./scripts/start_dashboard.sh"
echo ""

# Manter ambiente ativado para uso interativo
log "Ambiente ativado. Para sair, digite 'deactivate'"
exec $SHELL