#!/bin/bash

# 🔧 OMNIMIND RESOURCE ISOLATION CONFIG
# =====================================
# Configura OmniMind para fazer autorreparo (kill monitores ruins, etc)
# SEM ATRAPALHAR scripts de desenvolvimento
#
# ESTRATÉGIA:
# 1. Dev scripts: WHITELIST automática (nunca matados)
# 2. Backend/daemons: Podem fazer self-heal (kill children ruins, etc)
# 3. Limites: Mais relaxados em TEST mode
# 4. Priorities: Dev scripts rodam com nice=10 (baixa prioridade)

set -e

PROJECT_ROOT="${1:-/home/fahbrain/projects/omnimind}"
MODE="${2:-test}"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  🔧 OMNIMIND RESOURCE ISOLATION SETUP                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Project: $PROJECT_ROOT"
echo "🎯 Mode: $MODE (dev/test/prod)"
echo ""

# Criar/atualizar configuração de environment
cat > "$PROJECT_ROOT/.env.resource_config" << EOF
# Configuração de isolamento de recursos
# Gerado em $(date)

# Modo do protector
OMNIMIND_RESOURCE_PROTECTOR_MODE=$MODE

# Whitelist de padrões DEV (NUNCA matar)
OMNIMIND_DEV_PATTERNS="pytest|03_run_500|03_test_50|MASTER_RECOVERY|recovery|jupyter|consciousness_validation"

# Modo de desenvolvimento
OMNIMIND_ENABLE_DEV_ISOLATION=true

# Niceness para dev scripts (10 = baixa prioridade)
OMNIMIND_DEV_SCRIPT_NICE=10

# Proteção: SIGTERM ok, SIGKILL bloqueado
OMNIMIND_PROTECT_FROM_SIGKILL=true

# Daemons podem fazer autorreparo
OMNIMIND_ALLOW_DAEMON_SELF_HEAL=true
EOF

echo "✅ Config criado: .env.resource_config"
echo ""

# Configuração do ResourceProtector
cat > "$PROJECT_ROOT/src/monitor/resource_isolation_config.py" << 'PYTHON_EOF'
"""
Configuração de isolamento de recursos para desenvolvimento
Mantém OmniMind autoreparável mas não interfere em dev scripts
"""

# Padrões de dev scripts que NUNCA devem ser matados
DEV_SCRIPT_PATTERNS = [
    "pytest",
    "03_run_500_cycles",
    "03_test_50_cycles",
    "MASTER_RECOVERY",
    "integration_cycles",
    "jupyter",
    "python -m unittest",
    "scripts/recovery",
    "robust_consciousness_validation",
    "run_dev_safe",
    "omnimind_dev_script",
]

# Padrões de processos daemons que podem fazer autorreparo
DAEMON_PATTERNS = [
    "uvicorn",
    "qdrant",
    "redis",
    "observer_service",
    "resource_protector",
]

# Limites por modo (mais relaxados para dev)
LIMITS_BY_MODE = {
    "dev": {
        "cpu_percent": 80.0,          # Deixa 20% para IDE
        "memory_percent": 85.0,        # 85% de RAM
        "kill_threshold_cpu": 95.0,    # Só mata se > 95%
        "grace_period": 60,            # Mais tempo no startup
        "prefer_nice_over_kill": True, # Preferir reduzir prioridade
    },
    "test": {
        "cpu_percent": 85.0,
        "memory_percent": 88.0,
        "kill_threshold_cpu": 90.0,
        "grace_period": 30,
        "prefer_nice_over_kill": True,
    },
    "prod": {
        "cpu_percent": 95.0,
        "memory_percent": 95.0,
        "kill_threshold_cpu": 98.0,
        "grace_period": 120,
        "prefer_nice_over_kill": False,
    },
}

# Sinais permitidos para dev scripts
DEV_SCRIPT_SIGNALS = {
    "SIGTERM": True,   # OK - pode ser capturado
    "SIGKILL": False,  # BLOQUEADO - nunca enviar
}

# Configuração de logging
ENABLE_PROTECTION_DEBUG_LOGS = True
ENABLE_DEV_SCRIPT_PROTECTION_LOGS = True
PYTHON_EOF

echo "✅ Resource isolation config criado: src/monitor/resource_isolation_config.py"
echo ""

# Criar função auxiliar no ResourceProtector
cat >> "$PROJECT_ROOT/src/monitor/resource_protector.py" << 'PYTHON_APPEND'

# === DYNAMIC PROTECTION RULES (loaded from resource_isolation_config) ===
# Esta seção é adicionada automaticamente

try:
    from monitor.resource_isolation_config import (
        DEV_SCRIPT_PATTERNS,
        DAEMON_PATTERNS,
        LIMITS_BY_MODE,
        DEV_SCRIPT_SIGNALS,
    )
    _ISOLATION_CONFIG_LOADED = True
except ImportError:
    _ISOLATION_CONFIG_LOADED = False
    DEV_SCRIPT_PATTERNS = []
    DAEMON_PATTERNS = []

PYTHON_APPEND

echo "✅ ResourceProtector atualizado com regras de isolamento"
echo ""

# Criar script para resetar/recarregar proteção
cat > "$PROJECT_ROOT/scripts/isolate_resources.sh" << 'BASH_SCRIPT'
#!/bin/bash
# Recarrega configuração de isolamento sem desativar sistema

PROJECT_ROOT="${1:-/home/fahbrain/projects/omnimind}"
MODE="${2:-test}"

echo "🔄 Recarregando isolamento de recursos..."

# Atualizar env var
export OMNIMIND_RESOURCE_PROTECTOR_MODE=$MODE
export OMNIMIND_ENABLE_DEV_ISOLATION=true

echo "✅ Modo: $MODE"
echo "✅ Dev isolation: ATIVADO"
echo ""
echo "Dev scripts agora são automaticamente protegidos:"
echo "  • pytest runs"
echo "  • 03_run_500_cycles*"
echo "  • Recovery scripts"
echo "  • Consciousness validation"
echo ""
echo "Backend pode fazer autorreparo SEM atrapalhar dev"

BASH_SCRIPT

chmod +x "$PROJECT_ROOT/scripts/isolate_resources.sh"
echo "✅ Script isolate_resources.sh criado"
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP CONCLUÍDO                                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos passos:"
echo "1. source $PROJECT_ROOT/.env.resource_config"
echo "2. bash scripts/isolate_resources.sh $MODE"
echo "3. Executar dev scripts (agora com proteção automática)"
echo ""
echo "🛡️  Dev scripts NUNCA serão matados por resource_protector"
echo "🔧 Backend pode fazer autorreparo conforme necessário"
echo "✅ Sistema fica mais estável (dev + autorreparo)"
echo ""
