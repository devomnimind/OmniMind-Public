from __future__ import annotations

import json
from typing import Any, Dict
from ..tools.omnimind_tools import ToolsFramework
from .code_agent import CodeAgent
from .react_agent import ReactAgent

#!/usr/bin/env python3

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
ReviewerAgent - Agente crítico com RLAIF scoring
Modo: reviewer (⭐)

Função: Avalia código/resultados com score 0-10
Critérios: correctness, readability, efficiency, security
Gera feedback detalhado para refinamento (RLAIF loop)
"""


class ReviewerAgent(ReactAgent):
    """Agente revisor com RLAIF (Reinforcement Learning from AI Feedback)"""

    def __init__(self, config_path: str) -> None:
        super().__init__(config_path)
        self.tools_framework = ToolsFramework()
        self.mode = "reviewer"

        # Critérios de avaliação
        self.criteria: Dict[str, str] = {
            "correctness": "Does it work correctly?",
            "readability": "Is it clean and understandable?",
            "efficiency": "Is it performant?",
            "security": "Is it secure?",
            "maintainability": "Is it maintainable?",
        }

    def review_code(self, filepath: str, task_description: str) -> Dict[str, Any]:
        """Revisa código e retorna score + feedback"""
        try:
            # Ler código
            code_content = self.tools_framework.execute_tool("read_file", filepath=filepath)

            # Analisar
            analysis = self.tools_framework.execute_tool("analyze_code", filepath=filepath)

            # Gerar review via LLM
            prompt = f"""You are ReviewerAgent ⭐, an expert code reviewer using RLAIF scoring.

TASK: {task_description}
FILE: {filepath}

CODE TO REVIEW:
```
{code_content[:1000]}...
```

AUTOMATED ANALYSIS:
{json.dumps(analysis, indent=2)}

REVIEW CRITERIA (score each 0-10):
{chr(10).join([f"- {k}: {v}" for k, v in self.criteria.items()])}

Provide detailed review in this format:

SCORES:
correctness: <0-10>
readability: <0-10>
efficiency: <0-10>
security: <0-10>
maintainability: <0-10>

OVERALL_SCORE: <average>

STRENGTHS:
- <point 1>
- <point 2>

WEAKNESSES:
- <issue 1>
- <issue 2>

SUGGESTIONS:
- <improvement 1>
- <improvement 2>

CRITICAL_ISSUES:
- <blocker if any>

Your review:"""

            response = self.llm.invoke(prompt)

            # Parsear scores
            scores = self._parse_scores(response)
            overall = scores.get(
                "OVERALL_SCORE", sum(scores.values()) / len(scores) if scores else 5.0
            )

            review = {
                "filepath": filepath,
                "task": task_description,
                "scores": scores,
                "overall_score": overall,
                "passed": overall >= 7.0,
                "feedback": response,
                "timestamp": self._timestamp(),
            }

            # Armazenar feedback
            self.tools_framework.execute_tool(
                "collect_feedback", feedback_type="code_review", data=review
            )

            return review

        except Exception as e:
            return {"error": str(e), "overall_score": 0.0, "passed": False}

    def _parse_scores(self, response: str) -> Dict[str, float]:
        """Extrai scores do texto"""
        scores: Dict[str, float] = {}
        for line in response.split("\n"):
            for criterion in self.criteria.keys():
                if criterion in line.lower() and ":" in line:
                    try:
                        score_str = line.split(":")[1].strip().split()[0]
                        scores[criterion] = float(score_str)
                    except (ValueError, IndexError):
                        continue
            if "OVERALL_SCORE:" in line or "overall:" in line.lower():
                try:
                    score_str = line.split(":")[1].strip().split()[0]
                    scores["OVERALL_SCORE"] = float(score_str)
                except (ValueError, IndexError):
                    continue
        return scores

    def run_review_cycle(
        self, coder_agent: CodeAgent, task: str, max_attempts: int = 3
    ) -> Dict[str, Any]:
        """Executa loop RLAIF: Code → Review → Refine"""
        attempt = 0
        best_score = 0.0
        best_result = None

        while attempt < max_attempts:
            attempt += 1

            # Coder gera código
            code_result = coder_agent.run_code_task(task)

            # Reviewer avalia
            if code_result.get("completed"):
                # Assumir que criou arquivo
                filepath = f"generated_code_{attempt}.py"
                review = self.review_code(filepath, task)

                score = review.get("overall_score", 0.0)

                if score >= 7.0:
                    return {
                        "success": True,
                        "attempts": attempt,
                        "final_score": score,
                        "review": review,
                    }

                if score > best_score:
                    best_score = score
                    best_result = review

                # Feedback para próxima iteração
                task = f"{task}\n\nPREVIOUS FEEDBACK:\n{review['feedback']}"

        return {
            "success": False,
            "attempts": attempt,
            "best_score": best_score,
            "best_review": best_result,
        }


__all__ = ["ReviewerAgent"]
