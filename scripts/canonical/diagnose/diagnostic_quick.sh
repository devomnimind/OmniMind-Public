#!/bin/bash
echo "=== OmniMind Diagnostic ==="
echo "1. Python + Dependencies"
python --version
pip list | grep -E "qiskit|torch|fastapi|pydantic"

echo "2. GPU Status"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv

echo "3. Services Status"
lsof -i :3000 && echo "Frontend: UP" || echo "Frontend: DOWN"
lsof -i :8000 && echo "Backend: UP" || echo "Backend: DOWN"
lsof -i :11434 && echo "Ollama: UP" || echo "Ollama: DOWN"

echo "4. Git Status"
git status --short | head -10

echo "5. Test Suite Quick Check"
python -m pytest tests/ -x -q --tb=line 2>&1 | head -20
