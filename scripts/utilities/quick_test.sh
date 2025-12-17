#!/bin/bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

export PYTORCH_DISABLE_DYNAMO=1
export PYTHONUNBUFFERED=1

echo "1️⃣ Teste de sintaxe..."
python3 -m py_compile src/embeddings/code_embeddings.py 2>&1 | head -20 && echo "✅ Sintaxe OK" || echo "❌ Erro de sintaxe"

echo ""
echo "2️⃣ Teste de import rápido..."
timeout 8 python3 -c "
import sys
sys.path.insert(0, 'src')
print('Importing...')
from embeddings.code_embeddings import OmniMindEmbeddings
print('✅ Import OK')
emb = OmniMindEmbeddings()
print('✅ Instanciação OK')
" 2>&1 | head -30

echo ""
echo "Done!"
