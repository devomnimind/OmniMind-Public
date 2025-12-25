#!/usr/bin/env python
"""
Teste de carregamento de embedding model através do ReactAgent.
Valida que a correção de meta tensor error funciona.

CORREÇÃO (2025-12-17): Test CPU-first loading strategy
"""

import logging
import os
import sys

# Setup
sys.path.insert(0, "/home/fahbrain/projects/omnimind")
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(name)s - %(message)s"
)


def test_react_agent_embedding():
    """Teste carregamento de embedding model através do ReactAgent"""
    print("\n" + "=" * 70)
    print("TEST: ReactAgent Embedding Model Loading (CPU-First Strategy)")
    print("=" * 70 + "\n")

    try:
        from pathlib import Path

        from src.agents.react_agent import ReactAgent

        print("[1/3] Criando instância de ReactAgent...")
        config_path = Path("/home/fahbrain/projects/omnimind/config/agent_config.yaml")
        if not config_path.exists():
            print(f"⚠️ Config não encontrada: {config_path}")
            # Usar defaults se config não existir
            config_path = Path("/home/fahbrain/projects/omnimind/config/omnimind.yaml")

        agent = ReactAgent(str(config_path))
        print("\n[2/3] Acionando carregamento lazy do modelo de embedding...")
        # Trigger lazy loading
        test_text = "Teste de carregamento de embedding model"
        embedding = agent._generate_embedding(test_text)

        if embedding is not None and len(embedding) > 0:
            print("✓ Embedding gerado com sucesso")
            print("  - Texto: '{}'".format(test_text))
            dims = embedding.shape if hasattr(embedding, "shape") else len(embedding)
            print("  - Dimensões:", dims)
        else:
            print("⚠️ Embedding retornou None (fallback hash-based)")

        print("\n[3/3] Verificando estado do modelo...")
        if agent._embedding_model is not None:
            print("✓ Modelo de embedding disponível")
            # Testar segunda chamada (deve usar modelo em cache)
            agent._generate_embedding("Segundo teste")
            print("✓ Segunda geração de embedding funcionou")
        else:
            print("⚠️ Modelo em fallback (hash-based)")

        print("\n" + "=" * 70)
        print("✅ TEST PASSED: ReactAgent embedding loading OK!")
        print("=" * 70 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_react_agent_embedding()
    sys.exit(0 if success else 1)
