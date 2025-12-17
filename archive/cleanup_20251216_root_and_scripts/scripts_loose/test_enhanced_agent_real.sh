#!/bin/bash
# Script para executar testes reais do EnhancedCodeAgent
# Autor: Fabrício da Silva + assistência de IA

set -e

cd "$(dirname "$0")/.."

echo "=" | tr -d '\n' | head -c 80 && echo
echo "🧪 TESTES REAIS: EnhancedCodeAgent Integration"
echo "=" | tr -d '\n' | head -c 80 && echo
echo

# Ativar ambiente virtual
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "✅ Ambiente virtual ativado"
else
    echo "❌ Ambiente virtual não encontrado em .venv/"
    exit 1
fi

# Verificar dependências
echo
echo "1. Verificando dependências..."
python3 << 'PYEOF'
import sys
try:
    from src.agents.orchestrator_agent import OrchestratorAgent
    from src.agents.enhanced_code_agent import EnhancedCodeAgent
    print("   ✅ Imports OK")
except Exception as e:
    print(f"   ❌ Erro nos imports: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo "❌ Falha na verificação de dependências"
    exit 1
fi

# Verificar se config existe
if [ ! -f "config/agent_config.yaml" ]; then
    echo "❌ Arquivo config/agent_config.yaml não encontrado"
    exit 1
fi

echo "   ✅ Config encontrado"

# Executar testes
echo
echo "2. Executando testes reais..."
echo

# Opção 1: Teste individual
if [ "$1" == "single" ]; then
    TEST_NAME="${2:-test_initialization_with_orchestrator}"
    echo "   Executando: $TEST_NAME"
    pytest tests/agents/test_enhanced_code_agent_integration.py::TestEnhancedCodeAgentIntegration::"$TEST_NAME" \
        -v --tb=short -m real "$@"

# Opção 2: Todos os testes da classe
elif [ "$1" == "all" ]; then
    echo "   Executando todos os testes da classe..."
    pytest tests/agents/test_enhanced_code_agent_integration.py::TestEnhancedCodeAgentIntegration \
        -v --tb=short -m real "$@"

# Opção 3: Com logs detalhados
elif [ "$1" == "verbose" ]; then
    echo "   Executando com logs detalhados..."
    pytest tests/agents/test_enhanced_code_agent_integration.py::TestEnhancedCodeAgentIntegration \
        -v --tb=long -m real -s "$@"

# Opção 4: Apenas testes rápidos (sem Ollama)
elif [ "$1" == "fast" ]; then
    echo "   Executando testes rápidos (sem chamadas Ollama)..."
    pytest tests/agents/test_enhanced_code_agent_integration.py::TestEnhancedCodeAgentIntegration::test_initialization_with_orchestrator \
        tests/agents/test_enhanced_code_agent_integration.py::TestEnhancedCodeAgentIntegration::test_auto_error_detection_integration \
        -v --tb=short -m real "$@"

# Default: ajuda
else
    echo "Uso: $0 [single|all|verbose|fast] [args...]"
    echo
    echo "Opções:"
    echo "  single <test_name>  - Executa um teste específico"
    echo "  all                 - Executa todos os testes da classe"
    echo "  verbose             - Executa com logs detalhados (-s)"
    echo "  fast                - Executa apenas testes rápidos"
    echo
    echo "Exemplos:"
    echo "  $0 single test_initialization_with_orchestrator"
    echo "  $0 all"
    echo "  $0 verbose"
    echo "  $0 fast"
    exit 0
fi

echo
echo "=" | tr -d '\n' | head -c 80 && echo
echo "✅ Testes concluídos"
echo "=" | tr -d '\n' | head -c 80 && echo

