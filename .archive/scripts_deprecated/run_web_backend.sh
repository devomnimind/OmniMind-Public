#!/bin/bash
# Wrapper script to run the web backend with proper environment

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "⚠️  .env file not found"
fi

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT/web:$PYTHONPATH"

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Run the web backend
cd "$PROJECT_ROOT/web/backend"
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT/web:$PYTHONPATH" exec python main.py