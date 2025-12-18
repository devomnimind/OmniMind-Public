#!/usr/bin/env python3
"""
Análise Inteligente de Log de Testes - OmniMind
Extrai padrões críticos de logs grandes (600K+ linhas)
"""

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class ErrorPattern:
    """Padrão de erro encontrado."""

    category: str
    message: str
    count: int
    examples: List[str]
    related_tests: Set[str]


@dataclass
class TimeoutInfo:
    """Informação sobre timeouts."""

    value: int
    count: int
    contexts: List[str]
    test_names: Set[str]


@dataclass
class TestStatus:
    """Status de um teste."""

    name: str
    status: str  # PASSED, FAILED, ERROR, SKIPPED
    duration: float
    error_msg: str = ""


class LogAnalyzer:
    """Analisador inteligente de logs de teste."""

    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.errors: Dict[str, ErrorPattern] = {}
        self.timeouts: Dict[int, TimeoutInfo] = {}
        self.test_results: Dict[str, TestStatus] = {}
        self.warnings: Counter = Counter()
        self.critical_issues: List[str] = []
        self.model_references: Dict[str, int] = defaultdict(int)

    def analyze(self) -> Dict:
        """Executa análise completa do log."""
        print(f"📊 Analisando log: {self.log_path}")
        print(f"   Tamanho: {self.log_path.stat().st_size / 1024 / 1024:.1f} MB")

        with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        print(f"   Linhas: {len(lines):,}")
        print("   Processando...")

        # Análises paralelas
        self._extract_errors(lines)
        self._extract_timeouts(lines)
        self._extract_test_results(lines)
        self._extract_warnings(lines)
        self._extract_model_references(lines)
        self._extract_critical_issues(lines)

        return self._generate_report()

    def _extract_errors(self, lines: List[str]):
        """Extrai padrões de erro com classificação dinâmica."""
        error_patterns = {
            "CUDA_OOM": r"CUDA out of memory",
            "AttributeError": r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
            "TimeoutError": r"TimeoutError|TIMEOUT|timeout",
            "ConnectionError": r"ConnectionError|Failed to connect",
            "AssertionError": r"AssertionError",
            "ModuleNotFound": r"ModuleNotFoundError|No module named",
            "PhiCollapse": r"Φ collapse|Φ declinou|below threshold",
            "StructuralFailure": r"Structural Failure|Falha estrutural",
            # Entropy warnings - detecta quando entropia excede limites
            "EntropyWarning": r"entropy.*exceeds.*bekenstein.*bound|entropy.*warning|WARNING.*entropy|entropy.*threshold.*exceeded",
            # Meta cognition failures - CRÍTICO: não executar testes
            "MetacognitionAnalysisFailed": r"meta.*cogn.*analysis.*failed|metacognition.*analysis.*failed|failed.*load.*hash.*chain",
            "MetacognitionActionFailed": r"meta.*cogn.*action.*failed|metacognition.*action.*failed",
            # Insufficient history - dados insuficientes para cálculos
            "InsufficientHistory": r"insufficient.*history|history.*insufficient|insufficient.*data|insufficient.*history.*\(.*<.*\)|insufficient.*aligned.*history|insufficient.*valid.*causal.*predictions",
            # Padrões numéricos de insufficient history (ex: "4<10", "7<70")
            "InsufficientHistoryNumeric": r"(\d+)\s*<\s*(\d+).*insufficient|insufficient.*\((\d+)\s*<\s*(\d+)\)",
        }

        for pattern_name, pattern in error_patterns.items():
            matches = []
            test_names = set()

            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(line.strip())
                    # Tentar extrair nome do teste
                    if i > 0:
                        test_match = re.search(r"tests/[^:]+::[^:]+::(\w+)", lines[i - 1])
                        if test_match:
                            test_names.add(test_match.group(1))
                    if len(matches) >= 10:  # Limitar exemplos
                        break

            if matches:
                self.errors[pattern_name] = ErrorPattern(
                    category=pattern_name,
                    message=matches[0][:200],
                    count=len([l for l in lines if re.search(pattern, l, re.IGNORECASE)]),
                    examples=matches[:5],
                    related_tests=test_names,
                )

    def _extract_timeouts(self, lines: List[str]):
        """Extrai informações sobre timeouts."""
        timeout_values = [30, 60, 90, 120, 240, 300, 400, 600, 800]

        for timeout_val in timeout_values:
            pattern = rf"\b{timeout_val}\s*(?:s|seconds?|sec)\b"
            matches = []
            contexts = []
            test_names = set()

            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(line.strip())
                    contexts.append(line.strip()[:150])
                    # Extrair contexto do teste
                    for j in range(max(0, i - 5), min(len(lines), i + 5)):
                        test_match = re.search(r"tests/[^:]+::[^:]+::(\w+)", lines[j])
                        if test_match:
                            test_names.add(test_match.group(1))
                    if len(contexts) >= 10:
                        break

            if matches:
                self.timeouts[timeout_val] = TimeoutInfo(
                    value=timeout_val,
                    count=len(matches),
                    contexts=contexts[:5],
                    test_names=test_names,
                )

    def _extract_test_results(self, lines: List[str]):
        """Extrai resultados de testes."""
        # Padrões pytest
        passed_pattern = r"PASSED\s+([^\s]+)"
        failed_pattern = r"FAILED\s+([^\s]+)"
        error_pattern = r"ERROR\s+([^\s]+)"
        skipped_pattern = r"SKIPPED\s+\[?\d+\]?\s+([^\s]+)"

        for line in lines:
            # PASSED
            for match in re.finditer(passed_pattern, line):
                test_name = match.group(1)
                self.test_results[test_name] = TestStatus(
                    name=test_name, status="PASSED", duration=0.0
                )

            # FAILED
            for match in re.finditer(failed_pattern, line):
                test_name = match.group(1)
                self.test_results[test_name] = TestStatus(
                    name=test_name, status="FAILED", duration=0.0
                )

            # ERROR
            for match in re.finditer(error_pattern, line):
                test_name = match.group(1)
                self.test_results[test_name] = TestStatus(
                    name=test_name, status="ERROR", duration=0.0
                )

            # SKIPPED
            for match in re.finditer(skipped_pattern, line):
                test_name = match.group(1)
                self.test_results[test_name] = TestStatus(
                    name=test_name, status="SKIPPED", duration=0.0
                )

    def _extract_warnings(self, lines: List[str]):
        """Extrai warnings."""
        warning_pattern = r"\[.*?WARNING.*?\]\s+(.+)"

        for line in lines:
            match = re.search(warning_pattern, line)
            if match:
                warning_msg = match.group(1).strip()[:100]
                self.warnings[warning_msg] += 1

    def _extract_model_references(self, lines: List[str]):
        """Extrai referências a modelos."""
        model_patterns = [
            r"gpt-4",
            r"phi:latest",
            r"qwen",
            r"ollama/",
            r"hf/",
            r"gemini",
            r"claude",
        ]

        for pattern in model_patterns:
            count = sum(1 for line in lines if re.search(pattern, line, re.IGNORECASE))
            if count > 0:
                self.model_references[pattern] = count

    def _extract_critical_issues(self, lines: List[str]):
        """Extrai questões críticas."""
        critical_patterns = [
            (r"gpt-4", "Referência incorreta a modelo gpt-4 (não existe no projeto)"),
            (
                r"timeout.*30\s*(?:s|sec)",
                "Timeout de 30s detectado (deveria ser 800s para testes reais)",
            ),
            (r"timeout.*60\s*(?:s|sec)", "Timeout de 60s detectado (verificar se é adequado)"),
            (r"CUDA out of memory", "CUDA OOM - problema de memória GPU"),
            (r"Φ collapse", "Colapso de Φ - problema crítico de consciência"),
        ]

        for pattern, description in critical_patterns:
            matches = [line.strip() for line in lines if re.search(pattern, line, re.IGNORECASE)]
            if matches:
                self.critical_issues.append(
                    {
                        "pattern": pattern,
                        "description": description,
                        "count": len(matches),
                        "example": matches[0][:200] if matches else "",
                    }
                )

    def _generate_report(self) -> Dict:
        """Gera relatório completo."""
        total_tests = len(self.test_results)
        passed = sum(1 for t in self.test_results.values() if t.status == "PASSED")
        failed = sum(1 for t in self.test_results.values() if t.status == "FAILED")
        errors = sum(1 for t in self.test_results.values() if t.status == "ERROR")
        skipped = sum(1 for t in self.test_results.values() if t.status == "SKIPPED")

        # Converter sets para listas para serialização JSON
        errors_dict = {}
        for k, v in self.errors.items():
            err_dict = asdict(v)
            err_dict["related_tests"] = list(err_dict["related_tests"])
            errors_dict[k] = err_dict

        timeouts_dict = {}
        for k, v in self.timeouts.items():
            timeout_dict = asdict(v)
            timeout_dict["test_names"] = list(timeout_dict["test_names"])
            timeouts_dict[k] = timeout_dict

        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            },
            "errors": errors_dict,
            "timeouts": timeouts_dict,
            "warnings": dict(self.warnings.most_common(20)),
            "model_references": dict(self.model_references),
            "critical_issues": self.critical_issues,
            "test_status_counts": {
                "PASSED": passed,
                "FAILED": failed,
                "ERROR": errors,
                "SKIPPED": skipped,
            },
        }


def main():
    """Função principal."""
    import sys

    log_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "data/test_reports/consolidated_fast_20251207_120233.log"
    )

    analyzer = LogAnalyzer(log_path)
    report = analyzer.analyze()

    # Salvar relatório JSON
    output_path = (
        Path(log_path).parent / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Análise concluída!")
    print(f"   Relatório salvo em: {output_path}")
    print(f"\n📊 Resumo:")
    print(f"   Total de testes: {report['summary']['total_tests']}")
    print(f"   ✅ Passou: {report['summary']['passed']}")
    print(f"   ❌ Falhou: {report['summary']['failed']}")
    print(f"   ⚠️  Erros: {report['summary']['errors']}")
    print(f"   ⏭️  Pulados: {report['summary']['skipped']}")
    print(f"   📈 Taxa de sucesso: {report['summary']['success_rate']:.1f}%")
    print(f"\n🔍 Padrões de erro encontrados: {len(report['errors'])}")
    print(f"⏱️  Timeouts detectados: {len(report['timeouts'])}")
    print(f"⚠️  Questões críticas: {len(report['critical_issues'])}")


if __name__ == "__main__":
    main()
