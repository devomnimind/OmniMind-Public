#!/bin/bash
# Script para executar vetorização completa do sistema Ubuntu e OmniMind
# Uso: ./vectorize_system.sh [opções]

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$PROJECT_DIR/scripts"
PYTHON_SCRIPT="$SCRIPT_DIR/vectorize_system.py"

# Logs
LOG_DIR="$PROJECT_DIR/logs"
VECTORIZE_LOG="$LOG_DIR/system_vectorization_$(date +%Y%m%d_%H%M%S).log"

# Função para logging
log() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1" | tee -a "$VECTORIZE_LOG"
}

error() {
    echo -e "${RED}[$(date +%H:%M:%S)] ERROR:${NC} $1" >&2 | tee -a "$VECTORIZE_LOG"
}

warn() {
    echo -e "${YELLOW}[$(date +%H:%M:%S)] WARNING:${NC} $1" | tee -a "$VECTORIZE_LOG"
}

info() {
    echo -e "${BLUE}[$(date +%H:%M:%S)] INFO:${NC} $1" | tee -a "$VECTORIZE_LOG"
}

# Verificar se estamos no diretório correto
check_project_dir() {
    if [[ ! -f "$PROJECT_DIR/pyproject.toml" ]]; then
        error "Diretório do projeto não encontrado. Execute a partir de scripts/"
        exit 1
    fi
}

# Verificar dependências
check_dependencies() {
    log "🔍 Verificando dependências..."

    # Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 não encontrado"
        exit 1
    fi

    # Docker
    if ! command -v docker &> /dev/null; then
        error "Docker não encontrado. Instale o Docker primeiro."
        exit 1
    fi

    # Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose não encontrado"
        exit 1
    fi

    # Verificar se script Python existe
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        error "Script Python não encontrado: $PYTHON_SCRIPT"
        exit 1
    fi

    log "✅ Dependências OK"
}

# Verificar/inicializar Qdrant
check_qdrant() {
    log "🔍 Verificando Qdrant..."

    # Verificar se Qdrant está rodando
    if curl -s http://localhost:6333/healthz &> /dev/null; then
        log "✅ Qdrant já está rodando"
        return 0
    fi

    # Tentar iniciar Qdrant
    log "🚀 Iniciando Qdrant..."

    cd "$PROJECT_DIR/deploy"

    # Usar docker-compose ou docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    # Iniciar apenas Qdrant
    $COMPOSE_CMD up -d qdrant

    # Aguardar Qdrant ficar pronto
    log "⏳ Aguardando Qdrant ficar pronto..."
    for i in {1..30}; do
        if curl -s http://localhost:6333/healthz &> /dev/null; then
            log "✅ Qdrant pronto!"
            return 0
        fi
        sleep 2
        echo -n "."
    done

    error "Qdrant não ficou pronto após 60 segundos"
    exit 1
}

# Verificar permissões de sistema
check_permissions() {
    log "🔐 Verificando permissões de acesso ao sistema..."

    # Arquivos críticos que precisam ser acessíveis
    critical_files=(
        "/proc/cpuinfo"
        "/proc/meminfo"
        "/etc/os-release"
        "/etc/hostname"
    )

    missing_permissions=()

    for file in "${critical_files[@]}"; do
        if [[ ! -r "$file" ]]; then
            missing_permissions+=("$file")
        fi
    done

    if [[ ${#missing_permissions[@]} -gt 0 ]]; then
        warn "Alguns arquivos do sistema podem não ser acessíveis:"
        for file in "${missing_permissions[@]}"; do
            warn "  - $file"
        done
        warn "Isso pode limitar a vetorização do sistema Ubuntu"
        warn "Considere executar com sudo se necessário (não recomendado para produção)"
    else
        log "✅ Permissões de sistema OK"
    fi
}

# Executar vetorização
run_vectorization() {
    local args="$*"

    log "🚀 Iniciando vetorização do sistema..."
    log "📝 Logs em: $VECTORIZE_LOG"
    log "📊 Comando: python3 $PYTHON_SCRIPT $args"

    # Criar diretório de logs se não existir
    mkdir -p "$LOG_DIR"

    # Executar script Python
    cd "$PROJECT_DIR"
    export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"

    if python3 "$PYTHON_SCRIPT" $args 2>&1 | tee -a "$VECTORIZE_LOG"; then
        log "✅ Vetorização concluída com sucesso!"
    else
        error "❌ Vetorização falhou. Verifique os logs em $VECTORIZE_LOG"
        exit 1
    fi
}

# Função principal
main() {
    echo "🧠 OmniMind - Vetorização Completa do Sistema Ubuntu"
    echo "=================================================="

    # Verificar argumentos
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        echo "Uso: $0 [opções]"
        echo ""
        echo "Opções:"
        echo "  --ubuntu-only     Vetorizar apenas sistema Ubuntu"
        echo "  --omnimind-only   Vetorizar apenas projeto OmniMind"
        echo "  --kernel-only     Vetorizar apenas kernel AI"
        echo "  --incremental     Indexação incremental"
        echo "  --search QUERY    Buscar no sistema vetorizado"
        echo "  --stats           Mostrar estatísticas"
        echo "  --help           Mostrar esta ajuda"
        echo ""
        echo "Exemplos:"
        echo "  $0                          # Vetorização completa"
        echo "  $0 --ubuntu-only           # Apenas Ubuntu"
        echo "  $0 --incremental           # Indexação incremental"
        echo "  $0 --search 'kernel info'  # Buscar informações do kernel"
        exit 0
    fi

    # Verificações iniciais
    check_project_dir
    check_dependencies
    check_qdrant
    check_permissions

    # Executar vetorização
    run_vectorization "$@"

    # Estatísticas finais
    log "📊 Estatísticas finais:"
    python3 "$PYTHON_SCRIPT" --stats 2>/dev/null | grep -E "(Total|Coleção|Dimensão)" | sed 's/^/  /' || true

    log "🎉 Processo concluído!"
    log "📝 Logs salvos em: $VECTORIZE_LOG"
}

# Executar função principal
main "$@"
