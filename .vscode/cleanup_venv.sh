#!/bin/bash
# Script para limpar venvs extras e manter apenas o do projeto

echo "🧹 Limpando venv e configurações..."

# 1. Limpar cache Python
echo "1️⃣  Removendo cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "✅ Cache Python limpo"

# 2. Limpar cache de interpreters do VS Code
echo "2️⃣  Removendo cache de interpreters do VS Code..."
rm -rf ~/.config/"Code - Insiders"/User/globalStorage/ms-python.vscode-python-envs/pythonLocator/*.3.json 2>/dev/null
echo "✅ Cache de interpreters removido"

# 3. Limpar cache Pylance
echo "3️⃣  Removendo cache Pylance..."
rm -rf ~/.config/"Code - Insiders"/User/globalStorage/ms-python.vscode-pylance 2>/dev/null
echo "✅ Cache Pylance removido"

# 4. Verificar que só existe um venv
echo "4️⃣  Verificando venv do projeto..."
VENV_COUNT=$(find ~ -maxdepth 3 -type d \( -name ".venv" -o -name "venv" \) 2>/dev/null | wc -l)
echo "✅ Total de venv encontrados: $VENV_COUNT (esperado: 1)"

# 5. Validar venv
echo "5️⃣  Validando venv local..."
if [ -f ".venv/bin/python" ]; then
    PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
    echo "✅ venv válido: $PYTHON_VERSION"
else
    echo "❌ Erro: .venv/bin/python não encontrado"
    exit 1
fi

echo ""
echo "🎉 Limpeza concluída!"
echo "📝 Próximo passo: Recarregue o VS Code (Ctrl+Shift+P > reload)"
