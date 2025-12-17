#!/bin/bash
# ============================================================================
# Wrapper seguro para vetorização com venv e sudo
# ============================================================================
# USO:
#   ./scripts/indexing/vectorize.sh --skip-external
#   ./scripts/indexing/vectorize.sh --dry-run
#   ./scripts/indexing/vectorize.sh (full)
#
# POR QUÊ ISSO FUNCIONA:
#   - sudo -E não preserva VIRTUAL_ENV no bash (problema nativo do sudo)
#   - Usar /home/fahbrain/projects/omnimind/.venv/bin/python3 funciona porque:
#     * Python puro não depende de variáveis de ambiente
#     * site-packages já estão no sys.path do venv
#     * Módulos instalados no venv são encontrados automaticamente
# ============================================================================

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"

# Verificar se venv existe
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ ERRO: venv não encontrado em $VENV_PYTHON"
    echo "Por favor execute: python3 -m venv $PROJECT_ROOT/.venv"
    exit 1
fi

# Verificar permissões para /var/log/ se logs do Ubuntu forem coletados
if [[ "$@" != *"--skip-ubuntu"* ]]; then
    if ! sudo -n ls /var/log/ > /dev/null 2>&1; then
        echo "⚠️  AVISO: Você precisará de acesso sudo para coletar logs de /var/log/"
        echo "   Execute com: sudo ./scripts/indexing/vectorize.sh $@"
    fi
fi

# Executar script de vetorização com caminho correto do venv
echo "🚀 Executando vetorização com: $VENV_PYTHON"
echo "📝 Argumentos: $@"
echo ""

# Se não tem sudo ou não precisa, executar sem sudo
if [[ "$@" == *"--skip-external"* ]] || [[ "$@" == *"--skip-ubuntu"* ]]; then
    exec "$VENV_PYTHON" "$PROJECT_ROOT/scripts/indexing/vectorize_omnimind.py" "$@"
else
    # Precisamos de sudo para /var/log/
    exec sudo "$VENV_PYTHON" "$PROJECT_ROOT/scripts/indexing/vectorize_omnimind.py" "$@"
fi
