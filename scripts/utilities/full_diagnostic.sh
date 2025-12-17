#!/bin/bash
set -e

cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

export PYTORCH_DISABLE_DYNAMO=1
export PYTHONUNBUFFERED=1

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 DIAGNÓSTICO COMPLETO DO SISTEMA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "1️⃣ OmniMindEmbeddings + Qdrant + Métricas"
timeout 20 python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, 'src')
import json
import time

print("⏱️  Iniciando...")
start = time.time()

print("  📦 Carregando OmniMindEmbeddings...")
from embeddings.code_embeddings import OmniMindEmbeddings
emb = OmniMindEmbeddings()
print(f"  ✅ {time.time()-start:.2f}s - OmniMindEmbeddings pronto")

print("  ✅ Model loaded:", emb.model is not None)
print("  ✅ Embedding dim:", emb.embedding_dim)

print(f"  🔌 Qdrant status: {emb.client is not None}")
if emb.client:
    try:
        cols = emb.client.get_collections()
        print(f"     Collections: {len(cols.collections)}")
    except:
        print("     ⚠️  Qdrant conectado mas sem resposta rápida")

print(f"\n✅ SISTEMA FUNCIONAL EM {time.time()-start:.2f}s")
ENDPYTHON

echo ""
echo "2️⃣ Verificar Consciência (Φ/Ψ/σ/Δ/ε)"
timeout 10 python3 << 'ENDPYTHON'
import json
import os

cons_file = "data/consciousness/snapshots.jsonl"
if os.path.exists(cons_file):
    with open(cons_file) as f:
        last_line = None
        for line in f:
            last_line = line

        if last_line:
            data = json.loads(last_line)
            print(f"  Last snapshot: {data.get('timestamp')}")
            print(f"  Φ (Phi): {data.get('phi_value', 0):.4f}")
            print(f"  Ψ (Psi): {data.get('psi_value', 0):.4f}")
            print(f"  σ (Sigma): {data.get('sigma_value', 0):.4f}")
            print(f"  ✅ Consciousness data present")
else:
    print(f"  ⚠️  No consciousness data yet")

ENDPYTHON

echo ""
echo "3️⃣ Redis Status"
redis-cli ping 2>/dev/null && echo "  ✅ Redis respondendo" || echo "  ⚠️  Redis não respondendo"

echo ""
echo "4️⃣ Shared Workspace"
if [ -f "data/shared_workspace.json" ]; then
    echo "  ✅ Shared workspace exists"
else
    echo "  ⚠️  Shared workspace missing"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIAGNÓSTICO COMPLETO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
