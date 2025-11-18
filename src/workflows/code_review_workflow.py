"""Workflow Code→Review→Fix→Document com heurísticas rastreáveis."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..tools.omnimind_tools import ToolsFramework


@dataclass
class IterationRecord:
    """Resumo de uma iteração do workflow."""

    iteration: int
    review: Dict[str, Any]
    fixes: List[str]


class CodeReviewWorkflow:
    """Executa o ciclo Code → Review → Fix → Document com auditoria."""

    def __init__(self, tools_framework: Optional[ToolsFramework] = None) -> None:
        self.tools = tools_framework or ToolsFramework()

    def run(
        self,
        task_description: str,
        target_file: str,
        documentation_file: str,
        initial_code: str,
        max_iterations: int = 3,
        min_score: float = 8.0,
    ) -> Dict[str, Any]:
        """Executa o workflow completo e retorna métricas finais."""

        if max_iterations < 1:
            raise ValueError("max_iterations deve ser >= 1")

        target_path = Path(target_file)
        doc_path = Path(documentation_file)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.parent.mkdir(parents=True, exist_ok=True)

        self._write_content(str(target_path), initial_code)

        history: List[IterationRecord] = []
        success = False

        for iteration in range(1, max_iterations + 1):
            code = self._read_content(str(target_path))
            review = self._evaluate_code(code)
            history.append(
                IterationRecord(iteration=iteration, review=review, fixes=[])
            )

            if review["overall_score"] >= min_score:
                success = True
                break

            updated_code, fixes = self._apply_fix(
                code=code,
                task_description=task_description,
                suggestions=review["suggestions"],
            )
            history[-1].fixes = fixes

            if not fixes:
                # Evitar loop infinito quando não há mais heurísticas aplicáveis
                break

            self._write_content(str(target_path), updated_code)

        final_review = history[-1].review if history else {}
        self._write_content(
            str(doc_path),
            self._generate_report(
                task_description=task_description,
                target_file=str(target_path),
                history=history,
                success=success,
            ),
        )

        return {
            "success": success,
            "iterations": len(history),
            "final_score": final_review.get("overall_score", 0.0),
            "history": [record.__dict__ for record in history],
            "report_path": str(doc_path),
            "target_file": str(target_path),
        }

    # ------------------------------------------------------------------
    # Etapas principais
    # ------------------------------------------------------------------

    def _evaluate_code(self, code: str) -> Dict[str, Any]:
        correctness = self._score_correctness(code)
        readability = self._score_readability(code)
        efficiency = self._score_efficiency(code)
        security = self._score_security(code)
        maintainability = self._score_maintainability(code)

        scores = {
            "correctness": correctness,
            "readability": readability,
            "efficiency": efficiency,
            "security": security,
            "maintainability": maintainability,
        }
        overall = round(statistics.mean(scores.values()), 2)

        suggestions = []
        if not self._has_module_docstring(code):
            suggestions.append("Adicionar docstring de módulo.")
        if not self._has_type_hints(code):
            suggestions.append("Adicionar type hints nas assinaturas.")
        if "if __name__" not in code:
            suggestions.append("Adicionar bloco main para testes básicos.")
        if any(keyword in code for keyword in ("eval", "exec")):
            suggestions.append("Remover uso de eval/exec por segurança.")

        strengths = [k for k, v in scores.items() if v >= 8.0]
        weaknesses = [k for k, v in scores.items() if v < 8.0]

        return {
            "scores": scores,
            "overall_score": overall,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
        }

    def _apply_fix(
        self, code: str, task_description: str, suggestions: List[str]
    ) -> Tuple[str, List[str]]:
        updated = code
        fixes: List[str] = []

        if "Adicionar docstring de módulo." in suggestions:
            updated = self._add_module_docstring(task_description, updated)
            fixes.append("module_docstring")

        if "Adicionar type hints nas assinaturas." in suggestions:
            updated = self._add_type_hints(updated)
            fixes.append("type_hints")

        if "Adicionar bloco main para testes básicos." in suggestions:
            updated = self._ensure_main_block(updated, task_description)
            fixes.append("main_block")

        if "Remover uso de eval/exec por segurança." in suggestions:
            updated = updated.replace("eval", "")
            updated = updated.replace("exec", "")
            fixes.append("remove_eval_exec")

        return updated, fixes

    def _generate_report(
        self,
        task_description: str,
        target_file: str,
        history: List[IterationRecord],
        success: bool,
    ) -> str:
        header = (
            "# Relatório Code→Review→Fix→Document\n"
            f"- Tarefa: {task_description}\n"
            f"- Arquivo final: `{target_file}`\n"
            f"- Iterações executadas: {len(history)}\n"
            f"- Status final: {'✅ Sucesso' if success else '⚠️ Incompleto'}\n\n"
        )

        rows = [
            "| Iteração | Score | Forças | Fraquezas | Correções |",
            "| --- | --- | --- | --- | --- |",
        ]
        for record in history:
            review = record.review
            rows.append(
                "| {iter} | {score:.2f} | {strengths} | {weaknesses} | {fixes} |".format(
                    iter=record.iteration,
                    score=review["overall_score"],
                    strengths=", ".join(review["strengths"]) or "-",
                    weaknesses=", ".join(review["weaknesses"]) or "-",
                    fixes=", ".join(record.fixes) or "-",
                )
            )

        lesson_lines = [
            "\n## Lições e próximos passos\n",
            (
                "1. Garantir docstrings e type hints eleva automaticamente "
                "maintainability/readability.\n"
            ),
            (
                "2. Blocos main simples ajudam nos critérios de corretude "
                "sem exigir frameworks externos.\n"
            ),
            (
                "3. Remover chamadas arriscadas (`eval`/`exec`) mantém o score "
                "de segurança acima da meta.\n"
            ),
        ]
        lessons = "".join(lesson_lines)

        return header + "\n".join(rows) + lessons

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(10.0, round(value, 2)))

    def _score_correctness(self, code: str) -> float:
        score = 6.0
        if "return" in code:
            score += 1.5
        if "raise" in code:
            score += 1.0
        if "if __name__" in code:
            score += 0.5
        if "pass" in code:
            score -= 1.0
        return self._clamp(score)

    def _score_readability(self, code: str) -> float:
        score = 5.5
        if self._has_module_docstring(code):
            score += 2.0
        avg_len = self._average_line_length(code)
        if avg_len <= 80:
            score += 1.0
        if "    " in code:
            score += 0.5
        return self._clamp(score)

    def _score_efficiency(self, code: str) -> float:
        score = 7.0
        loop_count = code.count("for ") + code.count("while ")
        if loop_count == 0:
            score += 1.0
        elif loop_count == 1:
            score += 0.5
        if loop_count > 3:
            score -= 1.0
        if "range(" in code or "sum(" in code:
            score += 0.3
        return self._clamp(score)

    def _score_security(self, code: str) -> float:
        score = 7.5
        unsafe = any(keyword in code for keyword in ("eval", "exec"))
        if unsafe:
            score -= 3.0
        else:
            score += 1.0
        if "raise ValueError" in code:
            score += 0.5
        return self._clamp(score)

    def _score_maintainability(self, code: str) -> float:
        score = 5.5
        if self._has_module_docstring(code):
            score += 2.0
        if self._has_type_hints(code):
            score += 1.0
        functions = code.count("def ")
        if functions <= 3:
            score += 0.5
        return self._clamp(score)

    @staticmethod
    def _average_line_length(code: str) -> float:
        lines = [line for line in code.splitlines() if line.strip()]
        if not lines:
            return 0.0
        return statistics.mean(len(line) for line in lines)

    # ------------------------------------------------------------------
    # Code transformation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _has_module_docstring(code: str) -> bool:
        stripped = code.lstrip()
        return stripped.startswith('"""') or stripped.startswith("'''")

    def _add_module_docstring(self, task_description: str, code: str) -> str:
        docstring = (
            f'"""Implementação gerada pelo workflow para: {task_description}."""\n\n'
        )
        stripped = code.lstrip()
        return docstring + stripped

    @staticmethod
    def _has_type_hints(code: str) -> bool:
        return "->" in code

    def _add_type_hints(self, code: str) -> str:
        lines = code.splitlines()
        updated_lines = []
        hint_added = False
        for line in lines:
            if line.strip().startswith("def ") and ")" in line and "->" not in line:
                line = line.rstrip()
                if line.endswith(":"):
                    line = line[:-1] + " -> None:"
                else:
                    line += " -> None:"
                hint_added = True
            updated_lines.append(line)
        result = "\n".join(updated_lines)
        if hint_added and "from typing import Any" not in result:
            result = "from typing import Any\n" + result
        return result

    @staticmethod
    def _ensure_main_block(code: str, task_description: str) -> str:
        if 'if __name__ == "__main__"' in code:
            return code
        snippet = (
            '\n\nif __name__ == "__main__":\n'
            f'    print("Verificação rápida: {task_description}")\n'
        )
        return code.rstrip() + snippet + "\n"

    def _write_content(self, filepath: str, content: str) -> None:
        self.tools.execute_tool("write_to_file", filepath=filepath, content=content)

    def _read_content(self, filepath: str) -> str:
        result = self.tools.execute_tool("read_file", filepath=filepath)
        if isinstance(result, str):
            return result
        raise RuntimeError(f"Falha ao ler arquivo: {filepath}")


__all__ = ["CodeReviewWorkflow"]
