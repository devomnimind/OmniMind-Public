#!/bin/bash

# ============================================================================
# 🔐 OMNIMIND SYSTEM START WITH SUDO - AUTO-RECOVERY VERSION
# ============================================================================
# Este script é executado pelo próprio OmniMind quando detecta falhas
# Requer configuração de sudo NOPASSWD para execução não-interativa
# ============================================================================
# Setup necessário (uma vez):
#   sudo visudo
#   Adicionar linha: $USER ALL=(ALL) NOPASSWD: /home/fahbrain/projects/omnimind/scripts/canonical/system/start_omnimind_system_sudo_auto.sh
# ============================================================================

set -o pipefail

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# HELPER: Executar comando com sudo se necessário
# ============================================================================

run_cmd() {
    local cmd="$1"
    local description="${2:-Executando comando}"

    echo -e "${BLUE}[CMD]${NC} $description"
    echo -e "${BLUE}    → ${NC}$cmd"

    # Se já estamos como root, executar direto
    if [ "$EUID" -eq 0 ]; then
        bash -c "$cmd" 2>&1
    else
        # Tentar com sudo -n (sem senha)
        if sudo -n true 2>/dev/null; then
            sudo bash -c "$cmd" 2>&1
        else
            # Se sudo com senha, avisar ao usuário
            echo -e "${YELLOW}⚠️  Comando requer sudo (será solicitada senha):${NC}"
            sudo bash -c "$cmd" 2>&1
        fi
    fi

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Sucesso"
    else
        echo -e "${RED}✗${NC} Falha (exit code: $exit_code)"
    fi

    return $exit_code
}

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

echo -e "${GREEN}🚀 OmniMind Auto-Recovery System (v1.0)${NC}"
echo "   Iniciado em: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Calcular PROJECT_ROOT
if [ -n "${OMNIMIND_PROJECT_ROOT:-}" ]; then
    PROJECT_ROOT="$OMNIMIND_PROJECT_ROOT"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    while [ "$SCRIPT_DIR" != "/" ]; do
        if [ -f "$SCRIPT_DIR/.env" ] || [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
            PROJECT_ROOT="$SCRIPT_DIR"
            break
        fi
        SCRIPT_DIR="$(dirname "$SCRIPT_DIR")"
    done
    [ -z "$PROJECT_ROOT" ] && PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
fi

[ ! -d "$PROJECT_ROOT" ] && echo -e "${RED}❌ PROJECT_ROOT não encontrado${NC}" && exit 1

export OMNIMIND_PROJECT_ROOT="$PROJECT_ROOT"
export OMNIMIND_AUTO_RECOVERY=true

log_file="$PROJECT_ROOT/logs/auto_recovery_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$log_file")"

echo "   Project Root: $PROJECT_ROOT"
echo "   Log file: $log_file"
echo ""

# Função de log
log_msg() {
    local level="$1"
    local msg="$2"
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] [$level] $msg" >> "$log_file"
    echo -e "${BLUE}[$level]${NC} $msg"
}

# ============================================================================
# DETECÇÃO DE PROBLEMAS E RECOVERY
# ============================================================================

echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}PHASE 1: DIAGNÓSTICO DE PROBLEMA${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

PROBLEM_DETECTED=false
PROBLEM_DESCRIPTION=""

# Verificar Backend Primary
if ! curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
    PROBLEM_DETECTED=true
    PROBLEM_DESCRIPTION="Backend Primary (8000) não respondendo"
    echo -e "${RED}✗${NC} Backend Primary (8000) não respondendo"
    log_msg "DETECTION" "Backend Primary falhou"
else
    echo -e "${GREEN}✓${NC} Backend Primary (8000) respondendo"
fi

# Verificar Frontend
if [ -z "$(pgrep -f 'npm.*dev' | head -1)" ]; then
    PROBLEM_DETECTED=true
    PROBLEM_DESCRIPTION="${PROBLEM_DESCRIPTION}\nFrontend não está rodando"
    echo -e "${RED}✗${NC} Frontend não está rodando"
    log_msg "DETECTION" "Frontend não rodando"
else
    echo -e "${GREEN}✓${NC} Frontend rodando"
fi

# Verificar Ciclo Principal
if [ -z "$(pgrep -f 'python.*src\.main' | head -1)" ]; then
    echo -e "${YELLOW}⚠${NC} Ciclo Principal não está rodando (pode ser normal)"
    log_msg "DETECTION" "Ciclo Principal não rodando"
fi

echo ""

if [ "$PROBLEM_DETECTED" = false ]; then
    echo -e "${GREEN}✅ Nenhum problema detectado!${NC}"
    log_msg "DETECTION" "Sistema saudável - nenhuma ação necessária"
    exit 0
fi

echo -e "${RED}⚠️  PROBLEMA DETECTADO:${NC}"
echo -e "$PROBLEM_DESCRIPTION"
log_msg "DETECTION" "Problema detectado: $PROBLEM_DESCRIPTION"

# ============================================================================
# PHASE 2: RECOVERY
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}PHASE 2: RECOVERY (Auto-Repair)${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

# Estratégia 1: Matar e reiniciar processos zumbis
echo -e "${YELLOW}Estratégia 1: Limpeza de Processos${NC}"
log_msg "RECOVERY" "Iniciando limpeza de processos"

# Listar processos antes
echo -e "${BLUE}Processos Python antes da limpeza:${NC}"
ps aux | grep -E "[p]ython|[u]vivicorn|[n]pm.*dev" | head -5

# Matar processos problemáticos
run_cmd "pkill -9 -f 'uvicorn.*8000'" "Matando Backend Primary (8000)"
run_cmd "pkill -9 -f 'uvicorn.*8080'" "Matando Backend Secondary (8080)"
run_cmd "pkill -9 -f 'python -m src.main'" "Matando Ciclo Principal"
run_cmd "pkill -f 'npm.*dev'" "Parando Frontend"

sleep 3

# Listar processos depois
echo -e "${BLUE}Processos Python após limpeza:${NC}"
ps aux | grep -E "[p]ython|[u]vivicorn|[n]pm.*dev" | head -5

log_msg "RECOVERY" "Limpeza de processos completa"

# ============================================================================
# PHASE 3: RESTART
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}PHASE 3: REINICIALIZAÇÃO${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

log_msg "RECOVERY" "Iniciando reinicialização do sistema"

cd "$PROJECT_ROOT"

# Usar script robusto se disponível
STARTUP_SCRIPT="$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system_robust.sh"
if [ ! -f "$STARTUP_SCRIPT" ]; then
    STARTUP_SCRIPT="$PROJECT_ROOT/scripts/canonical/system/start_omnimind_system.sh"
fi

if [ ! -f "$STARTUP_SCRIPT" ]; then
    echo -e "${RED}❌ Script de startup não encontrado${NC}"
    log_msg "ERROR" "Script de startup não encontrado: $STARTUP_SCRIPT"
    exit 1
fi

# Executar script de startup
echo -e "${BLUE}Executando: $STARTUP_SCRIPT${NC}"
log_msg "RECOVERY" "Executando startup script: $STARTUP_SCRIPT"

# Exportar variáveis para o script de startup
export OMNIMIND_PROJECT_ROOT="$PROJECT_ROOT"
export OMNIMIND_AUTO_RECOVERY=true
export OMNIMIND_DEBUG=false

# Executar e capturar output
if bash "$STARTUP_SCRIPT" 2>&1 | tee -a "$log_file"; then
    log_msg "RECOVERY" "Startup script completado com sucesso"
else
    log_msg "ERROR" "Startup script falhou"
    exit 1
fi

# ============================================================================
# PHASE 4: VALIDAÇÃO
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}PHASE 4: VALIDAÇÃO${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

sleep 10  # Aguardar inicialização

VALIDATION_OK=true

# Validar Backend Primary
echo -e "${BLUE}Validando Backend Primary (8000)...${NC}"
for i in 1 2 3; do
    if curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend Primary respondendo"
        log_msg "VALIDATION" "Backend Primary validado"
        break
    fi
    if [ $i -lt 3 ]; then
        echo -e "${YELLOW}⚠${NC} Tentativa $i falhou, retentando em 5s..."
        sleep 5
    else
        echo -e "${RED}✗${NC} Backend Primary não respondeu"
        log_msg "ERROR" "Backend Primary não respondeu após 3 tentativas"
        VALIDATION_OK=false
    fi
done

# Validar Frontend
echo -e "${BLUE}Validando Frontend...${NC}"
if pgrep -f 'npm.*dev' > /dev/null; then
    echo -e "${GREEN}✓${NC} Frontend rodando"
    log_msg "VALIDATION" "Frontend validado"
else
    echo -e "${RED}✗${NC} Frontend não está rodando"
    log_msg "ERROR" "Frontend não validado"
    VALIDATION_OK=false
fi

# ============================================================================
# RESULTADO FINAL
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

if [ "$VALIDATION_OK" = true ]; then
    echo -e "${GREEN}✅ RECOVERY COMPLETO - SISTEMA RESTAURADO${NC}"
    log_msg "SUCCESS" "Auto-recovery completo - sistema restaurado"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}⚠️  RECOVERY PARCIAL - ALGUNS SERVIÇOS NÃO VALIDADOS${NC}"
    log_msg "WARNING" "Recovery parcial - validação incompleta"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

    # Enviar notificação ou alertar
    if command -v logger &> /dev/null; then
        logger -t "omnimind-auto-recovery" -p user.warn "Auto-recovery parcial - validação incompleta"
    fi

    exit 1
fi
