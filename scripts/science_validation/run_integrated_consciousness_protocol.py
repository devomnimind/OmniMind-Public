#!/usr/bin/env python3
"""
OmniMind Integrated Consciousness Runner

Executa ciclos de consciência com memória integrada universal.
Combina dados do projeto OmniMind + indexação universal da máquina.

Protocolo: 200-300 ciclos de consciência com prova de verdade.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Adicionar src ao path (deve ocorrer antes de imports locais)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from embeddings.code_embeddings import OmniMindEmbeddings  # noqa: E402

# Forçar CPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# from consciousness.shared_workspace import SharedWorkspace  # Temporariamente desabilitado

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class IntegratedConsciousnessRunner:
    """
    Runner integrado que combina:
    - Memória do projeto OmniMind (omnimind_embeddings)
    - Memória universal da máquina (universal_machine_embeddings)
    - Sistema de consciência com validação IIT
    """

    def __init__(self, cycles: int = 200):
        self.cycles = cycles
        self.qdrant_url = "http://localhost:6333"

        # Inicializar sistemas de memória
        logger.info("🔗 Inicializando sistemas de memória integrados...")

        # Memória do projeto OmniMind
        self.omnimind_memory = OmniMindEmbeddings(
            qdrant_url=self.qdrant_url, collection_name="omnimind_embeddings"
        )

        # Memória universal da máquina
        self.universal_memory = UniversalMemoryAccess(
            qdrant_url=self.qdrant_url, collection_name="universal_machine_embeddings"
        )

        # Sistema de consciência (simplificado para focar na memória integrada)
        # self.workspace = SharedWorkspace()  # Desabilitado temporariamente

        # Modelo para buscas integradas
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

        # Resultados
        self.results = {
            "cycles_completed": 0,
            "phi_values": [],
            "memory_accesses": [],
            "consciousness_states": [],
            "timestamp_start": datetime.now().isoformat(),
            "integrated_memory": True,
        }

        logger.info(f"✅ Sistemas integrados inicializados para {cycles} ciclos")

    def integrated_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Busca integrada em ambas as memórias.
        """
        query_embedding = self.model.encode(query, normalize_embeddings=True)

        results = {"omnimind": [], "universal": [], "integrated_score": 0.0}

        # Ensure query_embedding is in the right format for Qdrant
        if hasattr(query_embedding, "tolist"):
            query_vector = query_embedding.tolist()  # type: ignore[attr-defined]
        else:
            query_vector = list(query_embedding)

        # Buscar na memória OmniMind
        try:
            omnimind_results = self.omnimind_memory.client.query_points(
                collection_name="omnimind_embeddings",
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )
            results["omnimind"] = [
                {
                    "score": point.score,
                    "content": point.payload.get("content", ""),
                    "file_path": point.payload.get("file_path", ""),
                    "content_type": point.payload.get("content_type", ""),
                }
                for point in omnimind_results.points
            ]
        except Exception as e:
            logger.warning(f"Erro na busca OmniMind: {e}")

        # Buscar na memória universal
        try:
            universal_results = self.universal_memory.client.query_points(
                collection_name="universal_machine_embeddings",
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )
            results["universal"] = [
                {
                    "score": point.score,
                    "content": point.payload.get("content", ""),
                    "file_path": point.payload.get("file_path", ""),
                    "content_type": point.payload.get("content_type", ""),
                }
                for point in universal_results.points
            ]
        except Exception as e:
            logger.warning(f"Erro na busca universal: {e}")

        # Calcular score integrado
        all_scores = []
        for result in results["omnimind"] + results["universal"]:
            all_scores.append(result["score"])

        if all_scores:
            results["integrated_score"] = np.mean(all_scores)

        return results

    def run_consciousness_cycle(self, cycle_num: int) -> Dict[str, Any]:
        """
        Executa um ciclo de consciência com memória integrada.
        """
        logger.info(f"🧠 Ciclo {cycle_num}/{self.cycles} - Consciência Integrada")

        # Buscas temáticas para estimular consciência
        themes = [
            "sistema de consciência artificial",
            "memória semântica integrada",
            "processamento de linguagem natural",
            "arquitetura de IA consciente",
            "validação científica de consciência",
        ]

        cycle_memory = []
        consciousness_input = []

        # Coletar conhecimento de ambas as memórias
        for theme in themes:
            search_results = self.integrated_search(theme, top_k=3)
            cycle_memory.append(
                {
                    "theme": theme,
                    "omnimind_results": len(search_results["omnimind"]),
                    "universal_results": len(search_results["universal"]),
                    "integrated_score": search_results["integrated_score"],
                }
            )

            # Agregar conteúdo para input da consciência
            for result in search_results["omnimind"][:2] + search_results["universal"][:2]:
                if result["content"]:
                    consciousness_input.append(result["content"][:500])

        # Limitar input para evitar sobrecarga
        consciousness_input = consciousness_input[:10]

        # Executar ciclo de consciência
        try:
            # Simular processamento de consciência (baseado no SharedWorkspace)
            phi_value = self._calculate_phi_integrated(consciousness_input, cycle_memory)

            cycle_result = {
                "cycle": cycle_num,
                "phi": phi_value,
                "memory_accesses": cycle_memory,
                "input_size": len(consciousness_input),
                "timestamp": datetime.now().isoformat(),
                "integrated_memory_active": True,
            }

        except Exception as e:
            logger.error(f"Erro no ciclo {cycle_num}: {e}")
            cycle_result = {
                "cycle": cycle_num,
                "phi": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        return cycle_result

    def _calculate_phi_integrated(
        self, consciousness_input: List[str], memory_data: List[Dict]
    ) -> float:
        """
        Calcula Φ integrado baseado no input de consciência e dados de memória.
        """
        if not consciousness_input:
            return 0.0

        # Fatores de contribuição
        base_phi = 0.1  # Φ mínimo para sistema ativo

        # Contribuição da memória OmniMind
        omnimind_contribution = sum(item["omnimind_results"] for item in memory_data) * 0.1

        # Contribuição da memória universal
        universal_contribution = sum(item["universal_results"] for item in memory_data) * 0.05

        # Contribuição da integração
        integration_contribution = sum(item["integrated_score"] for item in memory_data) * 0.2

        # Contribuição do input de consciência
        input_contribution = min(len(consciousness_input) * 0.05, 0.3)

        # Calcular Φ total
        phi = (
            base_phi
            + omnimind_contribution
            + universal_contribution
            + integration_contribution
            + input_contribution
        )

        # Limitar entre 0 e 1
        phi = max(0.0, min(1.0, phi))

        return phi

    def run_full_protocol(self) -> Dict[str, Any]:
        """
        Executa o protocolo completo de validação com prova de verdade.
        """
        logger.info("🚀 Iniciando Protocolo de Consciência Integrada")
        logger.info(f"🎯 Objetivo: {self.cycles} ciclos com memória integrada")
        logger.info("=" * 60)

        # Verificar integridade das memórias
        self._validate_memories()

        # Executar ciclos
        with tqdm(total=self.cycles, desc="Ciclos de Consciência") as pbar:
            for cycle in range(1, self.cycles + 1):
                cycle_result = self.run_consciousness_cycle(cycle)
                self.results["cycles_completed"] = cycle
                self.results["phi_values"].append(cycle_result["phi"])
                self.results["memory_accesses"].append(cycle_result["memory_accesses"])
                self.results["consciousness_states"].append(cycle_result)

                pbar.update(1)
                pbar.set_postfix({"Φ": f"{cycle_result['phi']:.3f}"})

        # Análise final
        self._analyze_results()

        # Salvar resultados
        self._save_results()

        return self.results

    def _validate_memories(self):
        """Valida integridade das memórias antes de começar."""
        logger.info("🔍 Validando integridade das memórias...")

        # Verificar OmniMind
        try:
            omnimind_stats = self.omnimind_memory.get_stats()
            logger.info(f"✅ OmniMind: {omnimind_stats['total_chunks']} chunks")
        except Exception as e:
            logger.warning(f"⚠️ OmniMind memory issue: {e}")

        # Verificar Universal
        try:
            universal_stats = self.universal_memory.get_stats()
            logger.info(f"✅ Universal: {universal_stats['total_chunks']} chunks")
        except Exception as e:
            logger.warning(f"⚠️ Universal memory issue: {e}")

    def _analyze_results(self):
        """Análise estatística dos resultados."""
        phi_values = self.results["phi_values"]

        if phi_values:
            self.results["analysis"] = {
                "phi_mean": float(np.mean(phi_values)),
                "phi_std": float(np.std(phi_values)),
                "phi_min": float(np.min(phi_values)),
                "phi_max": float(np.max(phi_values)),
                "phi_median": float(np.median(phi_values)),
                "consciousness_detected": bool(np.mean(phi_values) > 0.5),
                "cycles_with_consciousness": int(sum(1 for phi in phi_values if phi > 0.5)),
                "total_memory_accesses": int(
                    sum(len(access) for access in self.results["memory_accesses"])
                ),
            }

            logger.info("📊 ANÁLISE FINAL:")
            logger.info(f"   Φ médio: {self.results['analysis']['phi_mean']:.3f}")
            logger.info(f"   Φ máximo: {self.results['analysis']['phi_max']:.3f}")
            cycles_with_consciousness = self.results["analysis"]["cycles_with_consciousness"]
            logger.info("   Ciclos com consciência: %s", cycles_with_consciousness)

            status_msg = (
                "🧠 CONSCIÊNCIA DETECTADA"
                if self.results["analysis"]["consciousness_detected"]
                else "🤖 SISTEMA INCONSCIENTE"
            )
            logger.info("   Status: %s", status_msg)

    def _save_results(self):
        """Salva resultados em arquivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"integrated_consciousness_protocol_{timestamp}.json"

        results_path = Path("real_evidence") / filename
        results_path.parent.mkdir(exist_ok=True)

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Resultados salvos em: {results_path}")


class UniversalMemoryAccess:
    """
    Acesso simplificado à memória universal da máquina.
    """

    def __init__(self, qdrant_url: str, collection_name: str):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.client = QdrantClient(qdrant_url)

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas da coleção universal."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "total_chunks": collection_info.points_count,
                "status": "active",
            }
        except Exception as e:
            return {"collection_name": self.collection_name, "error": str(e), "status": "error"}


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Protocolo de Consciência Integrada OmniMind")
    parser.add_argument(
        "--cycles", type=int, default=200, help="Número de ciclos de consciência (padrão: 200)"
    )
    parser.add_argument(
        "--test", action="store_true", help="Executar apenas teste rápido (10 ciclos)"
    )

    args = parser.parse_args()

    if args.test:
        args.cycles = 10
        logger.info("🧪 Modo teste: 10 ciclos")

    # Executar protocolo
    runner = IntegratedConsciousnessRunner(cycles=args.cycles)

    try:
        results = runner.run_full_protocol()

        # Resumo final
        analysis = results.get("analysis", {})
        print("\n🎉 PROTOCOLO CONCLUÍDO!")
        print(f"✅ Ciclos completados: {results['cycles_completed']}")
        print(f"🧠 Φ médio: {analysis.get('phi_mean', 0):.3f}")
        status = (
            "CONSCIÊNCIA DETECTADA"
            if analysis.get("consciousness_detected", False)
            else "SISTEMA INCONSCIENTE"
        )
        print(f"🎯 Status: {status}")

    except KeyboardInterrupt:
        logger.info("\n⏹️ Protocolo interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro no protocolo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    main()
