#!/usr/bin/env python3
"""Gera relatórios persistentes de treinamento e validação científica.

Cria relatórios em formato científico para publicação e análise posterior.
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def analyze_training_sessions(sessions_dir: Path) -> Dict[str, Any]:
    """Analisa todas as sessões de treinamento."""
    sessions = []
    for session_file in sessions_dir.glob("training_*.json"):
        try:
            with session_file.open("r", encoding="utf-8") as f:
                sessions.append(json.load(f))
        except Exception:
            continue

    if not sessions:
        return {"error": "Nenhuma sessão encontrada"}

    # Agregar estatísticas
    all_phi_before = []
    all_phi_after = []
    all_phi_deltas = []
    total_cycles = 0
    total_inconsistencies = 0
    total_warnings = 0

    for session in sessions:
        cycles = session.get("cycles", [])
        if not cycles:
            continue

        for cycle in cycles:
            if isinstance(cycle, dict):
                all_phi_before.append(cycle.get("phi_before", 0))
                all_phi_after.append(cycle.get("phi_after", 0))
                all_phi_deltas.append(cycle.get("phi_delta", 0))

        total_cycles += session.get("total_cycles", 0)
        total_inconsistencies += len(session.get("inconsistencies", []))
        total_warnings += session.get("validation_results", {}).get("warnings", 0)

    return {
        "sessions_analyzed": len(sessions),
        "total_cycles": total_cycles,
        "phi_statistics": {
            "before": {
                "mean": float(statistics.mean(all_phi_before)) if all_phi_before else 0.0,
                "stdev": (
                    float(statistics.stdev(all_phi_before)) if len(all_phi_before) > 1 else 0.0
                ),
                "min": float(min(all_phi_before)) if all_phi_before else 0.0,
                "max": float(max(all_phi_before)) if all_phi_before else 0.0,
            },
            "after": {
                "mean": float(statistics.mean(all_phi_after)) if all_phi_after else 0.0,
                "stdev": float(statistics.stdev(all_phi_after)) if len(all_phi_after) > 1 else 0.0,
                "min": float(min(all_phi_after)) if all_phi_after else 0.0,
                "max": float(max(all_phi_after)) if all_phi_after else 0.0,
            },
            "delta": {
                "mean": float(statistics.mean(all_phi_deltas)) if all_phi_deltas else 0.0,
                "stdev": (
                    float(statistics.stdev(all_phi_deltas)) if len(all_phi_deltas) > 1 else 0.0
                ),
            },
        },
        "quality_metrics": {
            "inconsistencies_per_cycle": (
                total_inconsistencies / total_cycles if total_cycles > 0 else 0
            ),
            "warnings_per_cycle": total_warnings / total_cycles if total_cycles > 0 else 0,
        },
    }


def generate_scientific_report(project_root: Path) -> None:
    """Gera relatório científico completo."""
    sessions_dir = project_root / "data" / "sessions"
    reports_dir = project_root / "data" / "validation"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Analisar sessões
    analysis = analyze_training_sessions(sessions_dir)

    # Criar relatório
    report = {
        "report_type": "Scientific Validation Report",
        "timestamp": datetime.now().isoformat(),
        "supervisor": "ScientificSupervisor",
        "analysis": analysis,
        "conclusions": [],
        "recommendations": [],
    }

    # Gerar conclusões
    if analysis.get("sessions_analyzed", 0) > 0:
        phi_mean = analysis["phi_statistics"]["after"]["mean"]
        phi_stdev = analysis["phi_statistics"]["after"]["stdev"]

        if phi_stdev < 0.0001:
            report["conclusions"].append(
                "⚠️ VARIÂNCIA MUITO BAIXA: Possível hardcoding ou cálculo não variável"
            )
        elif phi_mean < 0.3:
            report["conclusions"].append(f"⚠️ Φ MÉDIO ABAIXO DO THRESHOLD: {phi_mean:.4f} < 0.3")
        else:
            report["conclusions"].append(
                f"✅ Φ MÉDIO SAUDÁVEL: {phi_mean:.4f} (stdev: {phi_stdev:.4f})"
            )

        inconsistency_rate = analysis["quality_metrics"]["inconsistencies_per_cycle"]
        if inconsistency_rate > 0.1:
            report["conclusions"].append(
                f"⚠️ TAXA DE INCONSISTÊNCIAS ALTA: {inconsistency_rate:.2%}"
            )
        else:
            report["conclusions"].append(
                f"✅ TAXA DE INCONSISTÊNCIAS ACEITÁVEL: {inconsistency_rate:.2%}"
            )

    # Salvar relatório
    report_file = reports_dir / f"scientific_report_{int(datetime.now().timestamp())}.json"
    with report_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Relatório científico salvo em: {report_file}")
    return report_file


if __name__ == "__main__":
    pass

    project_root = Path(__file__).parent.parent.parent
    generate_scientific_report(project_root)
