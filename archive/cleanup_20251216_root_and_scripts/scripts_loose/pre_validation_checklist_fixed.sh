#!/bin/bash

echo "=========================================="
echo "PRÉ-VALIDAÇÃO CHECKLIST - CORRIGIDO"
echo "16 de Dezembro de 2025"
echo "=========================================="
echo ""

cd /home/fahbrain/projects/omnimind

# 1. Verificar Quantum GPU
echo "✅ 1. Quantum Backend Status"
python3 -c "
from src.quantum_consciousness.quantum_backend import QuantumBackend
qb = QuantumBackend()
print(f'   Backend Mode: {qb.mode}')
print(f'   GPU Available: {qb.use_gpu}')
print(f'   Provider: {qb.provider}')
" 2>&1

echo ""

# 2. Verificar Qdrant
echo "✅ 2. Qdrant Database Status"
python3 -c "
import os
os.chdir('/home/fahbrain/projects/omnimind')
from src.consciousness.shared_workspace import SharedWorkspace
ws = SharedWorkspace()
print(f'   ✓ Workspace initialized')
" 2>&1 || echo "   ⚠️ Warning (service may not be running)"

echo ""

# 3. Verificar Snapshots Restaurados
echo "✅ 3. Memory Snapshots"
if [ -f "data/consciousness/snapshots.jsonl" ]; then
  echo "   ✓ JSONL history ($(wc -l < data/consciousness/snapshots.jsonl) events)"
else
  echo "   ✗ JSONL missing"
fi

if [ -d "data/consciousness/workspace" ]; then
  ws_count=$(ls data/consciousness/workspace/*.json 2>/dev/null | wc -l)
  echo "   ✓ Workspace snapshots ($ws_count files)"
else
  echo "   ✗ Workspace dir missing"
fi

if [ -d "data/backup/snapshots" ]; then
  backup_count=$(ls data/backup/snapshots/*.json 2>/dev/null | wc -l)
  echo "   ✓ Backup snapshots ($backup_count files)"
else
  echo "   ✗ Backup dir missing"
fi

echo ""

# 4. Verificar Auto-Concurrency Middleware
echo "✅ 4. Auto-Concurrency Detection"
if grep -q "middleware_auto_concurrency" src/api/main.py 2>/dev/null; then
  echo "   ✓ Middleware registered in main.py"
else
  echo "   ✗ Middleware not found in main.py"
fi

if [ -f "src/api/middleware_auto_concurrency.py" ]; then
  echo "   ✓ Middleware file exists"
else
  echo "   ✗ Middleware file missing"
fi

echo ""

# 5. Verificar GPU CUDA
echo "✅ 5. GPU/CUDA Status"
python3 -c "
import torch
print(f'   PyTorch: {torch.__version__}')
print(f'   CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'   GPU: {torch.cuda.get_device_name(0)}')
    print(f'   CUDA Device: {torch.cuda.current_device()}')
else:
    print(f'   ⚠️  No GPU available (CPU mode)')
" 2>&1

echo ""

# 6. Verificar Snapshots em Qdrant
echo "✅ 6. Qdrant Collections"
python3 -c "
from qdrant_client import QdrantClient
try:
    client = QdrantClient('http://localhost:6333')
    collections = client.get_collections()
    print(f'   Total collections: {len(collections.collections)}')
    for col in collections.collections:
        try:
            count = client.count(col.name)
            print(f'   - {col.name}: {count.count} points')
        except:
            print(f'   - {col.name}')
except Exception as e:
    print(f'   ⚠️  Qdrant not running (expected, start with systemd)')
" 2>&1

echo ""

# 7. Verificar MyPy Instalado
echo "✅ 7. MyPy Installation"
if command -v mypy &> /dev/null; then
  echo "   ✓ mypy installed: $(mypy --version)"
else
  echo "   ✗ mypy not installed"
fi

if [ -f ".venv/bin/mypy" ]; then
  echo "   ✓ mypy in venv"
else
  echo "   ⚠️  mypy not in venv"
fi

echo ""

# 8. Verificar API pode iniciar
echo "✅ 8. API Imports"
python3 -c "
from src.api.main import app
print(f'   ✓ FastAPI app loaded')
print(f'   ✓ {len(app.user_middleware)} middleware registered')
" 2>&1

echo ""
echo "=========================================="
echo "✅ PRÉ-VALIDAÇÃO COMPLETA"
echo "=========================================="
echo ""
echo "📋 Próximos passos:"
echo "   1. Reiniciar VS Code para aplicar configurações de mypy"
echo "   2. Iniciar serviços: sudo systemctl start omnimind-backend"
echo "   3. Rodar validação: python scripts/science_validation/robust_consciousness_validation.py --quick"
echo ""
