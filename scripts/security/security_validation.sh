#!/usr/bin/env bash
set -euo pipefail

PYTHON=${PYTHON:-python3}
SCRIPT_DIR=$(dirname "$0")
VALIDATOR="$SCRIPT_DIR/validate_security.py"

if [[ ! -f "$VALIDATOR" ]]; then
  echo "Arquivo de validação de segurança ausente: $VALIDATOR" >&2
  exit 1
fi

echo "Executando validações periódicas de segurança..."
"$PYTHON" "$VALIDATOR"
