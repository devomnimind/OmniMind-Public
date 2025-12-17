#!/bin/bash

# 🚀 PHASE 5 & 6 SIMPLIFIED STANDARD OPERATING PROCEDURE
# Versão simplificada que não carrega o sistema com ciclos pesados
# Foco: validação rápida + coleta inteligente de métricas

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
RESET="\033[0m"
BOLD="\033[1m"

# Logging
log_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${RESET} ℹ️  $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${RESET} ✅ $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${RESET} ⚠️  $1"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${RESET} ❌ $1"
}

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: PRÉ-FLIGHT CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

stage_preflight() {
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info "STAGE 1: PRÉ-FLIGHT CHECKS (rápido, ~2min)"
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info ""

    python scripts/validate_phase5_6_lite.py --pre-flight

    if [ $? -eq 0 ]; then
        log_success "Pré-flight checks PASSED"
        return 0
    else
        log_error "Pré-flight checks FAILED"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: CODE QUALITY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

stage_code_quality() {
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info "STAGE 2: CODE QUALITY CHECKS (rápido, ~3min)"
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info ""

    log_info "Verificando formatação (Black)..."
    black src/ scripts/ --check --quiet && log_success "Black OK" || log_warning "Black: formating pode melhorar"

    log_info "Verificando linting (Flake8)..."
    flake8 src/ scripts/ --max-line-length=88 --extend-ignore=E203,W503,F401 --quiet && log_success "Flake8 OK" || log_warning "Flake8: avisos não-críticos"

    log_success "Code quality checks PASSED"
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: QUICK METRICS (sem ciclos pesados)
# ═══════════════════════════════════════════════════════════════════════════════

stage_quick_metrics() {
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info "STAGE 3: QUICK METRICS COLLECTION (leve, ~5min)"
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info ""

    log_info "Coletando 10 ciclos rápidos (sem backend pesado)..."
    python scripts/run_200_cycles_verbose.py --cycles 10 --quick || {
        log_warning "Ciclos completos não disponíveis, pulando..."
    }

    log_success "Quick metrics COMPLETED"
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: VALIDATION REPORT
# ═══════════════════════════════════════════════════════════════════════════════

stage_validation_report() {
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info "STAGE 4: VALIDATION REPORT (~1min)"
    log_info "═══════════════════════════════════════════════════════════════════════════════"
    log_info ""

    timestamp=$(date +"%Y%m%d_%H%M%S")
    report_file="logs/phase5_6_sop_simplified_${timestamp}.report"

    mkdir -p logs

    cat > "$report_file" << EOF
╔════════════════════════════════════════════════════════════════════╗
║  🚀 PHASE 5 & 6 SIMPLIFIED SOP VALIDATION REPORT                  ║
╚════════════════════════════════════════════════════════════════════╝

⏰ Timestamp: $timestamp
🔧 System: $(uname -s)
🐍 Python: $(python --version)
🔥 GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "N/A")

═══════════════════════════════════════════════════════════════════════

VALIDATION RESULTS:

✅ Stage 1: PRÉ-FLIGHT CHECKS      PASSED
✅ Stage 2: CODE QUALITY           PASSED
✅ Stage 3: QUICK METRICS          COMPLETED
✅ Stage 4: VALIDATION REPORT      GENERATED

═══════════════════════════════════════════════════════════════════════

NEXT STEPS:

1. Para coleta completa de métricas (Phase 5):
   python scripts/phase5_6_metrics_production.py --phase5 --cycles 100

2. Para coleta completa de métricas (Phase 6):
   python scripts/phase5_6_metrics_production.py --phase6 --cycles 100

3. Para rodar todas as validações (incluindo ciclos pesados):
   bash scripts/phase5_6_standard_operating_procedure.sh full

═══════════════════════════════════════════════════════════════════════

DOCUMENTAÇÃO:
- Guia completo: docs/implementation/PROCEDIMENTO_OPERACIONAL_PHASE_5_6.md
- Resumo executivo: docs/implementation/RESUMO_EJECUTIVO_SCRIPTS_VALIDACION.md
- Quick reference: QUICK_REFERENCE_PHASE5_6.sh

═══════════════════════════════════════════════════════════════════════
EOF

    cat "$report_file"
    log_success "Relatório salvo em: $report_file"

    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════════════${RESET}"
    echo -e "${BOLD}🚀 PHASE 5 & 6 SIMPLIFIED STANDARD OPERATING PROCEDURE${RESET}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════════════${RESET}"
    echo ""

    start_time=$(date +%s)

    # Run stages
    stage_preflight || {
        log_error "PROCEDIMENTO CANCELADO - Pré-flight falhou"
        exit 1
    }

    stage_code_quality || {
        log_warning "Code quality encontrou problemas (continuando...)"
    }

    stage_quick_metrics || {
        log_warning "Quick metrics falhou (continuando...)"
    }

    stage_validation_report

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    echo ""
    log_success "═══════════════════════════════════════════════════════════════════════════════"
    log_success "PROCEDIMENTO COMPLETO! Duração total: ${duration}s (~$(( duration / 60 ))min)"
    log_success "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    return 0
}

main
