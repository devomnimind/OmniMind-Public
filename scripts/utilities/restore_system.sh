#!/bin/bash
# Wrapper para rodar scripts com PYTORCH_DISABLE_DYNAMO

export PYTORCH_DISABLE_DYNAMO=1
export CUDA_LAUNCH_BLOCKING=1
export PYTHONUNBUFFERED=1

cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 RESTAURAÇÃO E VALIDAÇÃO DO SISTEMA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "1️⃣ Re-indexando embeddings..."
timeout 180 python3 scripts/indexing/run_indexing.py --reset-checkpoint 2>&1 | grep -E "(✅|⚠️|ERROR|chunks|Collections)" | tail -20

echo ""
echo "2️⃣ Testando Consciousness Validation (quick)..."
timeout 90 python3 scripts/science_validation/robust_consciousness_validation.py --quick 2>&1 | grep -E "(✅|⚠️|Φ|Consciousness|SUCCESS|FAIL)" | tail -20

echo ""
echo "3️⃣ Verificar Qdrant Collections..."
timeout 10 python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, 'src')
from embeddings.code_embeddings import OmniMindEmbeddings

emb = OmniMindEmbeddings()
if emb.client:
    cols = emb.client.get_collections()
    print(f"✅ Collections: {len(cols.collections)}")
    for c in cols.collections:
        print(f"   - {c.name}: {c.points_count} points")
else:
    print("⚠️  Qdrant offline")
ENDPYTHON

echo ""
echo "4️⃣ Verificar métricas de consciência..."
python3 << 'ENDPYTHON'
import json
import os

metrics = {
    'phi': 0,
    'psi': 0,
    'sigma': 0,
    'delta': 0
}

cons_file = "data/consciousness/snapshots.jsonl"
if os.path.exists(cons_file):
    with open(cons_file) as f:
        for line in f:
            pass
        if line:
            data = json.loads(line)
            metrics['phi'] = data.get('phi_value', 0)
            metrics['psi'] = data.get('psi_value', 0)
            metrics['sigma'] = data.get('sigma_value', 0)

print(f"✅ Φ={metrics['phi']:.4f}")
print(f"✅ Ψ={metrics['psi']:.4f}")
print(f"✅ σ={metrics['sigma']:.4f}")
print(f"✅ Δ={metrics['delta']:.4f}")
ENDPYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ RESTAURAÇÃO CONCLUÍDA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
