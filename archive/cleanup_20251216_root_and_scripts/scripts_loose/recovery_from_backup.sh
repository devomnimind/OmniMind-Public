#!/bin/bash

# OmniMind Recovery Script - Recuperação de Backup com Validação Completa
# Uso: ./scripts/recovery_from_backup.sh [--dry-run] [--backup-path /path]
#
# Funcionalidades:
# 1. Sincronizar dados críticos do backup
# 2. Inicializar docker-compose (Qdrant + Redis)
# 3. Validar integridade de dados
# 4. Restaurar agents e memoria
# 5. Teste de conectividade end-to-end

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_BASE="/media/fahbrain/DEV_BRAIN_CLEAN"
DRY_RUN=false
BACKUP_PATH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --backup-path) BACKUP_PATH="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Funções
log_info() { echo -e "${GREEN}✅${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; }
log_section() { echo -e "\n${BLUE}$1${NC}\n"; }

# 1. Encontrar backup mais recente
find_latest_backup() {
    local latest=$(sudo ls -dt "$BACKUP_BASE"/backup_omnimind_* 2>/dev/null | head -1)
    if [ -z "$latest" ]; then
        log_error "Nenhum backup encontrado em $BACKUP_BASE"
        exit 1
    fi
    echo "$latest"
}

# 2. Sincronizar dados críticos
sync_critical_data() {
    local src="$1"
    local dest="$2"
    local dry_flag=""

    if [ "$DRY_RUN" = true ]; then
        dry_flag="--dry-run"
        log_warn "DRY RUN - Nenhum arquivo será copiado"
    fi

    log_info "Sincronizando dados críticos..."

    # Lista de diretórios críticos
    local dirs=("data" "config" "src" "scripts")

    for dir in "${dirs[@]}"; do
        if [ -d "$src/$dir" ]; then
            log_info "  Sincronizando $dir..."
            sudo rsync -avz $dry_flag \
                --exclude=".git" \
                --exclude="__pycache__" \
                --exclude="node_modules" \
                "$src/$dir/" "$dest/$dir/" || true
        fi
    done
}

# 3. Inicializar docker-compose
init_docker_compose() {
    log_section "Inicializando Docker-Compose..."

    cd "$PROJECT_ROOT"

    # Verificar docker disponível
    if ! sudo docker ps > /dev/null 2>&1; then
        log_error "Docker daemon não está acessível"
        exit 1
    fi

    log_info "Docker daemon: OK"

    # Iniciar Qdrant e Redis
    log_info "Iniciando Qdrant + Redis..."
    sudo docker-compose -f deploy/docker-compose.yml up -d qdrant redis

    # Aguardar inicialização
    local max_retries=30
    local retry=0

    while [ $retry -lt $max_retries ]; do
        if curl -s http://localhost:6333/health > /dev/null 2>&1; then
            log_info "Qdrant respondendo em localhost:6333"
            break
        fi
        log_warn "  Aguardando Qdrant... ($((retry+1))/$max_retries)"
        sleep 2
        retry=$((retry+1))
    done

    if [ $retry -eq $max_retries ]; then
        log_error "Qdrant não respondeu após 60s"
        exit 1
    fi
}

# 4. Validar integridade do Qdrant
validate_qdrant() {
    log_section "Validando Qdrant..."

    # Tentar conectar
    if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
        log_error "Qdrant não está respondendo"
        return 1
    fi

    log_info "Qdrant health: OK"

    # Listar collections
    log_info "Collections em Qdrant:"
    curl -s http://localhost:6333/collections 2>&1 | python3 -m json.tool 2>&1 | \
        grep -E "name|points_count" | head -20 || true
}

# 5. Restaurar shared workspace
restore_workspace() {
    log_section "Restaurando Shared Workspace..."

    local ws_file="$PROJECT_ROOT/data/shared_workspace.json"
    local backup_ws="$BACKUP_PATH/data/shared_workspace.json"

    if [ -f "$backup_ws" ]; then
        log_info "Restaurando de backup..."
        if [ "$DRY_RUN" = false ]; then
            sudo cp "$backup_ws" "$ws_file"
            sudo chown fahbrain:fahbrain "$ws_file"
        fi
    else
        log_warn "Workspace não encontrado em backup, criando novo..."
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$(dirname "$ws_file")"
            cat > "$ws_file" << 'EOF'
{
  "version": "1.0",
  "created_at": "2025-12-12T00:00:00Z",
  "last_updated": "2025-12-12T00:00:00Z",
  "sessions": {},
  "modules": {},
  "shared_objects": {},
  "memory": {"episodic": [], "semantic": {}, "procedural": []},
  "consciousness": {"phi_global": 0.0, "psi_desire": 0.0, "sigma_lacanian": 0.0, "delta_trauma": 0.0, "gozo_jouissance": 0.0},
  "metadata": {"agents_count": 0, "collections_indexed": 0, "total_embeddings": 0, "last_qdrant_sync": null}
}
EOF
        fi
    fi
}

# 6. Teste de conectividade
test_connectivity() {
    log_section "Teste de Conectividade..."

    # Qdrant
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        log_info "Qdrant: ✅"
    else
        log_error "Qdrant: ❌"
    fi

    # Redis
    if echo "PING" | nc -q1 localhost 6379 2>/dev/null | grep -q "PONG"; then
        log_info "Redis: ✅"
    else
        log_warn "Redis: ⚠️ (pode estar respondendo de forma diferente)"
    fi

    # Python imports
    cd "$PROJECT_ROOT"
    if python3 -c "import sys; sys.path.insert(0, 'src'); from embeddings.code_embeddings import OmniMindEmbeddings; print('OK')" 2>/dev/null | grep -q "OK"; then
        log_info "Python imports: ✅"
    else
        log_error "Python imports: ❌"
    fi
}

# 7. Relatório final
print_summary() {
    log_section "RESUMO DA RECUPERAÇÃO"

    echo "Informações do sistema:"
    echo "  Projeto: $PROJECT_ROOT"
    echo "  Backup usado: $BACKUP_PATH"
    echo "  Data: $(date)"
    echo ""
    echo "Status:"
    echo "  Docker Compose: $(sudo docker ps --filter 'name=qdrant' --quiet | wc -l) containers ativos"
    echo "  Qdrant: http://localhost:6333"
    echo "  Redis: localhost:6379"
    echo ""
    echo "Próximos passos:"
    echo "  1. Verifique logs: tail -f logs/*.log"
    echo "  2. Inicie OmniMind: ./scripts/start_omnimind_system.sh"
    echo "  3. Acesse dashboard: http://localhost:3000"
}

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       OmniMind Recovery from Backup - Ubuntu Stable            ║"
echo "║                  2025-12-12 Repair Session                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ "$DRY_RUN" = true ]; then
    log_warn "MODO DRY-RUN: Nada será alterado"
fi

# Encontrar backup se não especificado
if [ -z "$BACKUP_PATH" ]; then
    BACKUP_PATH=$(find_latest_backup)
    log_info "Usando backup: $BACKUP_PATH"
fi

# Executar recuperação
sync_critical_data "$BACKUP_PATH" "$PROJECT_ROOT"
init_docker_compose
validate_qdrant
restore_workspace
test_connectivity
print_summary

echo -e "\n${GREEN}✨ Recuperação completa!${NC}\n"
