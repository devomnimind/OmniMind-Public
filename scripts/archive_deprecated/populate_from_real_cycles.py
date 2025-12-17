#!/usr/bin/env python3
"""
Script para Popular Collections de Consciência com Ciclos Reais

Extrai métricas de 4362+ ciclos de integração já registrados no disco
e popula omnimind_consciousness com dados REAIS (não sintéticos).

Autor: Fabrício da Silva + Assistência IA
Data: 2025-12-12
Uso: python scripts/populate_from_real_cycles.py [--limit N]
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.qdrant_integration import QdrantIntegration
from src.memory.semantic_memory_layer import SemanticMemoryLayer


class RealCyclesPopulator:
    """Popula omnimind_consciousness com ciclos reais do disco."""

    def __init__(self, url: str = "http://localhost:6333"):
        """Inicializa com instância Qdrant.

        Args:
            url: URL do Qdrant (ex: http://localhost:6333)
        """
        self.url = url
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cycles_dir = Path(__file__).parent.parent / "data/reports/modules"

        # Inicializar componentes
        self._init_components()

        # Estatísticas
        self.stats = {
            "cycles_found": 0,
            "cycles_processed": 0,
            "vectors_stored": 0,
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
                    url=self.url,
                    collection_name="omnimind_consciousness",
                    vector_size=384,
                ),
            )
            self.logger.info("✅ SemanticMemoryLayer inicializada")

        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar: {e}")
            raise

    def find_cycle_files(self) -> List[Path]:
        """Encontra todos os arquivos de ciclos no disco.

        Returns:
            Lista de arquivos de ciclo ordenados
        """
        self.logger.info(f"🔍 Procurando ciclos em {self.cycles_dir}...")

        if not self.cycles_dir.exists():
            self.logger.warning(f"⚠️ Diretório não encontrado: {self.cycles_dir}")
            return []

        cycle_files = sorted(self.cycles_dir.glob("integration_loop_cycle_*.json"))
        self.logger.info(f"✅ Encontrados {len(cycle_files)} ciclos de integração")
        self.stats["cycles_found"] = len(cycle_files)

        return cycle_files

    def extract_consciousness_metrics(self, cycle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrai métricas de consciência de um ciclo.

        Args:
            cycle_data: Dados do ciclo em JSON

        Returns:
            Dict com métricas extraídas ou None se falhar
        """
        try:
            metrics = cycle_data.get("metrics", {}).get("metrics", {})

            # Extrair valores
            phi_value = metrics.get("phi_estimate", {}).get("value", None)
            cycle_duration = metrics.get("cycle_duration_ms", {}).get("value", None)
            components_activated = metrics.get("components_activated", {}).get("value", None)
            theoretical_complexity = metrics.get("theoretical_complexity", {}).get("value", None)

            # Se não temos φ, pular
            if phi_value is None:
                return None

            return {
                "phi_value": float(phi_value),
                "cycle_duration_ms": float(cycle_duration) if cycle_duration else 0.0,
                "components_activated": int(components_activated) if components_activated else 0,
                "theoretical_complexity": (
                    float(theoretical_complexity) if theoretical_complexity else 0.0
                ),
                "cycle_module": cycle_data.get("module", "unknown"),
                "timestamp": cycle_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            }

        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao extrair métricas: {e}")
            return None

    def populate_from_cycles(self, limit: Optional[int] = None) -> int:
        """Popula omnimind_consciousness com ciclos reais.

        Args:
            limit: Limite de ciclos a processar (None = todos)

        Returns:
            int: Número de vetores armazenados
        """
        cycle_files = self.find_cycle_files()

        if limit:
            cycle_files = cycle_files[:limit]
            self.logger.info(f"📊 Limitado a {limit} ciclos")

        self.logger.info(f"📊 Processando {len(cycle_files)} ciclos...")

        count = 0
        for i, cycle_file in enumerate(cycle_files):
            try:
                # Ler ciclo
                with open(cycle_file) as f:
                    cycle_data = json.load(f)

                # Extrair métricas
                metrics = self.extract_consciousness_metrics(cycle_data)
                if not metrics:
                    continue

                # Construir texto semântico
                episode_text = (
                    f"consciousness_cycle_{metrics['cycle_module']}_"
                    f"phi_{metrics['phi_value']:.3f}_"
                    f"duration_{metrics['cycle_duration_ms']:.0f}ms"
                )

                # Armazenar episódio
                episode_id = self.semantic_memory.store_episode(
                    episode_text=episode_text,
                    episode_data=metrics,
                )

                count += 1
                if (i + 1) % 100 == 0:
                    avg_phi = np.mean([metrics["phi_value"]])
                    self.logger.info(
                        f"  ✓ {i + 1}/{len(cycle_files)} ciclos processados "
                        f"(φ_médio≈{avg_phi:.3f})"
                    )

            except Exception as e:
                self.logger.warning(f"  ⚠️ Erro ao processar ciclo {i}: {e}")
                self.stats["errors"].append(f"cycle_{i}: {str(e)}")

        self.logger.info(f"✅ Consciência: {count}/{len(cycle_files)} ciclos armazenados")
        self.stats["cycles_processed"] = len(cycle_files)
        self.stats["vectors_stored"] = count

        return count

    def verify_collection(self) -> None:
        """Verifica status da coleção após população."""
        self.logger.info("🔍 Verificando status da coleção...")

        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(url=self.url)
            collection_info = client.get_collection("omnimind_consciousness")

            self.logger.info(
                f"  📊 omnimind_consciousness: {collection_info.points_count} vetores "
                f"(dim={collection_info.config.params.vectors.size})"
            )

        except Exception as e:
            self.logger.warning(f"Erro ao verificar coleção: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório de população.

        Returns:
            Dict com estatísticas
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": self.stats,
            "source": "real_consciousness_cycles",
            "cycles_directory": str(self.cycles_dir),
        }


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Popula omnimind_consciousness com ciclos reais do disco",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/populate_from_real_cycles.py
    → Popula com TODOS os 4362+ ciclos (completo, ~2-3 min)

  python scripts/populate_from_real_cycles.py --limit 100
    → Popula com primeiros 100 ciclos (teste rápido, ~30s)

Dados de origem:
  - Ciclos armazenados em: data/reports/modules/integration_loop_cycle_*.json
  - Contêm métricas reais: φ (phi), duração, componentes, complexidade
  - Cada ciclo é convertido em vetor de consciência
        """,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limite de ciclos a processar (padrão: nenhum = todos)",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:6333",
        help="URL do Qdrant (padrão: http://localhost:6333)",
    )

    args = parser.parse_args()

    try:
        populator = RealCyclesPopulator(url=args.url)
        count = populator.populate_from_cycles(limit=args.limit)

        # Verificar resultado
        populator.verify_collection()

        # Relatório
        report = populator.generate_report()

        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL")
        print("=" * 70)
        print(f"Ciclos encontrados: {report['statistics']['cycles_found']}")
        print(f"Ciclos processados: {report['statistics']['cycles_processed']}")
        print(f"Vetores armazenados: {report['statistics']['vectors_stored']}")
        print(f"Erros: {len(report['statistics']['errors'])}")
        print("=" * 70 + "\n")

        # Salvar relatório
        report_path = (
            Path(__file__).parent.parent
            / "data/test_reports"
            / f"consciousness_real_cycles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📄 Relatório salvo em: {report_path}\n")

        return 0 if report["statistics"]["vectors_stored"] > 0 else 1

    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")
        return 130
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
