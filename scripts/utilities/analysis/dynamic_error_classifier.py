#!/usr/bin/env python3
"""
Dynamic Error Classifier for OmniMind Test Logs

Classifica erros dinamicamente baseado em padrões, incluindo:
- Entropy warnings
- Meta cognition analysis/action failures (CRÍTICO - não executar testes)
- Erros padrão (AssertionError, AttributeError, etc.)

Author: Fabrício da Silva + assistência de IA
Date: 2025-12-07
"""

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ErrorClassification:
    """Classificação de um erro."""

    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    message: str
    pattern_matched: str
    should_block_tests: bool = False
    recommendation: str = ""


class DynamicErrorClassifier:
    """Classificador dinâmico de erros baseado em padrões."""

    ERROR_CATEGORIES = {
        "ASSERTION": {
            "patterns": [r"AssertionError", r"assert False", r"assert\s+\w+\s*=="],
            "severity": "HIGH",
            "block_tests": False,
        },
        "ATTRIBUTE": {
            "patterns": [r"AttributeError: '(\w+)' object has no attribute '(\w+)'"],
            "severity": "HIGH",
            "block_tests": False,
        },
        "VALUE": {
            "patterns": [r"ValueError", r"wrong shape", r"invalid value"],
            "severity": "MEDIUM",
            "block_tests": False,
        },
        "MEMORY": {
            "patterns": [r"CUDA out of memory", r"OutOfMemoryError"],
            "severity": "HIGH",
            "block_tests": False,
        },
        "TIMEOUT": {
            "patterns": [r"TimeoutError", r"TIMEOUT", r"timed out"],
            "severity": "MEDIUM",  # Timeout é medição, não erro
            "block_tests": False,
        },
        "ENTROPY_WARNING": {
            "patterns": [
                r"entropy.*exceeds.*bekenstein.*bound",
                r"entropy.*warning",
                r"WARNING.*entropy",
                r"entropy.*threshold.*exceeded",
            ],
            "severity": "MEDIUM",
            "block_tests": False,
        },
        "METACOGNITION_ANALYSIS_FAILED": {
            "patterns": [
                r"meta.*cogn.*analysis.*failed",
                r"metacognition.*analysis.*failed",
                r"failed.*load.*hash.*chain",
            ],
            "severity": "CRITICAL",
            "block_tests": True,  # CRÍTICO: não executar testes
        },
        "METACOGNITION_ACTION_FAILED": {
            "patterns": [
                r"meta.*cogn.*action.*failed",
                r"metacognition.*action.*failed",
            ],
            "severity": "CRITICAL",
            "block_tests": True,  # CRÍTICO: não executar testes
        },
        "INSUFFICIENT_HISTORY": {
            "patterns": [
                r"insufficient.*history",
                r"history.*insufficient",
                r"insufficient.*data",
                r"insufficient.*aligned.*history",
                r"insufficient.*valid.*causal.*predictions",
                r"(\d+)\s*<\s*(\d+).*insufficient",
                r"insufficient.*\((\d+)\s*<\s*(\d+)\)",
            ],
            "severity": "MEDIUM",
            "block_tests": False,  # Não bloqueia, mas indica necessidade de mais dados
        },
    }

    CRITICAL_CATEGORIES = [
        "METACOGNITION_ANALYSIS_FAILED",
        "METACOGNITION_ACTION_FAILED",
    ]

    def __init__(self):
        """Inicializa classificador."""
        self.classifications: List[ErrorClassification] = []
        self.category_counts = Counter()
        self.blocking_errors: List[ErrorClassification] = []

    def classify_error(
        self, error_message: str, context: Optional[str] = None
    ) -> Optional[ErrorClassification]:
        """
        Classifica erro dinamicamente.

        Args:
            error_message: Mensagem de erro
            context: Contexto adicional (opcional)

        Returns:
            ErrorClassification ou None se não classificado
        """
        _error_lower = error_message.lower()

        for category, config in self.ERROR_CATEGORIES.items():
            for pattern in config["patterns"]:
                if re.search(pattern, error_message, re.IGNORECASE):
                    classification = ErrorClassification(
                        category=category,
                        severity=config["severity"],
                        message=error_message[:200],
                        pattern_matched=pattern,
                        should_block_tests=config["block_tests"],
                        recommendation=self._get_recommendation(category, error_message),
                    )

                    self.classifications.append(classification)
                    self.category_counts[category] += 1

                    if classification.should_block_tests:
                        self.blocking_errors.append(classification)

                    return classification

        return None

    def _get_recommendation(self, category: str, error_message: str) -> str:
        """Gera recomendação baseada na categoria."""
        recommendations = {
            "METACOGNITION_ANALYSIS_FAILED": (
                "CRITICAL: Meta cognition analysis failed - "
                "NÃO EXECUTAR TESTES até resolver problema de meta cognição"
            ),
            "METACOGNITION_ACTION_FAILED": (
                "CRITICAL: Meta cognition action failed - "
                "NÃO EXECUTAR TESTES até resolver problema de meta cognição"
            ),
            "ENTROPY_WARNING": (
                "WARNING: Entropy exceeds Bekenstein bound - " "Monitorar estabilidade do sistema"
            ),
            "MEMORY": (
                "HIGH: CUDA out of memory - " "Verificar uso de GPU e considerar limpeza de memória"
            ),
            "ATTRIBUTE": (
                "HIGH: AttributeError - "
                "Verificar se objeto tem atributo esperado ou se há incompatibilidade de versão"
            ),
            "ASSERTION": (
                "HIGH: AssertionError - " "Verificar lógica do teste ou condições de execução"
            ),
            "INSUFFICIENT_HISTORY": (
                "MEDIUM: Insufficient history - "
                "Dados insuficientes para cálculos completos. Executar mais ciclos/tasks para acumular histórico."
            ),
        }

        return recommendations.get(category, f"Erro classificado como {category}")

    def classify_log_file(self, log_lines: List[str]) -> Dict[str, Any]:
        """
        Classifica erros de um arquivo de log completo.

        Args:
            log_lines: Lista de linhas do log

        Returns:
            Dicionário com classificações e estatísticas
        """
        for line in log_lines:
            # Procurar por padrões de erro
            if re.search(r"ERROR|FAILED|Exception|Traceback", line, re.IGNORECASE):
                self.classify_error(line)

        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das classificações."""
        total = len(self.classifications)
        critical = len([c for c in self.classifications if c.severity == "CRITICAL"])
        blocking = len(self.blocking_errors)

        return {
            "total_classifications": total,
            "critical_count": critical,
            "blocking_count": blocking,
            "should_block_tests": blocking > 0,
            "category_counts": dict(self.category_counts),
            "blocking_errors": [
                {
                    "category": e.category,
                    "message": e.message,
                    "recommendation": e.recommendation,
                }
                for e in self.blocking_errors[:10]  # Top 10
            ],
            "severity_breakdown": {
                "CRITICAL": len([c for c in self.classifications if c.severity == "CRITICAL"]),
                "HIGH": len([c for c in self.classifications if c.severity == "HIGH"]),
                "MEDIUM": len([c for c in self.classifications if c.severity == "MEDIUM"]),
                "LOW": len([c for c in self.classifications if c.severity == "LOW"]),
                "INFO": len([c for c in self.classifications if c.severity == "INFO"]),
            },
        }

    def should_block_test_execution(self) -> bool:
        """
        Verifica se execução de testes deve ser bloqueada.

        Returns:
            True se meta cognition failures foram detectados
        """
        return len(self.blocking_errors) > 0

    def get_blocking_reasons(self) -> List[str]:
        """Retorna lista de razões para bloquear testes."""
        return [e.recommendation for e in self.blocking_errors]


def main():
    """Função principal para teste."""
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Uso: python dynamic_error_classifier.py <log_file>")
        sys.exit(1)

    log_path = Path(sys.argv[1])
    if not log_path.exists():
        print(f"Arquivo não encontrado: {log_path}")
        sys.exit(1)

    classifier = DynamicErrorClassifier()

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    summary = classifier.classify_log_file(lines)

    print("=" * 70)
    print("📊 CLASSIFICAÇÃO DINÂMICA DE ERROS")
    print("=" * 70)
    print(f"\nTotal de classificações: {summary['total_classifications']}")
    print(f"Erros críticos: {summary['critical_count']}")
    print(f"Erros bloqueantes: {summary['blocking_count']}")
    print(f"Bloquear testes: {'SIM' if summary['should_block_tests'] else 'NÃO'}")

    print("\n📊 Distribuição por Severidade:")
    for severity, count in summary["severity_breakdown"].items():
        print(f"   {severity}: {count}")

    print("\n📊 Distribuição por Categoria:")
    for category, count in summary["category_counts"].items():
        print(f"   {category}: {count}")

    if summary["blocking_errors"]:
        print("\n🔴 ERROS BLOQUEANTES (NÃO EXECUTAR TESTES):")
        for i, error in enumerate(summary["blocking_errors"], 1):
            print(f"\n   {i}. {error['category']}")
            print(f"      Mensagem: {error['message'][:100]}")
            print(f"      Recomendação: {error['recommendation']}")


if __name__ == "__main__":
    main()
