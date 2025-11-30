#!/bin/bash
# Force VS Code to use the correct Python environment

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PYTHONPATH="/home/fahbrain/projects/omnimind/src"
export VIRTUAL_ENV="/home/fahbrain/projects/omnimind/.venv"
export PATH="/home/fahbrain/projects/omnimind/.venv/bin:$PATH"

# Force Python interpreter
export PYTHON_INTERPRETER="/home/fahbrain/projects/omnimind/.venv/bin/python"

echo "✅ OmniMind Python Environment Activated"
echo "Python: $(python --version)"
echo "Path: $(which python)"
echo "Virtual Env: $VIRTUAL_ENV"