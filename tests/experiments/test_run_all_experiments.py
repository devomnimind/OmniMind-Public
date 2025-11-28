"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Testes para src/experiments/run_all_experiments.py.

Testa execução de experimentos de consciência e ética.
"""

from typing import Any, Dict
from unittest.mock import patch

import pytest

from src.experiments.run_all_experiments import (
    generate_summary,
    main,
    run_all_experiments,
)


class TestRunAllExperiments:
    """Testes para run_all_experiments."""

    def test_run_all_experiments_structure(self) -> None:
        """Testa que run_all_experiments retorna estrutura correta."""
        with (
            patch("src.experiments.run_all_experiments.experiment_phi_integration") as mock_phi,
            patch(
                "src.experiments.run_all_experiments.experiment_self_awareness"
            ) as mock_awareness,
            patch(
                "src.experiments.run_all_experiments.experiment_ethics_brazilian_context"
            ) as mock_ethics,
            patch(
                "src.experiments.run_all_experiments.experiment_transparency_tracking"
            ) as mock_transparency,
        ):

            # Configure mocks
            mock_phi.return_value = {"status": "success"}
            mock_awareness.return_value = {"status": "success"}
            mock_ethics.return_value = {"status": "success"}
            mock_transparency.return_value = {"status": "success"}

            results = run_all_experiments()

            assert "consciousness" in results
            assert "ethics" in results

            # Verify consciousness experiments
            assert "phi_integration" in results["consciousness"]
            assert "self_awareness" in results["consciousness"]

            # Verify ethics experiments
            assert "brazilian_context" in results["ethics"]
            assert "transparency" in results["ethics"]

    def test_run_all_experiments_calls_experiments(self) -> None:
        """Testa que todos os experimentos são chamados."""
        with (
            patch("src.experiments.run_all_experiments.experiment_phi_integration") as mock_phi,
            patch(
                "src.experiments.run_all_experiments.experiment_self_awareness"
            ) as mock_awareness,
            patch(
                "src.experiments.run_all_experiments.experiment_ethics_brazilian_context"
            ) as mock_ethics,
            patch(
                "src.experiments.run_all_experiments.experiment_transparency_tracking"
            ) as mock_transparency,
        ):

            # Configure mocks
            mock_phi.return_value = {"status": "success"}
            mock_awareness.return_value = {"status": "success"}
            mock_ethics.return_value = {"status": "success"}
            mock_transparency.return_value = {"status": "success"}

            run_all_experiments()

            # Verify all experiments were called
            mock_phi.assert_called_once()
            mock_awareness.assert_called_once()
            mock_ethics.assert_called_once()
            mock_transparency.assert_called_once()


class TestGenerateSummary:
    """Testes para generate_summary."""

    def test_generate_summary_empty_results(self) -> None:
        """Testa geração de sumário com resultados vazios."""
        results: Dict[str, Any] = {}

        summary = generate_summary(results)

        assert summary["total_experiments"] == 0
        assert summary["successful"] == 0
        assert summary["failed"] == 0
        assert len(summary["experiments"]) == 0

    def test_generate_summary_with_validated_experiments(self) -> None:
        """Testa sumário com experimentos validados."""
        results = {
            "consciousness": {
                "exp1": {"results": {"hypothesis_validated": True}},
                "exp2": {"results": {"hypothesis_validated": False}},
            }
        }

        summary = generate_summary(results)

        assert summary["total_experiments"] == 2
        assert summary["successful"] == 1
        assert summary["failed"] == 1
        assert len(summary["experiments"]) == 2

    def test_generate_summary_with_analysis_field(self) -> None:
        """Testa sumário com campo analysis."""
        results = {
            "ethics": {
                "exp1": {"analysis": {"hypothesis_validated": True}},
                "exp2": {"analysis": {"hypothesis_validated": False}},
            }
        }

        summary = generate_summary(results)

        assert summary["total_experiments"] == 2
        assert summary["successful"] == 1
        assert summary["failed"] == 1

    def test_generate_summary_with_direct_field(self) -> None:
        """Testa sumário com campo direto hypothesis_validated."""
        results = {
            "test": {
                "exp1": {"hypothesis_validated": True},
                "exp2": {"hypothesis_validated": False},
            }
        }

        summary = generate_summary(results)

        assert summary["total_experiments"] == 2
        assert summary["successful"] == 1
        assert summary["failed"] == 1

    def test_generate_summary_mixed_formats(self) -> None:
        """Testa sumário com formatos mistos."""
        results = {
            "category1": {
                "exp1": {"results": {"hypothesis_validated": True}},
                "exp2": {"analysis": {"hypothesis_validated": True}},
                "exp3": {"hypothesis_validated": False},
            }
        }

        summary = generate_summary(results)

        assert summary["total_experiments"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1

    def test_generate_summary_experiment_details(self) -> None:
        """Testa detalhes dos experimentos no sumário."""
        results = {
            "consciousness": {
                "phi_test": {"results": {"hypothesis_validated": True}},
            },
            "ethics": {
                "ethics_test": {"analysis": {"hypothesis_validated": False}},
            },
        }

        summary = generate_summary(results)

        experiments = summary["experiments"]
        assert len(experiments) == 2

        # Find experiments by name
        phi_exp = next(e for e in experiments if e["name"] == "phi_test")
        ethics_exp = next(e for e in experiments if e["name"] == "ethics_test")

        assert phi_exp["category"] == "consciousness"
        assert phi_exp["validated"] is True

        assert ethics_exp["category"] == "ethics"
        assert ethics_exp["validated"] is False

    def test_generate_summary_type_hints(self) -> None:
        """Testa que sumário tem tipo correto."""
        results = {
            "test": {
                "exp1": {"hypothesis_validated": True},
            }
        }

        summary = generate_summary(results)

        # Verify it matches ExperimentSummary structure
        assert "total_experiments" in summary
        assert "successful" in summary
        assert "failed" in summary
        assert "experiments" in summary

        assert isinstance(summary["total_experiments"], int)
        assert isinstance(summary["successful"], int)
        assert isinstance(summary["failed"], int)
        assert isinstance(summary["experiments"], list)


class TestMain:
    """Testes para função main."""

    def test_main_calls_experiment_runners(self) -> None:
        """Testa que main chama os runners de experimentos."""
        with (
            patch(
                "src.experiments.run_all_experiments.run_all_consciousness_experiments"
            ) as mock_consciousness,
            patch("src.experiments.run_all_experiments.run_all_ethics_experiments") as mock_ethics,
            patch("builtins.print") as mock_print,
        ):

            main()

            # Verify experiment runners were called
            mock_consciousness.assert_called_once()
            mock_ethics.assert_called_once()

            # Verify output was printed
            assert mock_print.call_count > 0

    def test_main_prints_header(self) -> None:
        """Testa que main imprime cabeçalho."""
        with (
            patch("src.experiments.run_all_experiments.run_all_consciousness_experiments"),
            patch("src.experiments.run_all_experiments.run_all_ethics_experiments"),
            patch("builtins.print") as mock_print,
        ):

            main()

            # Check that header was printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            header_printed = any("OMNIMIND" in call for call in print_calls)
            assert header_printed

    def test_main_prints_references(self) -> None:
        """Testa que main imprime referências."""
        with (
            patch("src.experiments.run_all_experiments.run_all_consciousness_experiments"),
            patch("src.experiments.run_all_experiments.run_all_ethics_experiments"),
            patch("builtins.print") as mock_print,
        ):

            main()

            # Check that references were printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            references_printed = any("concienciaetica-autonomia.md" in call for call in print_calls)
            assert references_printed

    def test_main_prints_completion_message(self) -> None:
        """Testa que main imprime mensagem de conclusão."""
        with (
            patch("src.experiments.run_all_experiments.run_all_consciousness_experiments"),
            patch("src.experiments.run_all_experiments.run_all_ethics_experiments"),
            patch("builtins.print") as mock_print,
        ):

            main()

            # Check that completion message was printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            completion_printed = any("CONCLUÍDOS" in call for call in print_calls)
            assert completion_printed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
