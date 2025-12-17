#!/bin/bash

# OmniMind Pre-Commit Hook Script
# Garante que o código esteja formatado e testado antes de permitir o commit.

set -e

echo "🔍 [OmniMind] Executando verificações pré-commit..."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PYTHON="$VENV_PATH/bin/python"

# Verificar se o venv existe
if [ ! -f "$PYTHON" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado em $VENV_PATH"
    exit 1
fi

cd "$PROJECT_ROOT"

# 1. Formatação (Black)
echo "⚫ Verificando formatação (Black)..."
"$PYTHON" -m black --check src tests web
if [ $? -ne 0 ]; then
    echo "⚠️  Código não formatado. Rodando Black..."
    "$PYTHON" -m black src tests web
fi

# 2. Ordenação de Imports (Isort)
echo "📚 Verificando imports (Isort)..."
"$PYTHON" -m isort --check-only src tests web
if [ $? -ne 0 ]; then
    echo "⚠️  Imports desordenados. Rodando Isort..."
    "$PYTHON" -m isort src tests web
fi

# 3. Tipagem Estática (MyPy) - Opcional no hook para não bloquear rápido demais, mas recomendado
# echo "types Verificando tipagem (MyPy)..."
# "$PYTHON" -m mypy src

# 4. Testes Rápidos (apenas unitários, não integração pesada)
echo "🧪 Rodando testes unitários essenciais..."
"$PYTHON" -m pytest -m "not integration" --maxfail=1
if [ $? -ne 0 ]; then
    echo "❌ Testes falharam. Corrija-os antes de commitar."
    exit 1
fi

echo "✅ [OmniMind] Tudo pronto. Código limpo e funcional."
exit 0

