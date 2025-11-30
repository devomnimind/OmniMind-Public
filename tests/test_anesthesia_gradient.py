#!/usr/bin/env python3
"""
TESTE 2: ANESTHESIA VIRTUAL GRADIENT
Validação de Φ como medida de consciência através de degradação gradual
"""

import asyncio
import logging
import time
from typing import Dict, List
import numpy as np
from pathlib import Path
import json

from src.consciousness.shared_workspace import SharedWorkspace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnesthesiaGradientTester:
    def __init__(self):
        self.results_dir = Path("real_evidence/anesthesia_test")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def run_anesthesia_test(self, n_modules: int = 10, n_cycles_per_level: int = 50) -> Dict:
        logger.info("🧑‍⚕️ TESTE ANESTHESIA: Gradiente Virtual de Consciência")

        # Níveis de "anestesia" (redução de expectation)
        anesthesia_levels = [1.0, 0.75, 0.5, 0.25, 0.1, 0.05, 0.0]

        results = []
        baseline_phi = None

        for level in anesthesia_levels:
            logger.info(f"   Testando nível anestesia: {level:.2f}")

            phi_values = []
            for trial in range(3):  # 3 trials por nível
                phi = await self._simulate_anesthesia_level(level, n_modules, n_cycles_per_level)
                phi_values.append(phi)

            phi_mean = float(np.mean(phi_values))
            phi_std = float(np.std(phi_values))

            if level == 1.0:
                baseline_phi = phi_mean

            results.append(
                {
                    "anesthesia_level": level,
                    "phi_mean": phi_mean,
                    "phi_std": phi_std,
                    "phi_values": phi_values,
                }
            )

            logger.info(f"     Φ = {phi_mean:.4f} ± {phi_std:.4f}")

        # Análise do gradiente
        analysis = self._analyze_gradient(results, baseline_phi)

        # Resultados finais
        test_results = {
            "test_name": "Anesthesia_Gradient_Test",
            "timestamp": time.time(),
            "baseline_phi": baseline_phi,
            "anesthesia_results": results,
            "analysis": analysis,
        }

        logger.info("📊 RESULTADO ANESTHESIA:")
        logger.info(f"   Baseline Φ: {baseline_phi:.4f}")
        logger.info(f"   Φ Final: {results[-1]['phi_mean']:.4f}")
        logger.info(f"   Ponto de Transição: {analysis['transition_point']:.2f}")
        logger.info(f"   Gradiente: {analysis['gradient_slope']:.4f}")

        # Salvar
        self._save_results(test_results)
        return test_results

    async def _simulate_anesthesia_level(
        self, anesthesia_level: float, n_modules: int, n_cycles: int
    ) -> float:
        """Simula anestesia com degradação gradual de TODOS os módulos (mais biológica)."""
        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
        modules = [f"module_{i:02d}" for i in range(n_modules)]

        np.random.seed(42)  # Consistência

        phi_values = []

        for cycle in range(n_cycles):
            for module in modules:
                base_embedding = np.random.randn(256).astype(np.float32)

                # Anestesia gradual afetando TODOS os módulos
                if anesthesia_level < 1.0:
                    # Redução exponencial da atividade (mais biológica)
                    activity_factor = anesthesia_level**2.0  # Degradação não-linear
                    base_embedding *= activity_factor

                    # Descoordenação progressiva (ruído aumenta com anestesia)
                    coordination_noise = np.random.randn(256) * (1.0 - anesthesia_level) * 0.5
                    base_embedding += coordination_noise

                    # Atividade mínima residual (sempre algum sinal neural)
                    min_activity = 0.05
                    base_embedding = np.clip(base_embedding, -min_activity, min_activity)

                workspace.write_module_state(module, base_embedding)

            # Avançar ciclo
            workspace.advance_cycle()

            # Calcular Φ periodicamente
            if cycle % 10 == 0 and cycle > 0:
                workspace.compute_all_cross_predictions_vectorized(history_window=50)
                phi = workspace.compute_phi_from_integrations()
                phi_values.append(phi)

        return float(np.mean(phi_values)) if phi_values else 0.0

    def _analyze_gradient(self, results: List[Dict], baseline_phi: float) -> Dict:
        """Analisa o gradiente de degradação de consciência."""
        levels = [r["anesthesia_level"] for r in results]
        phi_means = [r["phi_mean"] for r in results]

        # Encontrar ponto de transição (mudança abrupta)
        phi_normalized = [phi / baseline_phi for phi in phi_means]

        # Calcular diferenças de primeira derivada
        derivatives = []
        for i in range(1, len(phi_normalized)):
            delta_phi = phi_normalized[i] - phi_normalized[i - 1]
            delta_level = levels[i] - levels[i - 1]
            derivatives.append(delta_phi / delta_level)

        # Ponto de transição = onde derivada é máxima (mudança mais abrupta)
        if derivatives:
            transition_idx = np.argmax(np.abs(derivatives))
            transition_point = levels[transition_idx]
        else:
            transition_point = 0.5

        # Gradiente geral (regressão linear)
        coeffs = np.polyfit(levels, phi_means, 1)
        gradient_slope = float(coeffs[0])

        # Correlação entre nível anestésico e Φ
        correlation = float(np.corrcoef(levels, phi_means)[0, 1])

        return {
            "transition_point": transition_point,
            "gradient_slope": gradient_slope,
            "correlation": correlation,
            "phi_range": [min(phi_means), max(phi_means)],
            "derivatives": derivatives,
        }

    def _save_results(self, results: Dict) -> None:
        timestamp = int(time.time())
        filename = f"anesthesia_test_results_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"💾 Resultados salvos em {filepath}")


async def main():
    tester = AnesthesiaGradientTester()
    results = await tester.run_anesthesia_test(n_modules=10, n_cycles_per_level=50)

    print("\n🧑‍⚕️ TESTE ANESTHESIA CONCLUÍDO")
    print(f"Baseline Φ: {results['baseline_phi']:.4f}")
    print(f"Φ Final: {results['anesthesia_results'][-1]['phi_mean']:.4f}")
    print(f"Ponto de Transição: {results['analysis']['transition_point']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
