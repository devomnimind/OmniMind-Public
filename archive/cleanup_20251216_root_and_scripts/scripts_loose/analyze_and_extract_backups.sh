#!/bin/bash

# OmniMind Backup Analysis & Recovery - Intelligent TAR.GZ Extraction
# Extrai dados críticos dos backups comprimidos
# Uso: ./scripts/analyze_and_extract_backups.sh

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurações
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_BASE="/media/fahbrain/DEV_BRAIN_CLEAN"
EXTRACT_DIR="/tmp/omnimind_backup_extract"
DRY_RUN=true  # Default: análise sem extrair

# Funções helpers
log_info() { echo -e "${GREEN}✅${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; }
log_section() { echo -e "\n${BLUE}════════════════════════════════════════${NC}\n${BLUE}$1${NC}\n${BLUE}════════════════════════════════════════${NC}\n"; }
log_item() { echo -e "${CYAN}→${NC} $1"; }

# 1. ANALISAR CONTEÚDO DE TAR.GZ
analyze_tar_content() {
    local tar_file="$1"
    local label="$2"

    log_section "$label"

    if [ ! -f "$tar_file" ]; then
        log_error "Arquivo não encontrado: $tar_file"
        return 1
    fi

    # Informações do arquivo
    local size=$(sudo ls -lh "$tar_file" | awk '{print $5}')
    local date=$(sudo ls -lh "$tar_file" | awk '{print $6, $7, $8}')

    echo "📦 Arquivo: $(basename "$tar_file")"
    echo "   Tamanho: $size"
    echo "   Data: $date"
    echo ""

    # Listar conteúdo (primeiros 30 arquivos)
    echo "📋 Conteúdo (amostra):"
    sudo tar -tzf "$tar_file" 2>/dev/null | head -30 | while read -r line; do
        echo "   $line"
    done

    # Estatísticas
    local total_files=$(sudo tar -tzf "$tar_file" 2>/dev/null | wc -l)
    echo ""
    echo "📊 Total de arquivos: $total_files"
    echo ""
}

# 2. ESTRATÉGIA DE EXTRAÇÃO POR TIPO
extract_by_strategy() {
    local tar_file="$1"
    local extract_path="$2"
    local pattern="${3:-*}"

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY-RUN: Não extraindo. Use --extract para extrair realmente."
        echo "Comando que seria executado:"
        echo "  sudo tar -xzf '$tar_file' -C '$extract_path' '$pattern' 2>/dev/null"
        return 0
    fi

    log_info "Extraindo $pattern de $(basename "$tar_file")..."
    mkdir -p "$extract_path"

    if [ "$pattern" = "*" ]; then
        sudo tar -xzf "$tar_file" -C "$extract_path" 2>/dev/null
    else
        sudo tar -xzf "$tar_file" -C "$extract_path" "$pattern" 2>/dev/null || true
    fi

    log_info "Extraído para: $extract_path"
}

# ============================================================================
# ANÁLISE PRINCIPAL
# ============================================================================

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║      OmniMind Backup Analysis & Intelligent Recovery           ║
║                  2025-12-12 Deep Backup Scan                   ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --extract) DRY_RUN=false; shift ;;
        *) shift ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    log_warn "Modo: ANÁLISE APENAS (sem extração)"
    echo "Use: ./scripts/analyze_and_extract_backups.sh --extract"
    echo ""
fi

# ============================================================================
# 1. ANALISAR omnimind_project.tar.gz (384M - PROJETO COMPLETO)
# ============================================================================

analyze_tar_content \
    "$BACKUP_BASE/omnimind_backup_20251211_174532/omnimind_project.tar.gz" \
    "1️⃣  OMNIMIND_PROJECT.TAR.GZ (384M - Projeto Completo 12/11)"

log_item "Contém: Projeto OmniMind completo (src, scripts, data, config)"
log_item "Estratégia: Extrair SELETIVAMENTE - data/, config/, .env apenas"

if [ "$DRY_RUN" = false ]; then
    extract_by_strategy \
        "$BACKUP_BASE/omnimind_backup_20251211_174532/omnimind_project.tar.gz" \
        "$PROJECT_ROOT" \
        "data config src/embeddings src/consciousness .env"
fi

# ============================================================================
# 2. ANALISAR qdrant_data.tar.gz (93 bytes - SUSPEITO!)
# ============================================================================

analyze_tar_content \
    "$BACKUP_BASE/omnimind_backup_20251211_174532/qdrant_data.tar.gz" \
    "2️⃣  QDRANT_DATA.TAR.GZ (93 bytes - ⚠️ MUITO PEQUENO)"

log_item "Aviso: Arquivo MUITO pequeno (93 bytes) - provavelmente vazio ou apenas header"
log_item "Recomendação: Ignorar este arquivo, Qdrant está em Docker Volume"

