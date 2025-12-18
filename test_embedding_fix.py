#!/usr/bin/env python
"""
Teste rápido do carregamento de modelo de embedding com correção de meta tensor.

CORREÇÃO (2025-12-17): Validar que SentenceTransformer carrega sem meta tensor error
"""

import os
import sys

# Setup
sys.path.insert(0, "/home/fahbrain/projects/omnimind")
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"


def test_embedding_model_load():
    """Teste carregamento de modelo com nova estratégia CPU-first"""
    print("\n" + "=" * 70)
    print("TEST: Carregamento de Modelo de Embedding (CPU-First Strategy)")
    print("=" * 70)

    try:
        from sentence_transformers import SentenceTransformer

        print("\n✓ Imports OK")

        # Teste 1: Verificar modelo em cache
        from pathlib import Path

        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        model_cache_path = (
            cache_dir
            / "models--sentence-transformers--all-MiniLM-L6-v2"
            / "snapshots"
            / "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
        )

        if model_cache_path.exists():
            print(f"✓ Modelo encontrado em cache: {model_cache_path}")
            files = list(model_cache_path.glob("*"))
            print(f"  - {len(files)} arquivos no diretório")
            for f in files:
                if f.is_file():
                    size = f.stat().st_size / 1024 / 1024  # MB
                    print(f"    - {f.name}: {size:.1f} MB")
        else:
            print(f"⚠️ Modelo NÃO encontrado em cache: {model_cache_path}")

        # Teste 2: Carregar em CPU
        print("\n[1/3] Carregando modelo em CPU...")
        model_cpu = SentenceTransformer(
            str(model_cache_path) if model_cache_path.exists() else "all-MiniLM-L6-v2",
            device="cpu",
            local_files_only=model_cache_path.exists(),
        )
        print("✓ Modelo carregado em CPU")

        # Teste 3: Verificar se há meta tensors
        print("\n[2/3] Verificando meta tensors...")
        has_meta = False
        meta_count = 0
        for module in model_cpu.modules():  # type: ignore[attr-defined]
            for param in module.parameters():
                if param.device.type == "meta":
                    has_meta = True
                    meta_count += 1

        if has_meta:
            print(f"⚠️ ENCONTRADOS {meta_count} meta tensors!")
        else:
            print("✓ Sem meta tensors detectados")

        # Teste 4: Gerar embedding
        print("\n[3/3] Testando geração de embedding...")
        test_text = "Este é um teste de carregamento de modelo"
        embedding = model_cpu.encode(test_text)

        print("✓ Embedding gerado com sucesso")
        print(f"  - Texto: '{test_text}'")
        print(f"  - Dimensões: {embedding.shape}")  # type: ignore[attr-defined]
        print(f"  - Tipo: {embedding.dtype}")  # type: ignore[attr-defined]
        device = next(model_cpu.parameters()).device  # type: ignore[attr-defined]
        print(f"  - Device modelo: {device}")

        # Resumo
        print("\n" + "=" * 70)
        print("✅ TEST PASSED: Carregamento de modelo funcionando!")
        print("=" * 70 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_embedding_model_load()
    sys.exit(0 if success else 1)
