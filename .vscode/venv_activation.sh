#!/bin/bash
# 🚀 VENV ACTIVATION SCRIPT FOR VS CODE TERMINAL
# Automatically activated when terminal opens in VS Code
# Loads .env automatically

set -a

# Source the .env file if it exists
if [ -f "${OMNIMIND_ROOT:-$(pwd)}/.env" ]; then
    # shellcheck disable=SC1090
    source "${OMNIMIND_ROOT:-$(pwd)}/.env"
    echo "✅ .env loaded"
fi

# Activate venv
VENV_PATH="${OMNIMIND_ROOT:-.}/.venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    # shellcheck disable=SC1090
    source "$VENV_PATH"
    echo "✅ venv activated: $(python3 --version)"
else
    echo "⚠️  venv not found at $VENV_PATH"
fi

set +a

# Show status
echo "════════════════════════════════════"
echo "🧠 OmniMind Development Environment"
echo "════════════════════════════════════"
echo "Python: $(which python3)"
echo "PYTHONPATH: $PYTHONPATH"
echo "VIRTUAL_ENV: $VIRTUAL_ENV"
echo "════════════════════════════════════"
