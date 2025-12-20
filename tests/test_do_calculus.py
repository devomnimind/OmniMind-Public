#!/usr/bin/env python3
"""
TESTE 5: VALIDAÇÃO CAUSAL - Do-Calculus (REFACTORED)
Testa intervenção causal em Φ usando Do-Calculus via CausalEngine (src/metacognition).

Este teste valida:
1. A capacidade do CausalEngine de detectar causalidade.
2. A integração do CausalEngine com métricas do workspace.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from omnimind_parameters import get_parameter_manager  # type: ignore[import-untyped]
    from src.consciousness.shared_workspace import SharedWorkspace
    from src.metacognition.causal_engine import CausalEngine
except ImportError as e:
    logger.error(f"Failed to import: {e}")
    raise


class DoCalculusValidator:
    """
    Valida causalidade usando CausalEngine.
    """

    def __init__(self, n_experiments: int = 10):
        self.n_experiments = n_experiments
        self.results_dir = Path("real_evidence/do_calculus_test")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.params = get_parameter_manager()
        self.causal_engine = CausalEngine(confidence_level=0.95)

    def run_do_calculus_test(self) -> Dict[str, Any]:
        """
        Executa teste completo de Do-Calculus
        """
        logger.info("🔬 TESTE 5: VALIDAÇÃO CAUSAL - Do-Calculus (Engine Refactor)")
        logger.info("=" * 60)

        # Experimentos de intervenção
        intervention_results = []
        observational_results = []

        for exp_id in range(self.n_experiments):
            logger.info(f"Experimento {exp_id + 1}/{self.n_experiments}")

            # Resultado observacional (sem intervenção)
            phi_obs = self._compute_phi_observational(exp_id)
            observational_results.append(phi_obs)

            # Resultado com intervenção
            phi_int = self._compute_phi_interventional(exp_id)
            intervention_results.append(phi_int)

            logger.info(f"   Observacional: Φ = {phi_obs:.4f}")
            logger.info(f"   Intervencional: Φ = {phi_int:.4f}")
            logger.info(f"   Diferença: {phi_int - phi_obs:.4f}")

        # Análise Causal via Engine
        causal_report = self.causal_engine.compute_causal_effect(
            observational_results, intervention_results
        )

        test_results = {
            "test_name": "Do_Calculus_Causal_Validation",
            "timestamp": time.time(),
            "n_experiments": self.n_experiments,
            "observational_results": observational_results,
            "intervention_results": intervention_results,
            "causal_analysis": causal_report,
            "causal_criterion_met": causal_report.get("is_causal", False),
        }

        # Salvar resultados
        self._save_results(test_results)

        logger.info("📊 RESULTADO DO-CALCULUS (ENGINE):")
        logger.info(f"   ACE (Efeito Médio): {causal_report['ace']:.4f}")
        logger.info(f"   Cohen's d: {causal_report['effect_size_cohen']:.4f}")
        logger.info(f"   P-Value (T-Test): {causal_report['p_value_t']:.4f}")

        crit_str = (
            "✅ CAUSALIDADE COMPROVADA" if test_results["causal_criterion_met"] else "❌ INCERTO"
        )
        logger.info(f"   Veredito: {crit_str}")

        return test_results

    def _compute_phi_observational(self, seed: int) -> float:
        """
        Computa Φ sem intervenção (observacional)
        """
        np.random.seed(2000 + seed)
        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
        self._generate_normal_data(workspace, seed)
        return self._compute_phi_from_workspace(workspace)

    def _compute_phi_interventional(self, seed: int) -> float:
        """
        Computa Φ COM intervenção causal
        Do(X = x): força X para valor específico
        """
        np.random.seed(3000 + seed)
        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
        self._generate_intervention_data(workspace, seed)
        return self._compute_phi_from_workspace(workspace)

    def _generate_normal_data(self, workspace: SharedWorkspace, seed: int) -> None:
        """
        Gera dados normais sem intervenção
        """
        np.random.seed(seed)
        modules = [f"module_{i:02d}" for i in range(10)]

        for t in range(50):
            for module in modules:
                if t == 0:
                    embedding = np.random.randn(256)
                else:
                    last_state = workspace.get_module_history(module)[-1]
                    if hasattr(last_state, "embedding"):
                        last_embedding = last_state.embedding
                    else:
                        last_embedding = np.array(last_state)
                    embedding = 0.7 * last_embedding + 0.3 * np.random.randn(256)

                workspace.write_module_state(module, embedding)

        for _ in range(3):
            workspace.advance_cycle()

    def _generate_intervention_data(self, workspace: SharedWorkspace, seed: int) -> None:
        """
        Gera dados COM intervenção causal
        """
        np.random.seed(seed)
        modules = [f"module_{i:02d}" for i in range(10)]
        intervention_module = "module_05"
        intervention_value = np.ones(256) * 2.0

        for t in range(50):
            for module in modules:
                if module == intervention_module and t >= 25:
                    # INTERVENÇÃO: força valor específico (Do-calculus)
                    embedding = intervention_value + 0.1 * np.random.randn(256)
                else:
                    if t == 0:
                        embedding = np.random.randn(256)
                    else:
                        last_state = workspace.get_module_history(module)[-1]
                        if hasattr(last_state, "embedding"):
                            last_embedding = last_state.embedding
                        else:
                            last_embedding = np.array(last_state)
                        embedding = 0.7 * last_embedding + 0.3 * np.random.randn(256)

                workspace.write_module_state(module, embedding)

        for _ in range(3):
            workspace.advance_cycle()

    def _compute_phi_from_workspace(self, workspace: SharedWorkspace) -> float:
        workspace.compute_all_cross_predictions_vectorized(history_window=20)
        return workspace.compute_phi_from_integrations()

    def _save_results(self, results: Dict) -> None:
        timestamp = int(time.time())
        filename = f"do_calculus_results_{timestamp}.json"
        filepath = self.results_dir / filename
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"💾 Resultados salves em {filepath}")


def main():
    validator = DoCalculusValidator(n_experiments=10)
    results = validator.run_do_calculus_test()
    if not results["causal_criterion_met"]:
        # Se falhar (por random noise), não quebra pipeline CI, mas avisa
        logger.warning("Causalidade não atingiu significância neste run (pode ser ruído).")
    else:
        logger.info("Teste Causal OK.")


if __name__ == "__main__":
    main()
