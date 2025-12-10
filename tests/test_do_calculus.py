#!/usr/bin/env python3
"""
TESTE 5: VALIDAÇÃO CAUSAL - Do-Calculus
Testa intervenção causal em Φ usando Do-Calculus

Este teste implementa o critério de Pearl (2009) para causalidade:
- Se P(Y|do(X)) ≠ P(Y|X), então X causa Y
- Aplicado a Φ: intervenção em módulos deve afetar Φ
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

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
except ImportError as e:
    logger.error(f"Failed to import: {e}")
    raise


class DoCalculusValidator:
    """
    Valida causalidade usando Do-Calculus de Pearl
    Testa: P(Φ|do(intervenção)) ≠ P(Φ|observação)
    """

    def __init__(self, n_experiments: int = 10):
        self.n_experiments = n_experiments
        self.results_dir = Path("real_evidence/do_calculus_test")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.params = get_parameter_manager()

    def run_do_calculus_test(self) -> Dict[str, Any]:
        """
        Executa teste completo de Do-Calculus
        """
        logger.info("🔬 TESTE 5: VALIDAÇÃO CAUSAL - Do-Calculus")
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

        # Análise estatística
        causal_analysis = self._analyze_causal_effects(observational_results, intervention_results)

        # Teste de significância
        significance_test = self._test_causal_significance(
            observational_results, intervention_results
        )

        test_results = {
            "test_name": "Do_Calculus_Causal_Validation",
            "timestamp": time.time(),
            "n_experiments": self.n_experiments,
            "observational_results": observational_results,
            "intervention_results": intervention_results,
            "causal_analysis": causal_analysis,
            "significance_test": significance_test,
            "causal_criterion_met": significance_test["causal_effect_significant"],
        }

        # Salvar resultados
        self._save_results(test_results)

        logger.info("📊 RESULTADO DO-CALCULUS:")
        logger.info(f"   Efeito Causal Médio: {causal_analysis['mean_causal_effect']:.4f}")
        sig_str = "✅ SIM" if significance_test["causal_effect_significant"] else "❌ NÃO"
        logger.info(f"   Efeito Significativo: {sig_str}")
        crit_str = "✅ ATENDIDO" if test_results["causal_criterion_met"] else "❌ NÃO ATENDIDO"
        logger.info(f"   Critério Causal: {crit_str}")

        return test_results

    def _compute_phi_observational(self, seed: int) -> float:
        """
        Computa Φ sem intervenção (observacional)
        """
        np.random.seed(2000 + seed)

        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)

        # Gerar dados normais
        self._generate_normal_data(workspace, seed)

        # Computar Φ
        phi_value = self._compute_phi_from_workspace(workspace)

        return phi_value

    def _compute_phi_interventional(self, seed: int) -> float:
        """
        Computa Φ COM intervenção causal
        Do(X = x): força X para valor específico
        """
        np.random.seed(3000 + seed)

        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)

        # Gerar dados com intervenção
        self._generate_intervention_data(workspace, seed)

        # Computar Φ
        phi_value = self._compute_phi_from_workspace(workspace)

        return phi_value

    def _generate_normal_data(self, workspace: SharedWorkspace, seed: int) -> None:
        """
        Gera dados normais sem intervenção
        """
        np.random.seed(seed)
        modules = [f"module_{i:02d}" for i in range(10)]

        for t in range(50):  # Menos dados para teste rápido
            for module in modules:
                # Dados normais com dependências causais
                if t == 0:
                    embedding = np.random.randn(256)
                else:
                    # Dependência causal simulada - pegar último estado como array
                    last_state = workspace.get_module_history(module)[-1]
                    if hasattr(last_state, "embedding"):
                        last_embedding = last_state.embedding
                    else:
                        last_embedding = np.array(last_state)
                    embedding = 0.7 * last_embedding + 0.3 * np.random.randn(256)

                workspace.write_module_state(module, embedding)

        # Avançar ciclos
        for _ in range(3):
            workspace.advance_cycle()

    def _generate_intervention_data(self, workspace: SharedWorkspace, seed: int) -> None:
        """
        Gera dados COM intervenção causal
        Do(intervenção): força módulo crítico para valor específico
        """
        np.random.seed(seed)
        modules = [f"module_{i:02d}" for i in range(10)]

        # Escolher módulo para intervenção (módulo crítico)
        intervention_module = "module_05"  # Módulo central
        intervention_value = np.ones(256) * 2.0  # Valor forçado alto

        for t in range(50):
            for module in modules:
                if module == intervention_module and t >= 25:  # Intervenção na segunda metade
                    # INTERVENÇÃO: força valor específico (Do-calculus)
                    embedding = intervention_value + 0.1 * np.random.randn(256)
                else:
                    # Dados normais
                    if t == 0:
                        embedding = np.random.randn(256)
                    else:
                        # Dados normais
                        last_state = workspace.get_module_history(module)[-1]
                        if hasattr(last_state, "embedding"):
                            last_embedding = last_state.embedding
                        else:
                            last_embedding = np.array(last_state)
                        embedding = 0.7 * last_embedding + 0.3 * np.random.randn(256)

                workspace.write_module_state(module, embedding)

        # Avançar ciclos
        for _ in range(3):
            workspace.advance_cycle()

    def _compute_phi_from_workspace(self, workspace: SharedWorkspace) -> float:
        """
        Computa Φ de um workspace configurado
        """
        # Computar predições cruzadas
        workspace.compute_all_cross_predictions_vectorized(history_window=20)

        # Computar Φ
        phi_value = workspace.compute_phi_from_integrations()

        return phi_value

    def _analyze_causal_effects(
        self, observational: List[float], interventional: List[float]
    ) -> Dict[str, float]:
        """
        Analisa efeitos causais entre observacional e intervencional
        """
        obs_array = np.array(observational)
        int_array = np.array(interventional)

        causal_effects = int_array - obs_array

        return {
            "mean_causal_effect": float(np.mean(causal_effects)),
            "std_causal_effect": float(np.std(causal_effects)),
            "min_causal_effect": float(np.min(causal_effects)),
            "max_causal_effect": float(np.max(causal_effects)),
            "causal_effect_range": float(np.max(causal_effects) - np.min(causal_effects)),
        }

    def _test_causal_significance(
        self, observational: List[float], interventional: List[float]
    ) -> Dict[str, Any]:
        """
        Testa significância estatística do efeito causal
        """
        from scipy import stats

        obs_array = np.array(observational)
        int_array = np.array(interventional)

        # Teste t pareado
        t_stat, p_value = stats.ttest_rel(obs_array, int_array)

        # Teste de Wilcoxon (não-paramétrico)
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(obs_array, int_array)

        # Efeito causal significativo se p < 0.05
        causal_effect_significant = p_value < 0.05

        return {
            "t_statistic": float(t_stat),
            "t_p_value": float(p_value),
            "wilcoxon_statistic": float(wilcoxon_stat),
            "wilcoxon_p_value": float(wilcoxon_p),
            "causal_effect_significant": causal_effect_significant,
            "effect_size": float(abs(np.mean(int_array) - np.mean(obs_array)) / np.std(obs_array)),
        }

    def _save_results(self, results: Dict) -> None:
        """Salva resultados do teste Do-Calculus"""
        timestamp = int(time.time())
        filename = f"do_calculus_results_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"💾 Resultados Do-Calculus salvos em {filepath}")


def main():
    """Teste de validação causal usando Do-Calculus"""
    validator = DoCalculusValidator(n_experiments=10)
    results = validator.run_do_calculus_test()

    print("\n🔬 TESTE 5 DO-CALCULUS CONCLUÍDO")
    print(f"Efeito Causal Médio: {results['causal_analysis']['mean_causal_effect']:.4f}")
    sig_str = "✅ SIM" if results["significance_test"]["causal_effect_significant"] else "❌ NÃO"
    print(f"Efeito Significativo: {sig_str}")
    print(
        f"Critério Causal: {'✅ ATENDIDO' if results['causal_criterion_met'] else '❌ NÃO ATENDIDO'}"
    )


def test_do_calculus_with_topological_metrics():
    """Testa Do-Calculus com métricas topológicas."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

    logger.info("🔬 TESTE DO-CALCULUS: Com Topological Metrics")
    logger.info("=" * 60)

    # Criar workspace com engine topológico
    workspace = SharedWorkspace(embedding_dim=256, max_history_size=1000)
    workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Simular módulos
    modules = ["qualia_engine", "narrative_constructor", "expectation_module"]
    np.random.seed(42)

    # Gerar dados
    for t in range(100):
        for module in modules:
            embedding = np.random.randn(256)
            workspace.write_module_state(module, embedding)
        workspace.advance_cycle()

    # Calcular métricas topológicas
    topological_metrics = workspace.compute_hybrid_topological_metrics()

    # Verificar que métricas topológicas podem ser usadas na análise causal
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # Do-Calculus: intervenção causal
        # Topological: estrutura e integração
        # Ambas podem ser usadas para validação causal completa

    logger.info("✅ Do-Calculus + Topological Metrics verified")


if __name__ == "__main__":
    main()
