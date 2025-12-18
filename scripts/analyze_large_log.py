#!/usr/bin/env python3
"""
Análise Inteligente de Logs Grandes - OmniMind
Processa logs de 600K+ linhas de forma eficiente usando streaming e compressão
"""

import gzip
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ErrorSummary:
    """Resumo de erro."""

    pattern: str
    count: int
    first_occurrence: str
    last_occurrence: str
    sample_lines: List[str]


@dataclass
class TestResult:
    """Resultado de teste."""

    name: str
    status: str
    duration: float
    error_msg: Optional[str] = None


@dataclass
class LogMetrics:
    """Métricas do log."""

    total_lines: int
    total_size_mb: float
    errors: Dict[str, ErrorSummary]
    test_results: Dict[str, TestResult]
    timeouts: Dict[int, int]
    warnings: Dict[str, int]
    critical_issues: List[Dict]
    model_references: Dict[str, int]
    summary_stats: Dict


class StreamingLogAnalyzer:
    """Analisador de log que processa em streaming (não carrega tudo na memória)."""

    def __init__(self, log_path: str, chunk_size: int = 10000):
        self.log_path = Path(log_path)
        self.chunk_size = chunk_size

        # Contadores e agregadores
        self.line_count = 0
        self.errors: Dict[str, ErrorSummary] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.timeouts: Counter = Counter()
        self.warnings: Counter = Counter()
        self.model_refs: Counter = Counter()
        self.critical_patterns: List[Dict] = []

        # Padrões de regex compilados (mais eficiente)
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict:
        """Compila padrões regex uma vez para reutilização."""
        return {
            "cuda_oom": re.compile(r"CUDA out of memory", re.IGNORECASE),
            "attribute_error": re.compile(
                r"AttributeError: '(\w+)' object has no attribute '(\w+)'"
            ),
            "timeout": re.compile(r"\b(\d+)\s*(?:s|seconds?|sec)\b.*timeout", re.IGNORECASE),
            "test_passed": re.compile(r"PASSED\s+([^\s]+)"),
            "test_failed": re.compile(r"FAILED\s+([^\s]+)"),
            "test_error": re.compile(r"ERROR\s+([^\s]+)"),
            "test_skipped": re.compile(r"SKIPPED\s+\[?\d+\]?\s+([^\s]+)"),
            "warning": re.compile(r"\[.*?WARNING.*?\]\s+(.+)"),
            "gpt4_re": re.compile(r"gpt-4", re.IGNORECASE),
            "phi_collapse": re.compile(r"Φ collapse|Φ declinou|below threshold", re.IGNORECASE),
            "structural_failure": re.compile(r"Structural Failure|Falha estrutural", re.IGNORECASE),
            "test_summary": re.compile(
                r"=.*?(\d+)\s+failed.*?(\d+)\s+passed.*?(\d+)\s+skipped.*?(\d+)\s+errors",
                re.IGNORECASE,
            ),
        }

    def process_chunk(self, lines: List[str]) -> None:
        """Processa um chunk de linhas."""
        for line in lines:
            self.line_count += 1

            # Erros CUDA OOM
            if self.patterns["cuda_oom"].search(line):
                self._record_error("CUDA_OOM", line)

            # AttributeError
            match = self.patterns["attribute_error"].search(line)
            if match:
                self._record_error(f"AttributeError_{match.group(1)}_{match.group(2)}", line)

            # Timeouts
            match = self.patterns["timeout"].search(line)
            if match:
                timeout_val = int(match.group(1))
                if timeout_val in [30, 60, 90, 120, 240, 300, 400, 600, 800]:
                    self.timeouts[timeout_val] += 1

            # Testes
            for pattern_name, pattern in [
                ("PASSED", self.patterns["test_passed"]),
                ("FAILED", self.patterns["test_failed"]),
                ("ERROR", self.patterns["test_error"]),
                ("SKIPPED", self.patterns["test_skipped"]),
            ]:
                match = pattern.search(line)
                if match:
                    test_name = match.group(1)
                    if test_name not in self.test_results:
                        self.test_results[test_name] = TestResult(
                            name=test_name, status=pattern_name, duration=0.0
                        )

            # Warnings
            match = self.patterns["warning"].search(line)
            if match:
                warning_msg = match.strip()[:100] if hasattr(match, "strip") else str(match)[:100]
                self.warnings[warning_msg] += 1

            # Referências a modelos
            if self.patterns["gpt4_re"].search(line):
                self.model_refs["gpt-4"] += 1
            if "phi:latest" in line.lower() or "ollama/phi" in line.lower():
                self.model_refs["phi"] += 1
            if "qwen" in line.lower():
                self.model_refs["qwen"] += 1

            # Questões críticas
            if self.patterns["phi_collapse"].search(line):
                self.critical_patterns.append(
                    {
                        "type": "phi_collapse",
                        "line": line.strip()[:200],
                        "line_number": self.line_count,
                    }
                )

            if self.patterns["structural_failure"].search(line):
                self.critical_patterns.append(
                    {
                        "type": "structural_failure",
                        "line": line.strip()[:200],
                        "line_number": self.line_count,
                    }
                )

            # Resumo final de testes
            match = self.patterns["test_summary"].search(line)
            if match:
                # Extrair números do resumo final
                pass

    def _record_error(self, error_type: str, line: str) -> None:
        """Registra ocorrência de erro."""
        if error_type not in self.errors:
            self.errors[error_type] = ErrorSummary(
                pattern=error_type,
                count=0,
                first_occurrence=line.strip()[:200],
                last_occurrence=line.strip()[:200],
                sample_lines=[],
            )

        err = self.errors[error_type]
        err.count += 1
        err.last_occurrence = line.strip()[:200]
        if len(err.sample_lines) < 5:
            err.sample_lines.append(line.strip()[:200])

    def analyze_streaming(self) -> LogMetrics:
        """Analisa log em streaming (chunks)."""
        print(f"📊 Analisando log: {self.log_path}")
        print(f"   Tamanho: {self.log_path.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"   Processando em chunks de {self.chunk_size} linhas...")

        chunk = []
        chunk_count = 0

        try:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    chunk.append(line)

                    if len(chunk) >= self.chunk_size:
                        self.process_chunk(chunk)
                        chunk = []
                        chunk_count += 1

                        if chunk_count % 10 == 0:
                            print(
                                f"   Processados: {chunk_count * self.chunk_size:,} linhas...",
                                end="\r",
                            )

                # Processar último chunk
                if chunk:
                    self.process_chunk(chunk)

        except MemoryError:
            print("\n⚠️  Memória insuficiente. Processando com chunks menores...")
            self.chunk_size = self.chunk_size // 2
            return self.analyze_streaming()

        print(f"\n✅ Processamento concluído: {self.line_count:,} linhas")

        # Calcular estatísticas
        total_tests = len(self.test_results)
        passed = sum(1 for t in self.test_results.values() if t.status == "PASSED")
        failed = sum(1 for t in self.test_results.values() if t.status == "FAILED")
        errors = sum(1 for t in self.test_results.values() if t.status == "ERROR")
        skipped = sum(1 for t in self.test_results.values() if t.status == "SKIPPED")

        return LogMetrics(
            total_lines=self.line_count,
            total_size_mb=self.log_path.stat().st_size / 1024 / 1024,
            errors={k: asdict(v) for k, v in self.errors.items()},
            test_results={k: asdict(v) for k, v in self.test_results.items()},
            timeouts=dict(self.timeouts),
            warnings=dict(self.warnings.most_common(50)),
            critical_issues=self.critical_patterns[:100],  # Limitar a 100
            model_references=dict(self.model_refs),
            summary_stats={
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            },
        )


def compress_log(log_path: str, output_path: Optional[str] = None) -> str:
    """Comprime log para análise posterior."""
    log_path_obj = Path(log_path)

    if output_path is None:
        output_path = str(log_path_obj.with_suffix(".log.gz"))

    print("🗜️  Comprimindo log...")
    print(f"   Origem: {log_path_obj.stat().st_size / 1024 / 1024:.1f} MB")

    with open(log_path, "rb") as f_in:
        with gzip.open(output_path, "wb") as f_out:
            f_out.writelines(f_in)

    compressed_size = Path(output_path).stat().st_size / 1024 / 1024
    ratio = (1 - compressed_size / (log_path_obj.stat().st_size / 1024 / 1024)) * 100

    print(f"   Destino: {compressed_size:.1f} MB")
    print(f"   Compressão: {ratio:.1f}%")

    return output_path


def extract_key_sections(log_path: str, output_dir: str) -> Dict[str, str]:
    """Extrai seções-chave do log para análise rápida."""
    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(exist_ok=True)

    sections = {
        "errors": [],
        "failures": [],
        "summary": [],
        "timeouts": [],
        "critical": [],
    }

    print("📋 Extraindo seções-chave do log...")

    _current_section = None
    _buffer = []

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # Detectar seções
            if "ERROR" in line or "CRITICAL" in line:
                sections["errors"].append(line)
                sections["critical"].append(line)
            elif "FAILED" in line:
                sections["failures"].append(line)
            elif "TIMEOUT" in line or "timeout" in line.lower():
                sections["timeouts"].append(line)
            elif "passed" in line.lower() and "failed" in line.lower():
                sections["summary"].append(line)

    # Salvar seções
    for section_name, lines in sections.items():
        if lines:
            output_file = output_dir_obj / f"{section_name}.log"
            with open(output_file, "w", encoding="utf-8") as f:
                f.writelines(lines[:1000])  # Limitar a 1000 linhas por seção
            print(f"   ✅ {section_name}: {len(lines)} linhas → {output_file}")

    return {k: str(output_dir_obj / f"{k}.log") for k, v in sections.items() if v}


def generate_report(metrics: LogMetrics, output_path: str) -> None:
    """Gera relatório JSON completo."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "log_file": str(metrics.total_lines),
        "summary": metrics.summary_stats,
        "errors": metrics.errors,
        "test_results_count": len(metrics.test_results),
        "timeouts": metrics.timeouts,
        "warnings_top_20": dict(list(metrics.warnings.items())[:20]),
        "critical_issues_count": len(metrics.critical_issues),
        "model_references": metrics.model_references,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📊 Relatório salvo em: {output_path}")


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Analisa logs grandes de forma eficiente")
    parser.add_argument("log_path", help="Caminho para o arquivo de log")
    parser.add_argument("--compress", action="store_true", help="Comprimir log após análise")
    parser.add_argument("--extract-sections", action="store_true", help="Extrair seções-chave")
    parser.add_argument("--chunk-size", type=int, default=10000, help="Tamanho do chunk (linhas)")
    parser.add_argument(
        "--output-dir", default="data/test_reports/analysis", help="Diretório de saída"
    )

    args = parser.parse_args()

    log_path = Path(args.log_path)
    if not log_path.exists():
        print(f"❌ Arquivo não encontrado: {log_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extrair seções-chave (opcional, rápido)
    if args.extract_sections:
        _sections = extract_key_sections(str(log_path), str(output_dir / "sections"))
        print(f"\n✅ Seções extraídas em: {output_dir / 'sections'}")

    # 2. Análise streaming completa
    print(f"\n{'='*70}")
    print("ANÁLISE STREAMING COMPLETA")
    print(f"{'='*70}\n")

    analyzer = StreamingLogAnalyzer(str(log_path), chunk_size=args.chunk_size)
    metrics = analyzer.analyze_streaming()

    # 3. Gerar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"analysis_{timestamp}.json"
    generate_report(metrics, str(report_path))

    # 4. Comprimir log (opcional)
    if args.compress:
        compressed_path = compress_log(str(log_path), str(output_dir / f"{log_path.stem}.log.gz"))
        print(f"\n✅ Log comprimido: {compressed_path}")

    # 5. Resumo
    print(f"\n{'='*70}")
    print("📊 RESUMO DA ANÁLISE")
    print(f"{'='*70}")
    print(f"Total de linhas: {metrics.total_lines:,}")
    print(f"Tamanho: {metrics.total_size_mb:.1f} MB")
    print("\nTestes:")
    print(f"  ✅ Passou: {metrics.summary_stats['passed']}")
    print(f"  ❌ Falhou: {metrics.summary_stats['failed']}")
    print(f"  ⚠️  Erros: {metrics.summary_stats['errors']}")
    print(f"  ⏭️  Pulados: {metrics.summary_stats['skipped']}")
    print(f"  📈 Taxa de sucesso: {metrics.summary_stats['success_rate']:.1f}%")
    print(f"\nPadrões de erro: {len(metrics.errors)}")
    print(f"Timeouts detectados: {len(metrics.timeouts)}")
    print(f"Questões críticas: {len(metrics.critical_issues)}")
    print(f"\n📄 Relatório completo: {report_path}")


if __name__ == "__main__":
    main()
