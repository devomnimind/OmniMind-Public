#!/usr/bin/env python3
"""
Script para Verificar Status das Coleções de Consciência

Fornece visão em tempo real de:
- Número de vetores em cada collection
- Dimensões
- Últimas atualizações
- Recomendações

Uso: python scripts/check_consciousness_collections.py
"""

import sys
from pathlib import Path
from typing import Optional

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from qdrant_client import QdrantClient
except ImportError:
    print("❌ Erro: qdrant-client não instalado. Use: pip install qdrant-client")
    sys.exit(1)


def format_size(points: int) -> str:
    """Formata número de pontos com cores e status."""
    if points == 0:
        return "❌ VAZIO (0 vetores)"
    elif points < 100:
        return f"⚠️  PEQUENO ({points} vetores)"
    elif points < 1000:
        return f"🟡 MÉDIO ({points} vetores)"
    else:
        return f"✅ GRANDE ({points} vetores)"


def get_collection_info(client: QdrantClient, collection_name: str) -> Optional[dict]:
    """Obtém informações de uma collection."""
    try:
        info = client.get_collection(collection_name)
        return {
            "name": collection_name,
            "points": info.points_count,
            "vector_size": info.config.params.vectors.size,
            "indexed": getattr(info, "indexed_vectors_count", None),
        }
    except Exception as e:
        return {
            "name": collection_name,
            "error": str(e),
        }


def print_header() -> None:
    """Imprime cabeçalho visual."""
    print("\n" + "=" * 80)
    print("🧠 STATUS DAS COLEÇÕES DE CONSCIÊNCIA")
    print("=" * 80)


def print_collection_status(info: dict) -> None:
    """Imprime status de uma collection."""
    if "error" in info:
        print(f"\n⚠️  {info['name']}")
        print(f"   Erro: {info['error']}")
        return

    print(f"\n📦 {info['name']}")
    print(f"   Vetores: {format_size(info['points'])}")
    print(f"   Dimensão: {info['vector_size']} dims")

    # Recomendações conforme estado
    if info["points"] == 0:
        print("   ℹ️  AÇÃO: Aguardando operações do sistema")
        if "narratives" in info["name"]:
            print("       → Execute consciência para gerar narrativas")
        elif "consciousness" in info["name"]:
            print("       → Execute ciclos de integração IIT")
        elif "cache" in info["name"]:
            print("       → Execute orquestrador para cachear padrões")


def main() -> int:
    """Função principal."""
    qdrant_url = "http://localhost:6333"

    print_header()

    try:
        client = QdrantClient(url=qdrant_url)
        print(f"\n✅ Conectado ao Qdrant: {qdrant_url}")
    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")
        print("   Verifique se Qdrant está rodando:")
        print("   docker-compose up -d qdrant")
        return 1

    # Collections a verificar
    collections = [
        ("omnimind_embeddings", "Embeddings do Projeto"),
        ("omnimind_consciousness", "Estados de Consciência"),
        ("omnimind_narratives", "Narrativas Lacanianas"),
        ("orchestrator_semantic_cache", "Cache Semântico"),
        ("omnimind_episodes", "Episódios"),
        ("omnimind_memories", "Memórias"),
    ]

    print("\n" + "-" * 80)

    total_vectors = 0
    for collection_name, display_name in collections:
        info = get_collection_info(client, collection_name)
        if info and "error" not in info:
            # Customizar nome para exibição
            info["display_name"] = display_name
            print(f"\n{display_name}")
            print_collection_status(info)
            total_vectors += info["points"]

    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80)
    print(f"   Total de vetores: {total_vectors}")

    # Recomendações
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Se omnimind_embeddings < 10k vetores:")
    print("      → Aguarde conclusão da indexação")
    print("      → Ou execute: scripts/index_project_files.py --full")
    print("")
    print("   2. Se omnimind_consciousness = 0:")
    print("      → Execute: python scripts/populate_consciousness_collections.py --quick")
    print("")
    print("   3. Se omnimind_narratives = 0:")
    print("      → Igual ao passo 2 (mesmo script popula todas as 3)")
    print("")
    print("   4. Se orchestrator_semantic_cache = 0:")
    print("      → Igual ao passo 2 (mesmo script popula todas as 3)")

    print("\n" + "=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
