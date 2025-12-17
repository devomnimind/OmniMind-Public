#!/bin/bash

# Setup IDE Environment for OmniMind (VS Code / Cursor)
# This script ensures the development environment is configured correctly.

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

echo "=== OmniMind IDE Setup ==="
echo "Project Root: $PROJECT_ROOT"

# 1. Ensure Virtual Environment
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# 2. Install Dev Tools
echo "Installing/Updating Development Tools (Black, Isort, Pylint, MyPy)..."
"$VENV_PATH/bin/pip" install --upgrade pip black isort pylint flake8 mypy pytest > /dev/null

# 3. Configure VS Code / Cursor Extensions
echo "Installing Recommended Extensions..."

# Detect editor command
EDITOR_CMD=""
if command -v cursor &> /dev/null; then
    EDITOR_CMD="cursor"
elif command -v code &> /dev/null; then
    EDITOR_CMD="code"
fi

if [ -n "$EDITOR_CMD" ]; then
    echo "Detected Editor: $EDITOR_CMD"
    $EDITOR_CMD --install-extension ms-python.python --force
    $EDITOR_CMD --install-extension ms-python.vscode-pylance --force
    $EDITOR_CMD --install-extension ms-python.black-formatter --force
    $EDITOR_CMD --install-extension ms-python.isort --force
    $EDITOR_CMD --install-extension ms-python.flake8 --force
    $EDITOR_CMD --install-extension matangover.mypy --force
    $EDITOR_CMD --install-extension njpwerner.autodocstring --force
    $EDITOR_CMD --install-extension tamasfe.even-better-toml --force
else
    echo "WARNING: 'cursor' or 'code' command not found in PATH. Please install extensions manually from .vscode/extensions.json"
fi

# 4. Verify Settings
SETTINGS_PATH="$PROJECT_ROOT/.vscode/settings.json"
if [ -f "$SETTINGS_PATH" ]; then
    echo "Settings file found at $SETTINGS_PATH"
else
    echo "Creating default settings.json..."
    mkdir -p "$PROJECT_ROOT/.vscode"
    # (Conteúdo mínimo se não existir, mas já sabemos que existe)
fi

echo ""
echo "=== Setup Complete ==="
echo "Please restart your editor (Reload Window) to apply changes."
echo "Make sure to open the folder: $PROJECT_ROOT (not the parent directory!)"

