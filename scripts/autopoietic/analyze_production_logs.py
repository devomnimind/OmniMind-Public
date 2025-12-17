#!/usr/bin/env python3
"""Script para analisar logs de produção do ciclo autopoiético.

Analisa cycle_history.jsonl e componentes sintetizados para gerar
relatórios de saúde do sistema autopoiético em produção.
"""

from __future__ import annotations

import json
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class CycleStats:
    """Estatísticas agregadas dos ciclos autopoiéticos."""

    total_cycles: int = 0
    successful_syntheses: int = 0
    rejected_before: int = 0
    rolled_back: int = 0
    strategies: Dict[str, int] = None  # type: ignore
    phi_before_avg: float = 0.0
    phi_after_avg: float = 0.0
    phi_delta_avg: float = 0.0
    components_synthesized: int = 0
    unique_components: set[str] = None  # type: ignore

    def __post_init__(self):
        if self.strategies is None:
            object.__setattr__(self, "strategies", defaultdict(int))
        if self.unique_components is None:
            object.__setattr__(self, "unique_components", set())


def load_cycle_history(history_path: Path) -> List[Dict[str, Any]]:
    """Carrega histórico de ciclos do arquivo JSONL."""
    cycles: List[Dict[str, Any]] = []
    if not history_path.exists():
        logger.warning("Histórico não encontrado: %s", history_path)
        return cycles

    try:
        with history_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cycles.append(json.loads(line))
    except Exception as e:
        logger.error("Erro ao ler histórico: %s", e)
        return cycles

    return cycles


def analyze_cycles(cycles: List[Dict[str, Any]]) -> CycleStats:
    """Analisa ciclos e gera estatísticas."""
    stats = CycleStats()
    stats.total_cycles = len(cycles)

    phi_before_values = []
    phi_after_values = []
    phi_deltas = []

    for cycle in cycles:
        strategy = cycle.get("strategy", "UNKNOWN")
        stats.strategies[strategy] += 1

        synthesized = cycle.get("synthesized_components", [])
        stats.components_synthesized += len(synthesized)
        stats.unique_components.update(synthesized)

        phi_before = cycle.get("phi_before")
        phi_after = cycle.get("phi_after")

        if phi_before is not None:
            phi_before_values.append(phi_before)
        if phi_after is not None:
            phi_after_values.append(phi_after)
        if phi_before is not None and phi_after is not None:
            delta = phi_after - phi_before
            phi_deltas.append(delta)

        # Classificar ciclo
        if len(synthesized) > 0:
            # Verificar se foi rollback (phi_after < threshold mas tinha componentes)
            if phi_after is not None and phi_after < 0.3:
                stats.rolled_back += 1
            else:
                stats.successful_syntheses += 1
        else:
            # Pode ser rejeição antes ou ciclo sem evolução
            if phi_before is not None and phi_before < 0.3:
                stats.rejected_before += 1

    # Calcular médias
    if phi_before_values:
        stats.phi_before_avg = statistics.mean(phi_before_values)
    if phi_after_values:
        stats.phi_after_avg = statistics.mean(phi_after_values)
    if phi_deltas:
        stats.phi_delta_avg = statistics.mean(phi_deltas)

    return stats


def list_synthesized_components(code_dir: Path) -> List[Dict[str, Any]]:
    """Lista componentes sintetizados com informações."""
    components: List[Dict[str, Any]] = []
    if not code_dir.exists():
        return components

    for py_file in code_dir.glob("*.py"):
        try:
            stat = py_file.stat()
            with py_file.open("r", encoding="utf-8") as f:
                first_lines = "".join(f.readlines()[:5])
                has_class = "class " in first_lines

            components.append(
                {
                    "name": py_file.stem,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "has_class": has_class,
                }
            )
        except Exception as e:
            logger.warning("Erro ao ler componente %s: %s", py_file, e)

    return sorted(components, key=lambda x: x["modified"], reverse=True)


def generate_report(stats: CycleStats, components: List[Dict[str, Any]], output_path: Path) -> None:
    """Gera relatório em formato legível."""
    report_lines = [
        "=" * 70,
        "RELATÓRIO DE ANÁLISE - CICLO AUTOPOIÉTICO (PHASE 22)",
        "=" * 70,
        "",
        f"📊 ESTATÍSTICAS GERAIS",
        f"   Total de ciclos: {stats.total_cycles}",
        f"   Sínteses bem-sucedidas: {stats.successful_syntheses}",
        f"   Rejeitadas antes (Φ baixo): {stats.rejected_before}",
        f"   Rollbacks (Φ colapsou): {stats.rolled_back}",
        "",
        f"📈 MÉTRICAS DE Φ (PHI)",
        f"   Φ médio antes: {stats.phi_before_avg:.4f}",
        f"   Φ médio depois: {stats.phi_after_avg:.4f}",
        f"   Delta médio (ΔΦ): {stats.phi_delta_avg:+.4f}",
        "",
        f"🔧 ESTRATÉGIAS UTILIZADAS",
    ]

    for strategy, count in sorted(stats.strategies.items(), key=lambda x: -x[1]):
        percentage = (count / stats.total_cycles * 100) if stats.total_cycles > 0 else 0
        report_lines.append(f"   {strategy}: {count} ({percentage:.1f}%)")

    report_lines.extend(
        [
            "",
            f"🧬 COMPONENTES SINTETIZADOS",
            f"   Total sintetizado: {stats.components_synthesized}",
            f"   Componentes únicos: {len(stats.unique_components)}",
            "",
            f"📁 COMPONENTES PERSISTIDOS ({len(components)} arquivos)",
        ]
    )

    for comp in components[:10]:  # Top 10 mais recentes
        report_lines.append(
            f"   • {comp['name']}: {comp['size_bytes']} bytes "
            f"(modificado: {comp['modified'][:19]})"
        )

    if len(components) > 10:
        report_lines.append(f"   ... e mais {len(components) - 10} componentes")

    report_lines.extend(
        [
            "",
            "=" * 70,
            f"Relatório gerado em: {datetime.now().isoformat()}",
            "=" * 70,
        ]
    )

    report_text = "\n".join(report_lines)
    print(report_text)

    # Salvar em arquivo
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(report_text)
        logger.info("Relatório salvo em: %s", output_path)


def main():
    """Função principal."""
    project_root = Path(__file__).parent.parent.parent
    history_path = project_root / "data" / "autopoietic" / "cycle_history.jsonl"
    code_dir = project_root / "data" / "autopoietic" / "synthesized_code"
    output_path = project_root / "data" / "autopoietic" / "production_report.txt"

    logger.info("Analisando logs de produção...")
    logger.info("Histórico: %s", history_path)
    logger.info("Componentes: %s", code_dir)

    cycles = load_cycle_history(history_path)
    if not cycles:
        logger.warning("Nenhum ciclo encontrado. Sistema pode não ter rodado ainda.")
        return

    stats = analyze_cycles(cycles)
    components = list_synthesized_components(code_dir)

    generate_report(stats, components, output_path)


if __name__ == "__main__":
    main()
