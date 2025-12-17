#!/usr/bin/env python3
"""
Verificador offline de modelos HuggingFace - OmniMind
Testa se os modelos estão acessíveis sem internet.
"""

import os
from pathlib import Path

# Force offline mode ANTES de qualquer import de transformers
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

# Encontrar cache
cache_home = Path.home() / ".cache" / "huggingface" / "hub"
model_dir = cache_home / "models--sentence-transformers--all-MiniLM-L6-v2"

print("🔍 Verificando modelos offline...")
print(f"   Cache dir: {cache_home}")
print(f"   Model dir: {model_dir}")
print(f"   Existe: {model_dir.exists()}")

if model_dir.exists():
    snapshots = list((model_dir / "snapshots").glob("*"))
    if snapshots:
        snapshot = snapshots[0]
        print(f"   Snapshot: {snapshot.name}")

        # Listar arquivos
        files = list(snapshot.glob("*"))
        print(f"   Arquivos: {len(files)}")
        for f in sorted(files)[:5]:
            print(f"      - {f.name}")

        # Tentar carregar
        print("\n🧪 Tentando carregar modelo...")
        try:
            from sentence_transformers import SentenceTransformer

            # Usar o caminho do snapshot diretamente
            model = SentenceTransformer(
                str(snapshot), local_files_only=True, trust_remote_code=False, device="cpu"
            )

            print("✅ Modelo carregado com sucesso!")

            # Teste rápido
            text = "This is a test."
            embedding = model.encode(text)
            print(f"✅ Embedding gerado: dimensão {len(embedding)}")
            print(f"✅ Primeiras 5 dimensões: {embedding[:5]}")

        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
            import traceback

            traceback.print_exc()
else:
    print("❌ Modelo não encontrado em cache")
    print("   Download: huggingface-cli download sentence-transformers/all-MiniLM-L6-v2")
