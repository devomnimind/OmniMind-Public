#!/bin/bash
# Proteção contra vazamento de arquivos para /home/fahbrain/projects/

set -e

PARENT_DIR="/home/fahbrain/projects"
PROJECT_DIR="/home/fahbrain/projects/omnimind"

# Lista de arquivos/pastas que NÃO devem estar em /home/fahbrain/projects/
FORBIDDEN_ITEMS=(
    ".coverage"
    ".pytest_cache"
    "config"
    "data"
    "logs"
    ".omnimind"
    ".vscode"
    "htmlcov"
    "*.pyc"
    "__pycache__"
)

echo "🔍 Verificando integridade da estrutura do projeto..."

# Verificar se cada item proibido existe na pasta superior
for item in "${FORBIDDEN_ITEMS[@]}"; do
    if ls -d "$PARENT_DIR/$item" 2>/dev/null | grep -q "$item"; then
        echo "❌ VAZAMENTO DETECTADO: $PARENT_DIR/$item"
        rm -rf "$PARENT_DIR/$item"
        echo "   ✅ Removido"
    fi
done

# Verificar se os itens críticos existem NO PROJETO
CRITICAL_DIRS=(
    ".git"
    ".github"
    "src"
    "tests"
    "docs"
    "config"
    "data"
)

echo ""
echo "✅ Validando estrutura interna..."
for dir in "${CRITICAL_DIRS[@]}"; do
    if [ -d "$PROJECT_DIR/$dir" ]; then
        echo "   ✓ $dir"
    else
        echo "   ⚠️  Falta: $dir"
    fi
done

# Criar/restaurar .coveragerc se necessário
if [ ! -f "$PROJECT_DIR/.coveragerc" ]; then
    cat > "$PROJECT_DIR/.coveragerc" << 'COVERAGE_EOF'
[run]
data_file = .coverage
parallel = False

[report]
exclude_lines =
    pragma: no cover
    # pragma: no cover
COVERAGE_EOF
    echo "✅ .coveragerc restaurado"
fi

# Criar conftest.py se necessário
if [ ! -f "$PROJECT_DIR/conftest.py" ]; then
    cat > "$PROJECT_DIR/conftest.py" << 'CONFTEST_EOF'
"""Project-wide pytest configuration."""
import os
import sys

# Ensure .pytest_cache is created locally in project root
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "0"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
CONFTEST_EOF
    echo "✅ conftest.py restaurado"
fi

echo ""
echo "🔒 Proteção de estrutura COMPLETA"
