#!/bin/bash
# Safe test runner - disables aggressive monitoring

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

# Source environment to disable monitors
export $(cat .env.no_monitors | grep -v '^#' | xargs)

# Activate venv
source .venv/bin/activate 2>/dev/null || true

# Run the provided command
exec "$@"
