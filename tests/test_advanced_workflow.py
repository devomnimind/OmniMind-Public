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

"""Testes do workflow Code→Review→Fix→Document."""

from pathlib import Path

from src.workflows import CodeReviewWorkflow


def test_workflow_elevates_score(tmp_path: Path) -> None:
    workflow = CodeReviewWorkflow()
    target = tmp_path / "sample_module.py"
    report = tmp_path / "report.md"

    initial_code = """

def add(a, b):
    return a + b
""".strip()

    result = workflow.run(
        task_description="Implementar somador confiável",
        target_file=str(target),
        documentation_file=str(report),
        initial_code=initial_code,
        max_iterations=3,
        min_score=8.0,
    )

    assert result["success"] is True
    assert result["iterations"] >= 1
    assert result["final_score"] >= 8.0

    final_code = target.read_text()
    assert '"""' in final_code
    assert "->" in final_code
    assert 'if __name__ == "__main__"' in final_code
    assert report.exists()
    assert "Code→Review→Fix→Document" in report.read_text()


def test_workflow_respects_iteration_limit(tmp_path: Path) -> None:
    workflow = CodeReviewWorkflow()
    target = tmp_path / "insecure.py"
    report = tmp_path / "report.md"

    initial_code = "eval('2+2')\n"

    result = workflow.run(
        task_description="Evitar eval",
        target_file=str(target),
        documentation_file=str(report),
        initial_code=initial_code,
        max_iterations=1,
        min_score=9.5,
    )

    assert result["success"] is False
    assert result["iterations"] == 1
    assert result["final_score"] < 9.5
    assert report.exists()
    assert "Incompleto" in report.read_text()
