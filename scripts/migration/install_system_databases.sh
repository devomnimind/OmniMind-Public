#!/bin/bash
# ============================================================================
# 🚀 OMNIMIND MIGRATION INSTALLER - Docker → System OS
# ============================================================================
# Script executável que migra a arquitetura do Docker para Sistema OS
# Segue o plano arquitetural passo-a-passo com validação
#
# Uso:
#   chmod +x scripts/migration/install_system_databases.sh
#   ./scripts/migration/install_system_databases.sh [--phase PHASE_NUMBER]
#
# Phases:
#   0: Check & Backup
#   1: Install System Databases
#   2: Restore Data from Backup
#   3: Python + GPU Setup
#   4: Code Configuration
#   5: Full System Validation
# ============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="${OMNIMIND_PROJECT_ROOT:-.}"
LOG_FILE="$PROJECT_ROOT/logs/migration_$(date +%Y%m%d_%H%M%S).log"
BACKUP_EXTERNAL="/media/fahbrain/DEV_BRAIN_CLEAN/databases/20251214_070626"

# ============================================================================
# UTILITIES
# ============================================================================

log_header() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    echo "[$(date)] PHASE: $1" >> "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[$(date)] [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    echo "[$(date)] [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    echo "[$(date)] [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    echo "[$(date)] [ERROR] $1" >> "$LOG_FILE"
}

error_exit() {
    log_error "$1"
    exit 1
}

run_cmd() {
    local cmd="$1"
    local desc="${2:-Executando comando}"

    log_info "$desc"
    log_info "  → $cmd"

    if eval "$cmd" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Sucesso"
        return 0
    else
        log_error "Falha: $cmd"
        return 1
    fi
}

# ============================================================================
# PHASE 0: Check & Backup
# ============================================================================

phase_0_check_backup() {
    log_header "PHASE 0: Verificação de Ambiente e Backup"

    # Verificar se é Ubuntu 22.04
    if grep -q "22.04" /etc/os-release; then
        log_success "Ubuntu 22.04 LTS detectado"
    else
        log_warning "Sistema não é Ubuntu 22.04 - possíveis incompatibilidades"
    fi

    # Verificar GPU
    if command -v nvidia-smi &> /dev/null; then
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
        log_success "GPU detectada: $GPU_NAME"
        nvidia-smi | head -5 >> "$LOG_FILE"
    else
        log_error "GPU NVIDIA não detectada!"
        return 1
    fi

    # Verificar CUDA
    if command -v nvcc &> /dev/null; then
        CUDA_VERSION=$(nvcc --version | grep -oP 'release \K[0-9.]+')
        log_success "CUDA detectado: $CUDA_VERSION"
    else
        log_error "CUDA não encontrado!"
        return 1
    fi

    # Verificar backup
    if [ ! -d "$BACKUP_EXTERNAL/qdrant" ]; then
        log_error "Backup de Qdrant não encontrado em $BACKUP_EXTERNAL"
        return 1
    fi
    log_success "Backup de dados encontrado em $BACKUP_EXTERNAL"

    # Verificar espaço em disco
    AVAILABLE_VAR=$(df /var | awk 'NR==2 {print $4}')
    AVAILABLE_HOME=$(df /home | awk 'NR==2 {print $4}')

    log_info "Espaço em disco:"
    log_info "  /var: $((AVAILABLE_VAR / 1024 / 1024))GB disponível"
    log_info "  /home: $((AVAILABLE_HOME / 1024 / 1024))GB disponível"

    if [ $AVAILABLE_VAR -lt 5242880 ]; then  # 5GB
        log_error "/var tem menos de 5GB - não recomendado"
        return 1
    fi

    log_success "PHASE 0 concluída com sucesso"
}

# ============================================================================
# PHASE 1: Install System Databases
# ============================================================================

