#!/usr/bin/env python3
"""
Análise de Cobertura de Testes - OmniMind

Este script analisa os relatórios de cobertura gerados pelo pytest-cov
e fornece insights sobre a qualidade da cobertura de testes.

Uso:
    python scripts/analyze_test_coverage.py

Requisitos:
    - pytest-cov deve estar instalado
    - Relatório JSON deve existir: data/test_reports/coverage.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import statistics


class CoverageAnalyzer:
    """Analisador de cobertura de testes."""

    def __init__(self, coverage_file: Path):
        """
        Inicializa o analisador.

        Args:
            coverage_file: Caminho para o arquivo coverage.json
        """
        self.coverage_file = coverage_file
        self.data = None

    def load_coverage(self) -> bool:
        """Carrega dados de cobertura do arquivo JSON."""
        try:
            with open(self.coverage_file, "r") as f:
                self.data = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar cobertura: {e}")
            return False

    def get_overall_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais de cobertura."""
        if not self.data:
            return {}

        totals = self.data.get("totals", {})
        return {
            "percent_covered": totals.get("percent_covered", 0),
            "num_statements": totals.get("num_statements", 0),
            "covered_statements": totals.get("covered_statements", 0),
            "missing_statements": totals.get("missing_statements", 0),
            "excluded_statements": totals.get("excluded_statements", 0),
        }

    def get_file_coverage(self) -> List[Tuple[str, float]]:
        """Retorna cobertura por arquivo, ordenada por cobertura."""
        if not self.data:
            return []

        files = []
        for file_path, file_data in self.data.get("files", {}).items():
            summary = file_data.get("summary", {})
            percent = summary.get("percent_covered", 0)
            files.append((file_path, percent))

        return sorted(files, key=lambda x: x[1])

    def get_uncovered_lines(self, file_path: str) -> List[int]:
        """Retorna linhas não cobertas por testes em um arquivo."""
        if not self.data or file_path not in self.data.get("files", {}):
            return []

        file_data = self.data["files"][file_path]
        return file_data.get("missing_lines", [])

    def analyze_coverage_distribution(self) -> Dict[str, Any]:
        """Analisa distribuição da cobertura."""
        files = self.get_file_coverage()
        if not files:
            return {}

        percentages = [pct for _, pct in files]

        return {
            "total_files": len(files),
            "average_coverage": statistics.mean(percentages) if percentages else 0,
            "median_coverage": statistics.median(percentages) if percentages else 0,
            "min_coverage": min(percentages) if percentages else 0,
            "max_coverage": max(percentages) if percentages else 0,
            "files_below_80": len([p for p in percentages if p < 80]),
            "files_above_95": len([p for p in percentages if p >= 95]),
        }

    def print_report(self) -> None:
        """Imprime relatório completo de cobertura."""
        if not self.load_coverage():
            return

        print("📊 Relatório de Cobertura de Testes - OmniMind")
        print("=" * 50)

        # Estatísticas gerais
        stats = self.get_overall_stats()
        print("\n🎯 Estatísticas Gerais:")
        print(f"   Cobertura total: {stats['percent_covered']:.1f}%")
        print(f"   Statements cobertos: {stats['covered_statements']:,}")
        print(f"   Statements faltando: {stats['missing_statements']:,}")
        print(f"   Statements excluídos: {stats['excluded_statements']:,}")

        # Distribuição
        dist = self.analyze_coverage_distribution()
        print("\n📈 Distribuição:")
        print(f"   Cobertura média: {dist['average_coverage']:.1f}%")
        print(f"   Cobertura mediana: {dist['median_coverage']:.1f}%")
        print(f"   Cobertura mínima: {dist['min_coverage']:.1f}%")
        print(f"   Cobertura máxima: {dist['max_coverage']:.1f}%")
        print(f"   Arquivos < 80%: {dist['files_below_80']}")
        print(f"   Arquivos ≥ 95%: {dist['files_above_95']}")

        # Arquivos com menor cobertura
        print("\n📉 Arquivos com Menor Cobertura:")
        files = self.get_file_coverage()[:10]  # Top 10 lowest
        for file_path, pct in files:
            if pct < 90:  # Só mostra se baixa cobertura
                print(f"   {file_path}: {pct:.1f}%")

        # Arquivos com maior cobertura
        print("\n📈 Arquivos com Maior Cobertura:")
        files = self.get_file_coverage()[-10:]  # Top 10 highest
        files.reverse()  # Mais altos primeiro
        for file_path, pct in files:
            if pct >= 95:  # Só mostra se alta cobertura
                print(f"   {file_path}: {pct:.1f}%")

        print("\n💡 Recomendações:")
        if stats["percent_covered"] < 80:
            print("   ⚠️  Cobertura geral baixa - considere adicionar mais testes")
        if dist["files_below_80"] > 0:
            print(f"   📝 {dist['files_below_80']} arquivos precisam de mais testes")
        if stats["percent_covered"] >= 95:
            print("   ✅ Excelente cobertura! Mantenha o padrão.")

        print(f"\n📄 Relatório completo: {self.coverage_file}")


def main() -> int:
    """Função principal."""
    coverage_file = Path("data/test_reports/coverage.json")

    if not coverage_file.exists():
        print(f"❌ Arquivo de cobertura não encontrado: {coverage_file}")
        print("Execute os testes com --cov para gerar o relatório:")
        print("pytest tests/ --cov=src --cov-report=json:data/test_reports/coverage.json")
        return 1

    analyzer = CoverageAnalyzer(coverage_file)
    analyzer.print_report()

    return 0


if __name__ == "__main__":
    sys.exit(main())
