#!/usr/bin/env python3
"""
MCP 4340: Perfil de Modelo (Model Profile)
Mantém histórico de decisões e padrões do modelo
- Entrada: Decisões capturadas
- Saída: Padrões identificados, preferências, histórico
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


class ModelProfile:
    """Perfil do modelo com histórico e padrões."""

    def __init__(self, model_name: str = "omnimind-agent"):
        self.model_name = model_name
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

        # Histórico de decisões
        self.decision_history: List[Dict[str, Any]] = []

        # Padrões identificados
        self.patterns: Dict[str, Any] = {
            "preferred_approaches": {},  # abordagem -> freq
            "confidence_distribution": [],  # [min_conf, max_conf, count]
            "error_patterns": [],  # tipos de erro comuns
            "successful_strategies": [],  # estratégias bem-sucedidas
        }

        # Estatísticas
        self.stats = {
            "total_decisions": 0,
            "avg_confidence": 0.0,
            "success_rate": 0.0,
            "error_rate": 0.0,
            "total_reasoning_steps": 0,
        }

    def record_decision(
        self,
        decision_type: str,
        outcome: str,
        confidence: float,
        reasoning_steps: int = 0,
    ) -> Dict[str, Any]:
        """Registra uma decisão no perfil."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "type": decision_type,
            "outcome": outcome,  # "success", "partial", "failure"
            "confidence": confidence,
            "reasoning_steps": reasoning_steps,
        }

        self.decision_history.append(record)
        self.updated_at = datetime.now().isoformat()

        # Atualizar padrões
        self._update_patterns(record)

        # Atualizar estatísticas
        self._update_stats()

        return record

    def _update_patterns(self, record: Dict[str, Any]) -> None:
        """Atualiza padrões com base em novo registro."""
        # Registrar estratégia preferida
        if record["type"] not in self.patterns["preferred_approaches"]:
            self.patterns["preferred_approaches"][record["type"]] = 0
        self.patterns["preferred_approaches"][record["type"]] += 1

        # Registrar sucesso/erro
        if record["outcome"] == "success":
            if record["type"] not in self.patterns["successful_strategies"]:
                self.patterns["successful_strategies"].append(record["type"])
        else:
            if record["outcome"] not in self.patterns["error_patterns"]:
                self.patterns["error_patterns"].append(record["outcome"])

    def _update_stats(self) -> None:
        """Recalcula estatísticas."""
        if not self.decision_history:
            return

        total = len(self.decision_history)
        self.stats["total_decisions"] = total

        # Confiança média
        confidences = [d["confidence"] for d in self.decision_history]
        self.stats["avg_confidence"] = sum(confidences) / total if confidences else 0

        # Taxa de sucesso
        successes = sum(1 for d in self.decision_history if d["outcome"] == "success")
        self.stats["success_rate"] = successes / total if total > 0 else 0

        # Taxa de erro
        errors = sum(1 for d in self.decision_history if d["outcome"] == "failure")
        self.stats["error_rate"] = errors / total if total > 0 else 0

        # Total de passos
        self.stats["total_reasoning_steps"] = sum(
            d["reasoning_steps"] for d in self.decision_history
        )

    def get_profile(self) -> Dict[str, Any]:
        """Retorna o perfil completo."""
        return {
            "model_name": self.model_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "statistics": self.stats,
            "patterns": self.patterns,
            "decision_count": len(self.decision_history),
        }

    def get_profile_summary(self) -> str:
        """Retorna sumário legível do perfil."""
        profile = self.get_profile()
        top_strategies = (
            ", ".join(self.patterns["successful_strategies"][:5])
            if self.patterns["successful_strategies"]
            else "None yet"
        )
        common_errors = (
            ", ".join(list(set(self.patterns["error_patterns"]))[:5])
            if self.patterns["error_patterns"]
            else "None yet"
        )

        return f"""
Model Profile: {self.model_name}
Created: {self.created_at}
Updated: {self.updated_at}

Statistics:
  • Total Decisions: {profile['statistics']['total_decisions']}
  • Avg Confidence: {profile['statistics']['avg_confidence']:.2%}
  • Success Rate: {profile['statistics']['success_rate']:.2%}
  • Error Rate: {profile['statistics']['error_rate']:.2%}
  • Total Reasoning Steps: {profile['statistics']['total_reasoning_steps']}

Top Strategies:
    {top_strategies}

Common Errors:
    {common_errors}
        """

    def export_profile(self, filepath: str) -> None:
        """Exporta perfil para JSON."""
        profile = self.get_profile()
        profile["history"] = self.decision_history[:100]  # Últimas 100
        with open(filepath, "w") as f:
            json.dump(profile, f, indent=2)
        logger.info(f"Profile exported to {filepath}")


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    profile = ModelProfile("omnimind-test")
    logger.info("✅ Model Profile Service initialized")

    # Exemplos
    profile.record_decision("classification", "success", 0.95, 5)
    profile.record_decision("classification", "success", 0.92, 4)
    profile.record_decision("classification", "failure", 0.65, 8)
    profile.record_decision("reasoning", "success", 0.88, 12)
    profile.record_decision("reasoning", "success", 0.91, 11)

    logger.info(profile.get_profile_summary())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
