#!/usr/bin/env python3
"""
Diagnóstico de Dados de Consciência

Mostra:
1. Status das coleções Qdrant
2. Dados disponíveis no disco para população
3. Recomendações de próximos passos

Autor: Fabrício da Silva + Assistência IA
Data: 2025-12-12
Uso: python scripts/diagnose_consciousness_data.py
"""

import json
import sys
from pathlib import Path

import numpy as np


def diagnose_collections():
    """Diagnóstico das coleções Qdrant."""
    print("\n" + "=" * 70)
    print("📊 STATUS DAS COLEÇÕES QDRANT")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url="http://localhost:6333")

        collections_info = {
            "omnimind_embeddings": "Embeddings de projeto (indexação)",
            "omnimind_consciousness": "Estados de consciência avaliados",
            "omnimind_narratives": "Narrativas Lacanianas retroativas",
            "orchestrator_semantic_cache": "Padrões semânticos cacheados",
        }

        for collection_name, description in collections_info.items():
            try:
                info = client.get_collection(collection_name)
                points_count = info.points_count or 0
                status = "✅" if points_count > 0 else "⚠️"
                print(f"{status} {collection_name}")
                print(f"   └─ {description}")
                print(
                    f"      Vetores: {points_count} | "
                    f"Dimensão: {info.config.params.vectors.size}"  # type: ignore
                )
            except Exception as e:
                print(f"❌ {collection_name}")
                print(f"   └─ Erro: {e}")

    except Exception as e:
        print(f"❌ Não consegui conectar ao Qdrant: {e}")
        print("   Verifique se Qdrant está rodando em http://localhost:6333")


def diagnose_cycle_data():
    """Diagnóstico dos dados de ciclos disponíveis no disco."""
    print("\n" + "=" * 70)
    print("💾 DADOS DE CICLOS NO DISCO")
    print("=" * 70)

    cycles_dir = Path("data/reports/modules")

    if not cycles_dir.exists():
        print(f"⚠️ Diretório não encontrado: {cycles_dir}")
        return

    cycle_files = sorted(list(cycles_dir.glob("integration_loop_cycle_*.json")))
    print(f"✅ Encontrados {len(cycle_files)} ciclos de integração")

    if cycle_files:
        print(f"\n   Primeiro ciclo: {cycle_files[0].name}")
        print(f"   Último ciclo:  {cycle_files[-1].name}")

        # Analisar alguns ciclos para estatísticas
        print("\n   📊 Estatísticas de Métricas:")
        phi_values = []
        durations = []

        sample_size = min(100, len(cycle_files))
        for cycle_file in cycle_files[:sample_size]:
            try:
                with open(cycle_file) as f:
                    data = json.load(f)
                    metrics = data.get("metrics", {}).get("metrics", {})
                    phi = metrics.get("phi_estimate", {}).get("value")
                    duration = metrics.get("cycle_duration_ms", {}).get("value")

                    if phi is not None:
                        phi_values.append(float(phi))
                    if duration is not None:
                        durations.append(float(duration))
            except Exception:
                pass

        if phi_values:
            print(
                f"      φ (phi): min={min(phi_values):.3f}, "
                f"max={max(phi_values):.3f}, "
                f"μ={np.mean(phi_values):.3f}"
            )
        if durations:
            print(
                f"      Duração: min={min(durations):.1f}ms, "
                f"max={max(durations):.1f}ms, "
                f"μ={np.mean(durations):.1f}ms"
            )


def diagnose_recommendations():
    """Recomendações baseadas no status."""
    print("\n" + "=" * 70)
    print("🎯 RECOMENDAÇÕES")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url="http://localhost:6333")

        # Verificar status
        consciousness_empty = False
        narratives_empty = False
        embeddings_count = 0

        try:
            info = client.get_collection("omnimind_consciousness")
            consciousness_empty = info.points_count == 0
        except Exception:
            pass

        try:
            info = client.get_collection("omnimind_narratives")
            narratives_empty = info.points_count == 0
        except Exception:
            pass

        try:
            info = client.get_collection("omnimind_embeddings")
            embeddings_count = info.points_count or 0
        except Exception:
            pass

        # Recomendações
        if consciousness_empty:
            print("\n1️⃣ POPULATION DE CONSCIÊNCIA VAZIA")
            print("   Opção A: Usar dados sintéticos (rápido)")
            print("   $ python scripts/populate_consciousness_collections.py --quick")
            print("   └─ Resultado: ~30 vetores em ~30 segundos")
            print("\n   Opção B: Usar 4362+ ciclos reais (completo)")
            print("   $ python scripts/populate_from_real_cycles.py")
            print("   └─ Resultado: Todos os ciclos em ~2-3 minutos")

        if narratives_empty:
            print("\n2️⃣ NARRATIVAS VAZIAS")
            print("   Execute populate_consciousness_collections.py para popular")

        if embeddings_count > 0:
            print("\n3️⃣ INDEXAÇÃO DE PROJETO")
            print(f"   ✅ {embeddings_count} vetores de projeto já indexados")

    except Exception as e:
        print(f"⚠️ Não consegui gerar recomendações: {e}")


def main() -> int:
    """Função principal."""
    print("\n" + "🧠 DIAGNÓSTICO DE DADOS DE CONSCIÊNCIA (2025-12-12)")
    print("=" * 70)

    diagnose_collections()
    diagnose_cycle_data()
    diagnose_recommendations()

    print("\n" + "=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