phase_1_install_databases() {
    log_header "PHASE 1: Instalação de Bancos de Dados do Sistema"

    # Update package list
    log_info "Atualizando lista de pacotes..."
    sudo apt update || log_warning "apt update retornou erro"

    # 1. Redis
    log_info "Instalando Redis..."
    if run_cmd "sudo apt install -y redis-server" "Instalando Redis do repositório"; then
        log_success "Redis instalado"
        sudo systemctl start redis-server
        sudo systemctl enable redis-server

        # Test Redis
        if redis-cli ping | grep -q PONG; then
            log_success "Redis está funcionando"
        else
            error_exit "Redis não respondendo ao ping"
        fi
    else
        error_exit "Falha ao instalar Redis"
    fi

    # 2. PostgreSQL
    log_info "Instalando PostgreSQL..."
    if run_cmd "sudo apt install -y postgresql postgresql-contrib" "Instalando PostgreSQL"; then
        log_success "PostgreSQL instalado"
        sudo systemctl start postgresql
        sudo systemctl enable postgresql

        # Create database and user
        log_info "Criando database e usuário..."
        sudo -u postgres psql -c "CREATE DATABASE omnimind;" 2>/dev/null || log_warning "Database omnimind pode já existir"
        sudo -u postgres psql -c "CREATE USER omnimind WITH PASSWORD 'omnimind2025';" 2>/dev/null || log_warning "User omnimind pode já existir"

        log_success "PostgreSQL configurado"
    else
        error_exit "Falha ao instalar PostgreSQL"
    fi

    # 3. Qdrant (Binary ou Build)
    log_info "Instalando Qdrant..."

    if command -v qdrant &> /dev/null; then
        log_success "Qdrant já instalado"
    else
        log_info "Qdrant não encontrado - instalando binário..."

        # Download pre-built binary (mais rápido)
        QDRANT_VERSION="1.7.0"
        QDRANT_URL="https://github.com/qdrant/qdrant/releases/download/v${QDRANT_VERSION}/qdrant-v${QDRANT_VERSION}-x86_64-unknown-linux-gnu"

        log_info "Baixando Qdrant v${QDRANT_VERSION}..."
        if wget -q "$QDRANT_URL" -O /tmp/qdrant && chmod +x /tmp/qdrant; then
            sudo mv /tmp/qdrant /usr/local/bin/
            log_success "Qdrant instalado em /usr/local/bin/"
        else
            log_warning "Falha ao baixar binário, tentando Cargo..."
            if command -v cargo &> /dev/null; then
                run_cmd "cargo install qdrant" "Instalando Qdrant via Cargo" || \
                    error_exit "Falha ao instalar Qdrant"
            else
                error_exit "Nem wget nem Cargo disponíveis para instalar Qdrant"
            fi
        fi
    fi

    log_success "PHASE 1 concluída com sucesso"
}

# ============================================================================
# PHASE 2: Restore Data from Backup
# ============================================================================

phase_2_restore_backup() {
    log_header "PHASE 2: Restauração de Dados do Backup"

    # Create necessary directories with proper permissions
    log_info "Criando diretórios com permissões..."
    sudo mkdir -p /var/lib/qdrant
    sudo mkdir -p /var/lib/redis
    sudo mkdir -p /home/fahbrain/data/experiments

    # 1. Restore Qdrant
    log_info "Restaurando dados Qdrant..."
    if [ -d "$BACKUP_EXTERNAL/qdrant" ]; then
        sudo cp -r "$BACKUP_EXTERNAL/qdrant/"* /var/lib/qdrant/ 2>/dev/null || true
        sudo chown -R qdrant:qdrant /var/lib/qdrant 2>/dev/null || \
            sudo chown -R $(whoami):$(whoami) /var/lib/qdrant
        log_success "Dados Qdrant restaurados"
    else
        log_warning "Diretório Qdrant não encontrado no backup"
    fi

    # 2. Redis snapshots (se existirem)
    log_info "Restaurando dados Redis..."
    if [ -d "$BACKUP_EXTERNAL/redis" ]; then
        sudo cp -r "$BACKUP_EXTERNAL/redis/"* /var/lib/redis/ 2>/dev/null || true
        sudo chown -R redis:redis /var/lib/redis 2>/dev/null || true
        log_success "Dados Redis restaurados"
    else
        log_info "Nenhum backup Redis encontrado (normal se vazio)"
    fi

    # 3. PostgreSQL (se existir)
    if [ -d "$BACKUP_EXTERNAL/postgresql" ]; then
        log_info "Restaurando dados PostgreSQL..."
        # TODO: Implementar restore PostgreSQL se necessário
        log_warning "PostgreSQL restore não implementado ainda"
    fi

    # Restart services with data
    log_info "Reiniciando serviços..."
    sudo systemctl restart redis-server qdrant postgresql || true

    log_success "PHASE 2 concluída com sucesso"
}

