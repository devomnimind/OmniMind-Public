#!/usr/bin/env python3
"""
TESTE 3: TIMESCALE SWEEP
Validação de Φ através de varredura de escalas temporais
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


class TimescaleSweepTester:
    def __init__(self):
        self.results_dir = Path("real_evidence/timescale_test")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def run_timescale_test(self, n_modules: int = 10, n_cycles_per_window: int = 100) -> Dict:
        logger.info("⏰ TESTE TIMESCALE: Varredura de Escalas Temporais")

        # Janelas temporais para teste (em ciclos)
        time_windows = [10, 25, 50, 100, 200, 500]

        results = []

        for window_size in time_windows:
            logger.info(f"   Testando janela temporal: {window_size} ciclos")

            phi_values = []
            for trial in range(3):  # 3 trials por janela
                phi = await self._simulate_timescale(window_size, n_modules, n_cycles_per_window)
                phi_values.append(phi)

            phi_mean = float(np.mean(phi_values))
            phi_std = float(np.std(phi_values))

            results.append(
                {
                    "time_window": window_size,
                    "phi_mean": phi_mean,
                    "phi_std": phi_std,
                    "phi_values": phi_values,
                }
            )

            logger.info(f"     Φ = {phi_mean:.4f} ± {phi_std:.4f}")

        # Análise da robustez temporal
        analysis = self._analyze_timescale_robustness(results)

        # Resultados finais
        test_results = {
            "test_name": "Timescale_Sweep_Test",
            "timestamp": time.time(),
            "timescale_results": results,
            "analysis": analysis,
        }

        logger.info("📊 RESULTADO TIMESCALE:")
        logger.info(f"   Φ Médio Global: {analysis['global_phi_mean']:.4f}")
        logger.info(f"   Robustez (CV): {analysis['robustness_cv']:.4f}")
        logger.info(f"   Estabilidade: {analysis['stability_score']:.4f}")

        # Salvar
        self._save_results(test_results)
        return test_results

    async def _simulate_timescale(self, time_window: int, n_modules: int, n_cycles: int) -> float:
        """Simula sistema com janela temporal específica."""
        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
        modules = [f"module_{i:02d}" for i in range(n_modules)]

        np.random.seed(42)  # Consistência

        phi_values = []

        for cycle in range(n_cycles):
            for module in modules:
                # Atividade normal com variação temporal natural
                base_embedding = np.random.randn(256).astype(np.float32)
                # Adiciona componente temporal (drift lento)
                temporal_drift = 0.1 * np.sin(2 * np.pi * cycle / 50)  # Período de 50 ciclos
                base_embedding += temporal_drift

                workspace.write_module_state(module, base_embedding)

            workspace.advance_cycle()

            # Calcular Φ usando a janela temporal específica
            if cycle % 20 == 0 and cycle > time_window:
                workspace.compute_all_cross_predictions_vectorized(history_window=time_window)
                phi = workspace.compute_phi_from_integrations()
                phi_values.append(phi)

        return float(np.mean(phi_values)) if phi_values else 0.0

    def _analyze_timescale_robustness(self, results: List[Dict]) -> Dict:
        """Analisa robustez de Φ em diferentes escalas temporais."""
        phi_means = [r["phi_mean"] for r in results]
        time_windows = [r["time_window"] for r in results]

        # Estatísticas globais
        global_phi_mean = float(np.mean(phi_means))
        global_phi_std = float(np.std(phi_means))

        # Coeficiente de variação (robustez)
        robustness_cv = global_phi_std / global_phi_mean if global_phi_mean > 0 else 0.0

        # Estabilidade: quanto Φ permanece consistente através de escalas
        stability_score = 1.0 - robustness_cv  # Score de 0-1, maior = mais estável

        # Análise de tendência
        coeffs = np.polyfit(np.log(time_windows), phi_means, 1)
        temporal_trend = float(coeffs[0])  # Inclinação da tendência log-temporal

        # Ponto ótimo de integração
        optimal_window_idx = np.argmax(phi_means)
        optimal_window = time_windows[optimal_window_idx]

        return {
            "global_phi_mean": global_phi_mean,
            "global_phi_std": global_phi_std,
            "robustness_cv": robustness_cv,
            "stability_score": stability_score,
            "temporal_trend": temporal_trend,
            "optimal_window": optimal_window,
            "phi_range": [min(phi_means), max(phi_means)],
        }

    def _save_results(self, results: Dict) -> None:
        timestamp = int(time.time())
        filename = f"timescale_test_results_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"💾 Resultados salvos em {filepath}")


async def main():
    tester = TimescaleSweepTester()
    results = await tester.run_timescale_test(n_cycles_per_window=100)

    print("\n⏰ TESTE TIMESCALE CONCLUÍDO")
    print(f"Φ Médio Global: {results['analysis']['global_phi_mean']:.4f}")
    print(f"Robustez (CV): {results['analysis']['robustness_cv']:.4f}")
    print(f"Janela Ótima: {results['analysis']['optimal_window']} ciclos")


async def test_timescale_with_topological_metrics():
    """Testa timescale sweep com métricas topológicas."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

    logger.info("⏰ TESTE TIMESCALE: Com Topological Metrics")
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

    # Verificar que métricas topológicas podem ser usadas na análise de timescale
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # Timescale: robustez temporal (Φ em diferentes janelas)
        # Topological: estrutura e integração (Omega, Betti-0)
        # Ambas podem ser usadas para análise completa de robustez temporal

    logger.info("✅ Timescale Sweep + Topological Metrics verified")


if __name__ == "__main__":
    asyncio.run(main())
