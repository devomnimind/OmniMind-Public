#!/bin/bash
# OmniMind Canonical Action Logger CLI
# Interface para registro de ações das AIs

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

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    error "Python3 não encontrado"
    exit 1
fi

# Verificar se estamos no diretório do projeto
if [[ ! -f "src/audit/canonical_logger.py" ]]; then
    error "Não estamos no diretório raiz do projeto OmniMind"
    exit 1
fi

# Comando principal
case "$1" in
    "log")
        if [[ $# -lt 6 ]]; then
            echo "Uso: $0 log <ai_agent> <action_type> <target> <result> <description> [details] [impact] [auto_actions...]"
            exit 1
        fi
        
        AI_AGENT="$2"
        ACTION_TYPE="$3"
        TARGET="$4"
        RESULT="$5"
        DESCRIPTION="$6"
        DETAILS="${7:-}"
        IMPACT="${8:-}"
        shift 8
        AUTO_ACTIONS="$*"
        
        log "Registrando ação: $AI_AGENT $ACTION_TYPE $TARGET"
        
        # Executar registro
        if python3 -c "
import sys
sys.path.insert(0, 'src')
from audit.canonical_logger import canonical_logger

auto_actions = ['$AUTO_ACTIONS' ] if '$AUTO_ACTIONS' else []
hash_result = canonical_logger.log_action(
    ai_agent='$AI_AGENT',
    action_type='$ACTION_TYPE', 
    target='$TARGET',
    result='$RESULT',
    description='$DESCRIPTION',
    details='$DETAILS',
    impact='$IMPACT',
    automatic_actions=auto_actions
)
print(f'Ação registrada com hash: {hash_result}')
        "; then
            success "Ação registrada com sucesso"
        else
            error "Falha ao registrar ação"
            exit 1
        fi
        ;;
        
    "validate")
        log "Validando integridade do log canônico..."
        if python3 -c "
import sys
sys.path.insert(0, 'src')
from audit.canonical_logger import canonical_logger
if canonical_logger.validate_integrity():
    print('✅ Integridade validada')
else:
    print('❌ Integridade comprometida')
    sys.exit(1)
        "; then
            success "Integridade validada"
        else
            error "Integridade comprometida!"
            exit 1
        fi
        ;;
        
    "metrics")
        log "Exibindo métricas atuais..."
        python3 -c "
import sys
sys.path.insert(0, 'src')
from audit.canonical_logger import canonical_logger
import json
metrics = canonical_logger.get_metrics()
print(json.dumps(metrics, indent=2))
        "
        ;;
        
    "help"|*)
        echo "OmniMind Canonical Action Logger CLI"
        echo ""
        echo "Uso: $0 <comando> [opções]"
        echo ""
        echo "Comandos:"
        echo "  log <ai_agent> <action_type> <target> <result> <description> [details] [impact] [auto_actions...]  - Registrar ação"
        echo "  validate                                                                                          - Validar integridade"
        echo "  metrics                                                                                           - Exibir métricas"
        echo "  help                                                                                              - Esta ajuda"
        echo ""
        echo "Exemplos:"
        echo "  $0 log CODE_AGENT FILE_MODIFIED src/main.py SUCCESS 'Arquivo modificado'"
        echo "  $0 validate"
        echo "  $0 metrics"
        ;;
esac