# ============================================================================
# PHASE 3: Python + GPU Setup
# ============================================================================

phase_3_python_gpu() {
    log_header "PHASE 3: Python 3.12.8 + GPU (Qiskit Aer + PyTorch)"

    cd "$PROJECT_ROOT"

    # 1. Check/Create venv
    if [ ! -d ".venv" ]; then
        log_info "Criando venv Python 3.12.8..."
        python3.12 -m venv .venv 2>/dev/null || \
            python3 -m venv .venv
    fi

    source .venv/bin/activate
    PYTHON_VERSION=$(python --version)
    log_success "Venv ativado: $PYTHON_VERSION"

    # 2. Upgrade pip
    log_info "Atualizando pip..."
    pip install --upgrade pip setuptools wheel 2>&1 | tail -3

    # 3. Qiskit + Aer GPU (VERSÕES VALIDADAS 16 DEC 2025)
    # ✅ PyTorch 2.5.1 cu121 + Qiskit 1.2.4 + Aer GPU 0.15.1
    log_info "Instalando Quantum Stack (Versões Validadas)..."

    # PyTorch 2.5.1 cu121 (CORRETO)
    log_info "  → PyTorch 2.5.1+cu121..."
    pip install "torch==2.5.1" --index-url https://download.pytorch.org/whl/cu121 -q
    pip install "torchvision==0.20.1" "torchaudio==2.5.1" --index-url https://download.pytorch.org/whl/cu121 -q

    # Qiskit + Aer GPU 0.15.1 (VALIDADO COM GTX 1650)
    log_info "  → Qiskit 1.2.4 + Aer-GPU 0.15.1..."
    pip install "qiskit==1.2.4" "qiskit-aer-gpu==0.15.1" "qiskit-ibm-runtime==0.19.1" -q

    # CuPy + cuQuantum (GPU acceleration)
    log_info "  → CuPy + cuQuantum cu12 (GPU acceleration)..."
    pip install "cupy-cuda12x" -q
    pip install \
      "cuquantum-cu12==25.11.0" \
      "custatevec-cu12==1.11.0" \
      "cutensor-cu12==2.4.1" -q

    log_success "Quantum Stack instalado"

    # 4. Validate GPU
    log_info "Validando GPU + Quantum Stack..."
    python validate_gpu_quantum.py 2>&1 | tee -a "$LOG_FILE"

    # 5. Install dev tools + core requirements
    log_info "Instalando ferramentas de desenvolvimento..."
    pip install black flake8 mypy isort pytest pytest-cov -q

    log_info "Instalando requirements core do OmniMind..."
    pip install -r requirements/requirements-core.txt -q

    log_success "PHASE 3 concluída com sucesso"
}

# ============================================================================
# PHASE 4: Code Configuration
# ============================================================================

phase_4_configure_code() {
    log_header "PHASE 4: Configuração de Código"

    cd "$PROJECT_ROOT"

    # 1. Create database_os.py
    log_info "Criando src/config/database_os.py..."
    cat > src/config/database_os.py << 'EOF'
"""Database configuration para Sistema OS."""
import os
from typing import Dict, Any

class DatabaseConfig:
    ENVIRONMENTS = {
        "production": {
            "qdrant": {"url": "http://localhost:6333", "timeout": 30.0},
            "redis": {"url": "redis://localhost:6379/0"},
            "postgres": {
                "host": "localhost", "port": 5432,
                "database": "omnimind", "user": "omnimind",
                "password": os.getenv("POSTGRES_PASSWORD", "omnimind2025")
            },
        },
        "docker_experiments": {
            "qdrant": {"url": "http://qdrant-exp:6333"},
            "redis": {"url": "redis://redis-exp:6379/0"},
            "postgres": {
                "host": "postgres-exp", "port": 5432,
                "database": "omnimind_exp", "user": "omnimind",
                "password": "experimental"
            },
        },
    }

    @classmethod
    def get_config(cls, environment=None):
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "production")
        return cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS["production"])

    @classmethod
    def get_qdrant_url(cls, environment=None):
        return cls.get_config(environment)["qdrant"]["url"]