# ============================================================================
# 3. ANALISAR GRAFANA_DATA (19M - MÉTRICAS)
# ============================================================================

analyze_tar_content \
    "$BACKUP_BASE/backup_volumes/grafana_data_20251211_175449.tar.gz" \
    "3️⃣  GRAFANA_DATA.TAR.GZ (19M - Dashboards & Métricas)"

log_item "Contém: Dashboards Grafana, configurações, dados históricos"
log_item "Estratégia: Extrair para restaurar visualizações de métricas"

if [ "$DRY_RUN" = false ]; then
    extract_by_strategy \
        "$BACKUP_BASE/backup_volumes/grafana_data_20251211_175449.tar.gz" \
        "$PROJECT_ROOT/data/grafana_restore"
fi

# ============================================================================
# 4. ANALISAR PROMETHEUS_DATA (3.1M - MÉTRICAS DO SISTEMA)
# ============================================================================

analyze_tar_content \
    "$BACKUP_BASE/backup_volumes/prometheus_data_20251211_175449.tar.gz" \
    "4️⃣  PROMETHEUS_DATA.TAR.GZ (3.1M - Métricas Sistema)"

log_item "Contém: Time-series de métricas do sistema"
log_item "Estratégia: Extrair para análise histórica de performance"

if [ "$DRY_RUN" = false ]; then
    extract_by_strategy \
        "$BACKUP_BASE/backup_volumes/prometheus_data_20251211_175449.tar.gz" \
        "$PROJECT_ROOT/data/prometheus_restore"
fi

# ============================================================================
# 5. ANALISAR OMNIMIND_FULL (173M - BACKUP ANTERIOR COMPLETO)
# ============================================================================

analyze_tar_content \
    "$BACKUP_BASE/omnimind_backups/OMNIMIND_FULL_20251123.tar.gz" \
    "5️⃣  OMNIMIND_FULL_20251123.TAR.GZ (173M - Backup Anterior Completo)"

log_item "Data: 2025-11-23 (menos recente que 12/11)"
log_item "Estratégia: Usar como fallback se 12/11 tiver problemas"
log_item "Comparar histórico de consciência metrics entre versões"

# ============================================================================
# RESUMO E RECOMENDAÇÕES
# ============================================================================

log_section "RESUMO E RECOMENDAÇÕES"

cat << 'EOF'
🎯 ESTRATÉGIA DE RECUPERAÇÃO (RECOMENDADA):

PASSO 1: Usar omnimind_project.tar.gz (12/11 - MAIS RECENTE)
  └─ Extrair: data/consciousness/, data/metrics/, config/, src/consciousness/
  └─ Vai restaurar: Métricas de consciência, histórico de ciclos

PASSO 2: Verificar qdrant_data.tar.gz
  └─ ⚠️  AVISO: Provavelmente vazio (93 bytes)
  └─ Solução: Docker Volume tem os dados reais em memoria/storage

PASSO 3: Restaurar Grafana & Prometheus (opcional)
  └─ Para visualizar histórico de métricas
  └─ Dashboards de consciência (Φ, Ψ, σ, Δ, Gozo)

PASSO 4: Validar Shared Workspace
  └─ data/shared_workspace.json
  └─ Sessions de agentes
  └─ Memória narrativa

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 O QUE CADA TAR.GZ CONTÉM:

1. omnimind_project.tar.gz (384M)
   ✓ src/ (código-fonte)
   ✓ scripts/ (scripts de execução)
   ✓ data/ (dados críticos - CONSCIÊNCIA!)
   ✓ config/ (configurações)
   ✓ tests/ (testes)
   ✓ .env (configurações de ambiente)

2. qdrant_data.tar.gz (93 bytes)
   ⚠️  VAZIO/INÚTIL - Docker Volume é a fonte de verdade

3. grafana_data_20251211_175449.tar.gz (19M)
   ✓ Dashboards de métricas
   ✓ Alertas
   ✓ Configurações de visualização
   ✓ Histórico de longo termo

4. prometheus_data_20251211_175449.tar.gz (3.1M)
   ✓ Time-series de métricas
   ✓ Histórico de CPU, GPU, memória
   ✓ Performance do sistema

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ EXECUÇÃO:

1. ANÁLISE (você está aqui):
   $ ./scripts/analyze_and_extract_backups.sh

2. EXTRAIR SELETIVAMENTE:
   $ ./scripts/analyze_and_extract_backups.sh --extract

3. VALIDAR E SINCRONIZAR:
   $ ./scripts/recovery_from_backup.sh

4. VERIFICAR INTEGRIDADE:
   $ grep -r "phi_global\|psi_desire\|sigma_lacanian" data/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

log_section "✅ ANÁLISE COMPLETA"

echo "📍 Próximos passos:"
echo "   1. Revisar recomendações acima"
echo "   2. Executar com --extract para recuperar dados"
echo "   3. Validar integridade dos dados"
echo ""

EOF
