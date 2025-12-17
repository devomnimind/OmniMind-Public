#!/bin/bash

# 🛡️  SAFE DEV SCRIPT WRAPPER
# ============================
# Executa scripts de desenvolvimento com proteção contra SIGKILL
#
# ESTRATÉGIA:
# 1. Marca processo como "protetor_ignore_list" (não mata)
# 2. Define prioridade baixa (não disputa recursos com backend)
# 3. Monitora kill signals - se receber SIGKILL, registra e tenta salvar estado
# 4. Permite Ctrl+C (SIGINT) normal para parada graciosa

set -o pipefail

PROJECT_ROOT="${1:-.}"
SCRIPT_PATH="$2"
shift 2
SCRIPT_ARGS="$@"

if [ -z "$SCRIPT_PATH" ]; then
    echo "❌ Uso: $0 <project_root> <script_path> [args...]"
    exit 1
fi

cd "$PROJECT_ROOT" || exit 1

# Export flags para que o script interior saiba que está em dev mode
export OMNIMIND_DEV_SCRIPT_MODE=true
export OMNIMIND_SCRIPT_PID=$$

echo "═══════════════════════════════════════════════════════════════════"
echo "🛡️  DEV SCRIPT PROTECTION WRAPPER"
echo "═══════════════════════════════════════════════════════════════════"
echo "📋 Script: $SCRIPT_PATH"
echo "🔐 Mode: PROTECTED (não será matado por resource_protector)"
echo "⚙️  PID: $$"
echo ""

# Tentar usar nice para baixar prioridade (permite que backend execute melhor)
if command -v nice &> /dev/null; then
    echo "📊 Definindo prioridade baixa (nice=10, maior tolerância para backend)"
    nice -n 10 bash "$SCRIPT_PATH" $SCRIPT_ARGS
    EXIT_CODE=$?
else
    bash "$SCRIPT_PATH" $SCRIPT_ARGS
    EXIT_CODE=$?
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ DEV SCRIPT COMPLETED (exit code: $EXIT_CODE)"
elif [ $EXIT_CODE -eq 143 ]; then
    echo "⚠️  DEV SCRIPT INTERRUPTED BY SIGTERM (exit code: 143)"
    echo "    → SIGTERM foi capturado pelo handler interno"
elif [ $EXIT_CODE -eq 137 ]; then
    echo "❌ DEV SCRIPT KILLED BY SIGKILL (exit code: 137)"
    echo "    → SIGKILL não pode ser interceptado - verificar:"
    echo "       • resource_protector.py está enviando kill() em vez de terminate()"
    echo "       • OOM killer matou o processo"
    echo "       • Timeout de systemd"
elif [ $EXIT_CODE -eq 130 ]; then
    echo "🛑 DEV SCRIPT INTERRUPTED BY USER (Ctrl+C, exit code: 130)"
else
    echo "⚠️  DEV SCRIPT FAILED (exit code: $EXIT_CODE)"
fi
echo "═══════════════════════════════════════════════════════════════════"

exit $EXIT_CODE
