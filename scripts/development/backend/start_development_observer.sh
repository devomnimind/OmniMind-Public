#!/bin/bash

# Development Observer Launcher - Versão Simplificada

echo "🚀 Iniciando Development Observer (Bash)..."

# Verificações básicas
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Execute do diretório omnimind/"
    exit 1
fi

# Ativar venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Ambiente virtual ativado"
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    exit 1
fi

# Criar logs
mkdir -p logs

echo "📁 Workspace: $(pwd)"
echo "🔍 PID: $$"
echo "📝 Logs: logs/development_observer.log"
echo ""
echo "Pressione Ctrl+C para parar..."
echo "----------------------------------------"

# Executar diretamente
PYTHONPATH="$(pwd)/src" python3 scripts/run_development_observer.py</content>
<parameter name="filePath">/home/fahbrain/projects/omnimind/scripts/start_development_observer.sh