#!/usr/bin/env python3
"""
MCP 4341: Inteligência Comparativa (Comparative Intelligence)
Compara modelos, identifica pontos fortes/fracos, faz recomendações
- Entrada: Perfis de múltiplos modelos
- Saída: Comparações, recomendações, análise
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


class ComparativeIntelligence:
    """Inteligência comparativa entre modelos."""

    def __init__(self):
        self.created_at = datetime.now().isoformat()
        self.model_profiles: Dict[str, Dict[str, Any]] = {}
        self.comparisons: List[Dict[str, Any]] = []

    def add_model_profile(self, model_name: str, profile_data: Dict[str, Any]) -> None:
        """Adiciona perfil de um modelo."""
        self.model_profiles[model_name] = profile_data
        logger.info(f"Added profile for model: {model_name}")

    def compare_success_rates(self) -> Dict[str, float]:
        """Compara taxa de sucesso entre modelos."""
        comparison = {}
        for name, profile in self.model_profiles.items():
            stats = profile.get("statistics", {})
            success_rate = stats.get("success_rate", 0)
            comparison[name] = success_rate

        # Ordenar por taxa de sucesso
        sorted_comparison = dict(sorted(comparison.items(), key=lambda x: x[1], reverse=True))
        return sorted_comparison

    def compare_confidence(self) -> Dict[str, float]:
        """Compara confiança média entre modelos."""
        comparison = {}
        for name, profile in self.model_profiles.items():
            stats = profile.get("statistics", {})
            avg_conf = stats.get("avg_confidence", 0)
            comparison[name] = avg_conf

        sorted_comparison = dict(sorted(comparison.items(), key=lambda x: x[1], reverse=True))
        return sorted_comparison

    def identify_strengths_weaknesses(self, model_name: str) -> Dict[str, List[str]]:
        """Identifica pontos fortes e fracos de um modelo."""
        if model_name not in self.model_profiles:
            return {"strengths": [], "weaknesses": []}

        profile = self.model_profiles[model_name]
        stats = profile.get("statistics", {})
        patterns = profile.get("patterns", {})

        strengths = []
        weaknesses = []

        # Análise de força
        if stats.get("success_rate", 0) > 0.85:
            strengths.append("High success rate")
        if stats.get("avg_confidence", 0) > 0.80:
            strengths.append("High confidence")
        if patterns.get("successful_strategies"):
            strengths.append(f"Strong in: {', '.join(patterns['successful_strategies'][:2])}")

        # Análise de fraqueza
        if stats.get("error_rate", 0) > 0.15:
            weaknesses.append("High error rate")
        if stats.get("avg_confidence", 0) < 0.70:
            weaknesses.append("Low confidence")
        if patterns.get("error_patterns"):
            error_list = list(set(patterns["error_patterns"]))[:2]
            weaknesses.append(f"Issues with: {', '.join(error_list)}")

        return {"strengths": strengths, "weaknesses": weaknesses}

    def make_recommendations(self) -> Dict[str, List[str]]:
        """Faz recomendações para cada modelo."""
        recommendations = {}

        for model_name in self.model_profiles.keys():
            recs = []
            analysis = self.identify_strengths_weaknesses(model_name)

            # Recomendações baseadas em fraquezas
            if "High error rate" in analysis["weaknesses"]:
                recs.append("Focus on error handling and validation")
            if "Low confidence" in analysis["weaknesses"]:
                recs.append("Improve decision confidence through better training")
            if not analysis["strengths"]:
                recs.append("Model needs overall improvement")

            # Recomendações baseadas em comparação
            success_rates = self.compare_success_rates()
            if success_rates:
                best_model = list(success_rates.keys())[0]
                if model_name != best_model:
                    best_rate = success_rates[best_model]
                    current_rate = success_rates.get(model_name, 0)
                    gap = best_rate - current_rate
                    if gap > 0.10:
                        recs.append(f"Study strategies from {best_model} (gap: {gap:.1%})")

            recommendations[model_name] = recs

        return recommendations

    def generate_comparison_report(self) -> Dict[str, Any]:
        """Gera relatório completo de comparação."""
        return {
            "timestamp": datetime.now().isoformat(),
            "model_count": len(self.model_profiles),
            "success_rates": self.compare_success_rates(),
            "confidence_levels": self.compare_confidence(),
            "strengths_weaknesses": {
                name: self.identify_strengths_weaknesses(name)
                for name in self.model_profiles.keys()
            },
            "recommendations": self.make_recommendations(),
        }

    def export_comparison_report(self, filepath: str) -> None:
        """Exporta relatório de comparação."""
        report = self.generate_comparison_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Comparison report exported to {filepath}")


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    comp = ComparativeIntelligence()
    logger.info("✅ Comparative Intelligence Service initialized")

    # Exemplo
    comp.add_model_profile(
        "Model A",
        {
            "statistics": {
                "success_rate": 0.95,
                "avg_confidence": 0.88,
                "error_rate": 0.05,
            },
            "patterns": {
                "successful_strategies": ["classification", "reasoning"],
                "error_patterns": [],
            },
        },
    )

    comp.add_model_profile(
        "Model B",
        {
            "statistics": {
                "success_rate": 0.82,
                "avg_confidence": 0.75,
                "error_rate": 0.18,
            },
            "patterns": {
                "successful_strategies": ["classification"],
                "error_patterns": ["timeout", "out_of_memory"],
            },
        },
    )

    report = comp.generate_comparison_report()
    logger.info(f"Comparison report:\n{json.dumps(report, indent=2)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
