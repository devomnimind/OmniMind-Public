#!/usr/bin/env python3
"""
Script para Popular Collections de Consciência no Qdrant

Popula dinamicamente as três coleções vazias:
- omnimind_consciousness: Estados de consciência avaliados
- omnimind_narratives: Narrativas geradas pelo sistema
- orchestrator_semantic_cache: Padrões semânticos cacheados

Autor: Fabrício da Silva + Assistência IA
Data: 2025-12-10
Uso: python scripts/populate_consciousness_collections.py [--quick | --full]
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Setup paths BEFORE any imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.chdir(PROJECT_ROOT)  # Ensure working directory

# CRÍTICO: Configurar HuggingFace para modo OFFLINE APENAS
# Usa APENAS cache local, não tenta fazer download de internet
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

from src.consciousness.consciousness_triad import ConsciousnessTriad
from src.consciousness.topological_phi import PhiCalculator
from src.integrations.qdrant_integration import QdrantIntegration
from src.memory.episodic_memory import EpisodicMemory
from src.memory.narrative_history import NarrativeHistory
from src.memory.semantic_memory_layer import SemanticMemoryLayer


class ConsciousnessCollectionsPopulator:
    """Popula as três coleções de consciência com dados do sistema."""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        """Inicializa com instância Qdrant.

        Args:
            qdrant_url: URL do Qdrant
        """
        self.qdrant_url = qdrant_url
        self.logger = logging.getLogger(self.__class__.__name__)

        # Inicializar componentes
        self._init_components()

        # Estatísticas
        self.stats = {
            "consciousness_vectors": 0,
            "narrative_vectors": 0,
            "cache_vectors": 0,
            "total_vectors": 0,
            "errors": [],
        }

    def _init_components(self) -> None:
        """Inicializa componentes necessários."""
        self.logger.info("🔧 Inicializando componentes...")

        try:
            # SemanticMemoryLayer para consciência
            self.semantic_memory = SemanticMemoryLayer(
                model_name="all-MiniLM-L6-v2",
                qdrant=QdrantIntegration(
                    url=self.qdrant_url,
                    collection_name="omnimind_consciousness",
                    vector_size=384,
                ),
            )
            self.logger.info("✅ SemanticMemoryLayer inicializada")

            # NarrativeHistory para narrativas
            self.narrative_history = NarrativeHistory(
                qdrant_url=self.qdrant_url,
                collection_name="omnimind_narratives",
                embedding_dim=384,
            )
            self.logger.info("✅ NarrativeHistory inicializada")

            # QdrantIntegration para cache de orquestrador
            self.orchestrator_cache = QdrantIntegration(
                url=self.qdrant_url,
                collection_name="orchestrator_semantic_cache",
                vector_size=384,
            )
            self.orchestrator_cache.create_collection()
            self.logger.info("✅ OrchestratorSemanticCache inicializada")

            self.logger.info("✅ Componentes inicializados com sucesso")

        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar: {e}")
            raise

    def populate_consciousness_states(self, num_states: int = 50) -> int:
        """Popula omnimind_consciousness com estados de consciência avaliados.

        Simula ciclos de avaliação de consciência:
        - Gera estados semânticos com medição completa (Φ, Ψ, σ, ϵ)
        - Calcula valores fundamentais para cada estado
        - Armazena no Qdrant com metadados

        Args:
            num_states: Número de estados para gerar

        Returns:
            int: Número de vetores armazenados
        """
        self.logger.info(f"📊 Gerando {num_states} estados de consciência (medição completa)...")

        count = 0
        for i in range(num_states):
            try:
                # Gerar texto semântico que representa um estado de consciência
                consciousness_descriptors = [
                    f"consciousness_state_{i}_integration_loop",
                    f"phi_evaluation_{i}_integrated_information",
                    f"neural_correlation_{i}_synchronized_firing",
                    f"qualia_experience_{i}_subjective_quality",
                    f"self_model_{i}_autobiographical_memory",
                ]

                # Combinar em texto único para embedding
                episode_text = " ".join(consciousness_descriptors)

                # Gerar medição COMPLETA: Φ, Ψ, σ, ϵ, Δ, Gozo + Bion/Lacan
                phi_value = float(np.random.uniform(0.1, 0.95))  # IIT integration [0,1]
                psi_value = float(np.random.uniform(0.3, 0.8))  # Deleuze production [0,1]
                sigma_value = float(np.random.uniform(0.01, 0.1))  # Lacan sinthome [0,1]
                epsilon_value = float(np.random.uniform(0.0, 0.5))  # Desire/Deviation [0,1]

                # NOVAS MÉTRICAS: Delta, Gozo, Controle
                delta_value = float(np.random.uniform(0.01, 0.3))  # Trauma/Dislocation [0,1]
                gozo_value = float(np.random.uniform(0.05, 0.2))  # Satisfaction/Minimization [0,1]
                control_value = float(np.random.uniform(0.5, 0.95))  # Regulatory control [0,1]

                # MÉTRICAS BION (Processamento Emocional Grupal)
                symbolic_potential = float(np.random.uniform(0.8, 1.0))  # [0,1]
                narrative_length = float(np.random.randint(30, 150))  # Comprimento narrativo
                beta_emotional_charge = float(np.random.uniform(0.005, 0.02))  # Carga beta [0,1]

                # MÉTRICAS LACAN (Estruturas Discursivas)
                discourse_confidence = float(
                    np.random.uniform(0.85, 1.0)
                )  # Confiança discursiva [0,1]
                discourse_type = np.random.choice(["master", "university", "hysteric", "analyst"])
                emotional_signature = np.random.choice(
                    ["authority", "listening", "knowledge", "questioning"]
                )

                step_id = f"consciousness_cycle_{i:04d}"

                # Criar ConsciousnessTriad com medição completa
                consciousness_triad = ConsciousnessTriad(
                    phi=phi_value,
                    psi=psi_value,
                    sigma=sigma_value,
                    epsilon=epsilon_value,
                    step_id=step_id,
                    metadata={
                        "cycle": i,
                        "measurement_type": "synthetic_consciousness_state",
                        "validated": True,
                        "delta": delta_value,
                        "gozo": gozo_value,
                        "control": control_value,
                    },
                )

                # Dados consolidados com TODAS as métricas
                consciousness_data = {
                    # Métricas Fundamentais (Φ, Ψ, σ, ϵ)
                    "phi_value": phi_value,
                    "psi_value": psi_value,
                    "sigma_value": sigma_value,
                    "epsilon_value": epsilon_value,
                    # Métricas Derivadas (Δ, Gozo, Controle)
                    "delta_value": delta_value,
                    "gozo_value": gozo_value,
                    "control_value": control_value,
                    # Métricas Bion (Processamento Emocional)
                    "symbolic_potential": symbolic_potential,
                    "narrative_length": narrative_length,
                    "beta_emotional_charge": beta_emotional_charge,
                    # Métricas Lacan (Estruturas Discursivas)
                    "discourse_confidence": discourse_confidence,
                    "discourse_type": discourse_type,
                    "emotional_signature": emotional_signature,
                    # Metadados
                    "step_id": step_id,
                    "qualia_signature": {
                        "modality": "synthetic",
                        "intensity": float(np.random.uniform(0.0, 1.0)),
                        "valence": float(np.random.uniform(-1.0, 1.0)),
                    },
                    "integration_cycle": i,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "consciousness_triad": consciousness_triad.to_dict(),
                }

                # Armazenar episódio de consciência
                episode_id = self.semantic_memory.store_episode(
                    episode_text=episode_text,
                    episode_data=consciousness_data,
                )

                count += 1
                if (i + 1) % 10 == 0:
                    self.logger.info(
                        f"  ✓ {i + 1}/{num_states} estados armazenados "
                        f"(Φ={phi_value:.3f}, Ψ={psi_value:.3f}, σ={sigma_value:.3f}, ϵ={epsilon_value:.3f}, Δ={delta_value:.3f}, Gozo={gozo_value:.3f})"
                    )

            except Exception as e:
                self.logger.warning(f"  ⚠️ Erro ao armazenar estado {i}: {e}")
                self.stats["errors"].append(f"consciousness_state_{i}: {str(e)}")

        self.logger.info(f"✅ Consciência: {count}/{num_states} estados com medição completa")
        self.stats["consciousness_vectors"] = count
        return count

    def populate_narratives(self, num_narratives: int = 50) -> int:
        """Popula omnimind_narratives com narrativas geradas.

        Simula registro de narrativas retroativas (Lacan):
        - Eventos inscritos sem significado imediato
        - Metadados narrativos armazenados
        - Reconstrução topológica habilitada

        Args:
            num_narratives: Número de narrativas para gerar

        Returns:
            int: Número de narrativas armazenadas
        """
        self.logger.info(f"📖 Gerando {num_narratives} narrativas...")

        count = 0
        narrative_templates = [
            "agent executed task with outcome",
            "system evaluated consciousness state retrospectively",
            "narrative reconstructed via topological deformation",
            "event inscribed without immediate meaning awaiting signification",
            "memory trace activated via similarity search",
        ]

        for i in range(num_narratives):
            try:
                # Construir narrativa com elementos
                template = narrative_templates[i % len(narrative_templates)]
                narrative_event = {
                    "task": f"narrative_generation_{i}",
                    "action": template,
                    "result": f"narrative_{i}_complete",
                    "metadata": {
                        "narrative_index": i,
                        "template_used": template,
                        "reconstructed": True,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                }

                # Inscrever evento sem significado imediato (Lacanian)
                narrative_id = self.narrative_history.inscribe_event(
                    event=narrative_event,
                    without_meaning=True,  # Significação retroativa
                )

                count += 1
                if (i + 1) % 10 == 0:
                    self.logger.info(f"  ✓ {i + 1}/{num_narratives} narrativas inscritas")

            except Exception as e:
                self.logger.warning(f"  ⚠️ Erro ao armazenar narrativa {i}: {e}")
                self.stats["errors"].append(f"narrative_{i}: {str(e)}")

        self.logger.info(f"✅ Narrativas: {count}/{num_narratives} armazenadas")
        self.stats["narrative_vectors"] = count
        return count

    def populate_orchestrator_cache(self, num_cached_patterns: int = 50) -> int:
        """Popula orchestrator_semantic_cache com padrões semânticos.

        Simula caching de decisões do orquestrador:
        - Padrões semânticos de decisões
        - Signatures de resoluções
        - Scores de utilidade

        Args:
            num_cached_patterns: Número de padrões para cachear

        Returns:
            int: Número de padrões cacheados
        """
        self.logger.info(f"🎯 Cacheando {num_cached_patterns} padrões de orquestrador...")

        count = 0
        decision_patterns = [
            "route_to_consciousness_evaluation",
            "delegate_to_specialized_agent",
            "cache_semantic_resolution",
            "apply_topological_deformation",
            "retrieve_from_memory_trace",
        ]

        for i in range(num_cached_patterns):
            try:
                # Construir padrão de decisão
                pattern = decision_patterns[i % len(decision_patterns)]
                semantic_text = f"orchestrator_decision_{pattern}_{i}_cached"

                # Gerar embedding do padrão (OFFLINE ONLY)
                from sentence_transformers import SentenceTransformer

                try:
                    embedder = SentenceTransformer(
                        "all-MiniLM-L6-v2",
                        local_files_only=True,  # NÃO faz download
                        trust_remote_code=False,
                    )
                except Exception as e:
                    self.logger.error(f"❌ Erro ao carregar SentenceTransformer offline: {e}")
                    self.logger.error("💡 Solução: Configure HF_HUB_OFFLINE=1")
                    raise

                embedding = embedder.encode(semantic_text)
                if hasattr(embedding, "tolist"):
                    embedding_list = embedding.tolist()
                else:
                    embedding_list = list(embedding)

                # Metadados do padrão cacheado
                point_metadata = {
                    "pattern": pattern,
                    "decision_index": i,
                    "utility_score": float(np.random.uniform(0.5, 1.0)),
                    "cache_timestamp": datetime.now(timezone.utc).isoformat(),
                    "hit_count": 0,
                }

                # Armazenar no orchestrator_semantic_cache
                point_id = hash(semantic_text) & 0x7FFFFFFFFFFFFFFF
                self.orchestrator_cache.upsert_points(
                    points=[
                        {
                            "id": point_id,
                            "vector": embedding_list,
                            "payload": point_metadata,
                        }
                    ]
                )

                count += 1
                if (i + 1) % 10 == 0:
                    self.logger.info(f"  ✓ {i + 1}/{num_cached_patterns} padrões cacheados")

            except Exception as e:
                self.logger.warning(f"  ⚠️ Erro ao cachear padrão {i}: {e}")
                self.stats["errors"].append(f"cache_pattern_{i}: {str(e)}")

        self.logger.info(f"✅ OrchestratorCache: {count}/{num_cached_patterns} padrões")
        self.stats["cache_vectors"] = count
        return count

    def verify_collections(self) -> None:
        """Verifica status das coleções após população."""
        self.logger.info("🔍 Verificando status das coleções...")

        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(url=self.qdrant_url)

            collections = {
                "omnimind_consciousness": "Consciência",
                "omnimind_narratives": "Narrativas",
                "orchestrator_semantic_cache": "Cache de Orquestrador",
            }

            for collection_name, display_name in collections.items():
                try:
                    collection_info = client.get_collection(collection_name)
                    point_count = collection_info.points_count
                    self.logger.info(
                        f"  📊 {display_name}: {point_count} vetores "
                        f"(dim={collection_info.config.params.vectors.size})"
                    )
                except Exception as e:
                    self.logger.warning(f"  ⚠️ Erro ao verificar {display_name}: {e}")

        except Exception as e:
            self.logger.warning(f"Erro ao verificar coleções: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório de população das coleções.

        Returns:
            Dict com estatísticas
        """
        self.stats["total_vectors"] = (
            self.stats["consciousness_vectors"]
            + self.stats["narrative_vectors"]
            + self.stats["cache_vectors"]
        )

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": self.stats,
            "summary": {
                "total_vectors_created": self.stats["total_vectors"],
                "errors_encountered": len(self.stats["errors"]),
                "success_rate": (
                    f"{(self.stats['total_vectors'] / max(150, self.stats['total_vectors'] + len(self.stats['errors'])) * 100):.1f}%"
                    if (self.stats["total_vectors"] + len(self.stats["errors"])) > 0
                    else "N/A"
                ),
            },
        }

        if self.stats["errors"]:
            report["errors"] = self.stats["errors"]

        return report

    def populate(self, mode: str = "quick") -> Dict[str, Any]:
        """Executa população completa das coleções.

        Args:
            mode: "quick" (50 cada) ou "full" (200 cada)

        Returns:
            Dict com relatório
        """
        start_time = time.time()

        # Determinar número de vetores conforme modo
        num_vectors = 50 if mode == "quick" else 200

        self.logger.info("=" * 70)
        self.logger.info(f"🚀 Iniciando população de coleções ({mode.upper()} mode)")
        self.logger.info(f"   Alvo: {num_vectors} vetores por coleção")
        self.logger.info("=" * 70)

        try:
            # 1. Popular consciência
            self.logger.info("\n[1/3] Populando consciência...")
            consciousness_count = self.populate_consciousness_states(num_vectors)

            # 2. Popular narrativas
            self.logger.info("\n[2/3] Populando narrativas...")
            narratives_count = self.populate_narratives(num_vectors)

            # 3. Popular cache de orquestrador
            self.logger.info("\n[3/3] Populando cache de orquestrador...")
            cache_count = self.populate_orchestrator_cache(num_vectors)

            # Verificar resultados
            self.logger.info("\n[4/3] Verificando coleções...")
            self.verify_collections()

        except Exception as e:
            self.logger.error(f"❌ Erro durante população: {e}")
            self.stats["errors"].append(f"fatal_error: {str(e)}")

        # Relatório final
        elapsed = time.time() - start_time
        report = self.generate_report()
        report["elapsed_seconds"] = elapsed

        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 RELATÓRIO FINAL")
        self.logger.info("=" * 70)
        self.logger.info(
            f"Consciência:      {report['statistics']['consciousness_vectors']} vetores"
        )
        self.logger.info(f"Narrativas:       {report['statistics']['narrative_vectors']} vetores")
        self.logger.info(f"Cache Orq.:       {report['statistics']['cache_vectors']} vetores")
        self.logger.info(f"Total:            {report['summary']['total_vectors_created']} vetores")
        self.logger.info(f"Erros:            {report['summary']['errors_encountered']}")
        self.logger.info(f"Taxa de Sucesso:  {report['summary']['success_rate']}")
        self.logger.info(f"Tempo Total:      {elapsed:.2f}s")
        self.logger.info("=" * 70 + "\n")

        return report


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Popula coleções de consciência no Qdrant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/populate_consciousness_collections.py --quick
    → Popula com 50 vetores por coleção (rápido, ~30s)

  python scripts/populate_consciousness_collections.py --full
    → Popula com 200 vetores por coleção (completo, ~2min)

Coleções criadas:
  - omnimind_consciousness: Estados de consciência avaliados
  - omnimind_narratives: Narrativas geradas pelo sistema
  - orchestrator_semantic_cache: Padrões semânticos cacheados
        """,
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Modo rápido (50 vetores por coleção)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Modo completo (200 vetores por coleção)",
    )
    parser.add_argument(
        "--qdrant-url",
        default="http://localhost:6333",
        help="URL do Qdrant (padrão: http://localhost:6333)",
    )

    args = parser.parse_args()

    # Validação
    if args.quick and args.full:
        print("❌ Erro: especifique --quick OU --full, não ambos")
        return 1

    mode = "quick" if args.quick else ("full" if args.full else "quick")

    try:
        populator = ConsciousnessCollectionsPopulator(qdrant_url=args.qdrant_url)
        report = populator.populate(mode=mode)

        # Salvar relatório
        report_path = (
            Path(__file__).parent.parent
            / "data/test_reports"
            / f"consciousness_population_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Relatório salvo em: {report_path}")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")
        return 130
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