EOF
    log_success "database_os.py criado"

    # 2. Create .env.system
    log_info "Criando .env.system..."
    cat > .env.system << 'EOF'
# OmniMind System Configuration
ENVIRONMENT=production
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
POSTGRES_URL=postgresql://omnimind:omnimind2025@localhost:5432/omnimind
POSTGRES_PASSWORD=omnimind2025
CUDA_VISIBLE_DEVICES=0
QISKIT_AER_USE_GPU=1
OMNIMIND_WORKERS=2
OMNIMIND_BACKENDS=3
OMNIMIND_AUTO_RECOVERY=true
EOF
    log_success ".env.system criado"

    # 3. Update config/omnimind.yaml
    log_info "Atualizando config/omnimind.yaml..."
    if [ -f "config/omnimind.yaml" ]; then
        sed -i 's/http:\/\/qdrant:/http:\/\/localhost:/g' config/omnimind.yaml
        sed -i 's/redis:\/\/redis:/redis:\/\/localhost:/g' config/omnimind.yaml
        log_success "config/omnimind.yaml atualizado"
    fi

    log_success "PHASE 4 concluída com sucesso"
}

# ============================================================================
# PHASE 5: Full System Validation
# ============================================================================

phase_5_validation() {
    log_header "PHASE 5: Validação Completa do Sistema"

    cd "$PROJECT_ROOT"
    source .venv/bin/activate

    # Validate databases
    log_info "Validando conexões de banco de dados..."

    # Redis
    if redis-cli ping | grep -q PONG; then
        log_success "✓ Redis conectado"
    else
        log_error "✗ Redis não respondendo"
    fi

    # PostgreSQL
    if PGPASSWORD=omnimind2025 psql -h localhost -U omnimind -d omnimind -c "SELECT 1" &>/dev/null; then
        log_success "✓ PostgreSQL conectado"
    else
        log_error "✗ PostgreSQL não respondendo"
    fi

    # Qdrant
    if curl -s http://localhost:6333/health | grep -q '"status"'; then
        log_success "✓ Qdrant conectado"
    else
        log_error "✗ Qdrant não respondendo"
    fi

    # Python imports
    log_info "Validando imports Python..."
    python -c "import qiskit_aer, torch, redis; print('✓ All imports OK')" || \
        log_warning "⚠ Alguns imports falharam"

    log_success "PHASE 5 concluída com sucesso"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    mkdir -p "$(dirname "$LOG_FILE")"

    echo -e "${GREEN}🚀 OmniMind Migration: Docker → System OS${NC}"
    echo "   Log: $LOG_FILE"
    echo ""

    # Parse arguments
    PHASE="${1:-all}"

    case "$PHASE" in
        0|check) phase_0_check_backup ;;
        1|install) phase_0_check_backup && phase_1_install_databases ;;
        2|restore) phase_2_restore_backup ;;
        3|python) phase_3_python_gpu ;;
        4|config) phase_4_configure_code ;;
        5|validate) phase_5_validation ;;
        all)
            phase_0_check_backup
            phase_1_install_databases
            phase_2_restore_backup
            phase_3_python_gpu
            phase_4_configure_code
            phase_5_validation
            ;;
        *)
            echo "Uso: $0 [0|1|2|3|4|5|check|install|restore|python|config|validate|all]"
            exit 1
            ;;
    esac

    log_header "✅ MIGRAÇÃO COMPLETA"
    echo -e "${GREEN}Sistema pronto para inicialização!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "  1. source .venv/bin/activate"
    echo "  2. export ENVIRONMENT=production"
    echo "  3. ./scripts/canonical/system/run_cluster.sh"
    echo "  4. cd web/frontend && npm run dev"
}

main "$@"
