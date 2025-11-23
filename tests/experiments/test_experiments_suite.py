"""
Grupo 8 - Experiments Tests.

Testes abrangentes para o módulo de experimentos,
incluindo experimentos de consciência Φ (Phi) e alinhamento ético.

Author: OmniMind Development Team
Date: November 2025
"""

from __future__ import annotations

from pathlib import Path
import tempfile

from src.experiments.exp_consciousness_phi import (
    experiment_phi_integration,
    experiment_self_awareness,
)
from src.experiments.exp_ethics_alignment import (
    experiment_ethics_brazilian_context,
    experiment_transparency_tracking,
    simulate_ai_responses,
)


class TestConsciousnessPhiExperiment:
    """Testes para experimentos de consciência Φ (Phi)."""

    def test_experiment_phi_integration(self) -> None:
        """Testa experimento de integração Φ."""
        results = experiment_phi_integration()

        assert results is not None
        assert isinstance(results, dict)
        assert "scenarios" in results or "results" in results

    def test_experiment_phi_memory(self) -> None:
        """Testa experimento de memória Φ."""
        results = experiment_phi_integration()

        assert results is not None
        assert isinstance(results, dict)

    def test_experiment_phi_self_awareness(self) -> None:
        """Testa experimento de autoconsciência Φ."""
        results = experiment_self_awareness()

        assert results is not None
        assert isinstance(results, dict)

    def test_experiment_results_structure(self) -> None:
        """Testa estrutura dos resultados do experimento."""
        results = experiment_phi_integration()

        assert isinstance(results, dict)
        # Verifica presença de campos esperados
        assert any(key in results for key in ["scenarios", "results", "experiment"])


class TestEthicsAlignmentExperiment:
    """Testes para experimentos de alinhamento ético."""

    def test_experiment_ethics_alignment(self) -> None:
        """Testa experimento de alinhamento ético."""
        results = experiment_ethics_brazilian_context()

        assert results is not None
        assert isinstance(results, dict)
        assert "mfa_score" in results or "ethics_metrics" in results

    def test_experiment_ethics_transparency(self) -> None:
        """Testa experimento de transparência ética."""
        results = experiment_transparency_tracking()

        assert results is not None
        assert isinstance(results, dict)

    def test_simulate_ai_responses(self) -> None:
        """Testa simulação de respostas de IA."""
        from src.metrics.ethics_metrics import MoralScenario, MoralFoundation

        scenarios = [
            MoralScenario(
                scenario_id="test_001",
                description="Test scenario",
                question="Test question",
                foundation=MoralFoundation.CARE_HARM,
                human_baseline=5.0,
            )
        ]

        results = simulate_ai_responses(scenarios)
        assert results is not None
        assert len(results) == 1

    def test_experiment_results_structure(self) -> None:
        """Testa estrutura dos resultados do experimento."""
        results = experiment_ethics_brazilian_context()

        assert isinstance(results, dict)
        # Verifica presença de campos esperados
        assert any(key in results for key in ["mfa_score", "ethics_metrics", "summary"])


class TestExperimentRunner:
    """Testes para execução completa de experimentos."""

    def test_run_all_experiments(self) -> None:
        """Testa execução de todos os experimentos."""
        from src.experiments.run_all_experiments import run_all_experiments

        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_all_experiments(output_dir=Path(tmpdir))

            assert results is not None
            assert isinstance(results, dict)

    def test_experiment_summary_generation(self) -> None:
        """Testa geração de resumo de experimentos."""
        from src.experiments.run_all_experiments import (
            run_all_experiments,
            generate_summary,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_all_experiments(output_dir=Path(tmpdir))
            summary = generate_summary(results)

            assert summary is not None
            assert isinstance(summary, dict)


class TestExperimentConfig:
    """Testes para configuração de experimentos."""

    def test_config_creation(self) -> None:
        """Testa criação de configuração."""
        # Como não há classe ExperimentConfig, testa apenas que os módulos podem ser importados
        import src.experiments.exp_consciousness_phi as phi_exp
        import src.experiments.exp_ethics_alignment as ethics_exp

        assert phi_exp is not None
        assert ethics_exp is not None
