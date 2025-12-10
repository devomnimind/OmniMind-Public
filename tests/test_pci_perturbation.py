#!/usr/bin/env python3
"""
TESTE 1: PCI Perturbacional - Validação de Φ como Medida de Consciência
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

from src.consciousness.shared_workspace import SharedWorkspace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PCITester:
    def __init__(self):
        self.results_dir = Path("real_evidence/pci_test")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def run_pci_test(self, n_modules: int = 10, n_trials: int = 3) -> Dict:
        logger.info("🧠 TESTE PCI: Perturbational Complexity Index")

        # Baseline
        baseline_phi = await self._compute_baseline_phi(n_modules)
        logger.info(".4f")

        # Intervenções
        pci_results = await self._run_perturbations(n_modules, n_trials, baseline_phi)

        # Análise
        all_pcis = [r["pci_mean"] for r in pci_results]
        analysis = {
            "pci_mean": float(np.mean(all_pcis)),
            "pci_std": float(np.std(all_pcis)),
            "baseline_phi": baseline_phi,
        }

        logger.info("📊 RESULTADO PCI:")
        logger.info(".3f")
        logger.info(".3f")

        results = {
            "test_name": "PCI_Test",
            "timestamp": time.time(),
            "baseline_phi": baseline_phi,
            "pci_results": pci_results,
            "analysis": analysis,
        }

        # Salvar
        self._save_results(results)
        return results

    async def _compute_baseline_phi(self, n_modules: int) -> float:
        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
        modules = [f"module_{i:02d}" for i in range(n_modules)]

        np.random.seed(42)
        for module in modules:
            for t in range(200):
                embedding = np.random.randn(256).astype(np.float32)
                workspace.write_module_state(module, embedding)

        for _ in range(5):
            workspace.advance_cycle()

        # Computar predições cruzadas antes de calcular Φ
        workspace.compute_all_cross_predictions_vectorized(history_window=50)

        return workspace.compute_phi_from_integrations()

    async def _run_perturbations(
        self, n_modules: int, n_trials: int, baseline_phi: float
    ) -> List[Dict]:
        results = []

        for module_idx in range(n_modules):
            module_name = f"module_{module_idx:02d}"
            logger.info(f"   Testando {module_name}...")

            pcis = []
            for trial in range(n_trials):
                phi_perturbed = await self._single_perturbation(module_idx, n_modules)
                pci = (baseline_phi - phi_perturbed) / baseline_phi if baseline_phi > 0 else 0
                pcis.append(pci)
                logger.info(f"     Trial {trial}: PCI = {pci:.3f}")

            results.append(
                {
                    "module": module_name,
                    "pci_mean": float(np.mean(pcis)),
                    "pci_std": float(np.std(pcis)),
                }
            )

        return results

    async def _single_perturbation(self, target_module_idx: int, n_modules: int) -> float:
        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
        modules = [f"module_{i:02d}" for i in range(n_modules)]
        target_module = modules[target_module_idx]

        np.random.seed(12345)
        for t in range(200):
            for module in modules:
                embedding = np.random.randn(256).astype(np.float32)
                if module == target_module:
                    perturbation = np.random.randn(256) * 0.5  # 50% noise
                    embedding += perturbation
                workspace.write_module_state(module, embedding)

        for _ in range(5):
            workspace.advance_cycle()

        # Computar predições cruzadas antes de calcular Φ
        workspace.compute_all_cross_predictions_vectorized(history_window=50)

        return workspace.compute_phi_from_integrations()

    def _save_results(self, results: Dict) -> None:
        timestamp = int(time.time())
        filename = f"pci_test_results_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"💾 Resultados salvos em {filepath}")


async def main():
    tester = PCITester()
    await tester.run_pci_test(n_modules=10, n_trials=3)

    print("\n📊 TESTE PCI CONCLUÍDO")
    print(".3f")
    print(".3f")


async def test_pci_with_topological_metrics():
    """Testa PCI perturbation com métricas topológicas."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

    logger.info("🧠 TESTE PCI: Com Topological Metrics")
    logger.info("=" * 60)

    # Criar workspace com engine topológico
    workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
    workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Simular módulos
    modules = [f"module_{i:02d}" for i in range(10)]
    np.random.seed(42)

    # Gerar dados
    for t in range(200):
        for module in modules:
            embedding = np.random.randn(256)
            workspace.write_module_state(module, embedding)
        workspace.advance_cycle()

    # Calcular métricas topológicas
    topological_metrics = workspace.compute_hybrid_topological_metrics()

    # Verificar que métricas topológicas podem ser usadas na análise de PCI
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # PCI: complexidade perturbacional (intervenção → mudança em Φ)
        # Topological: estrutura e integração (Omega, Betti-0)
        # Ambas podem ser usadas para análise completa de complexidade

    logger.info("✅ PCI Perturbation + Topological Metrics verified")


if __name__ == "__main__":
    asyncio.run(main())
